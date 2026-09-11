"""Explicit adapters connecting education to research and truth boundaries."""
from __future__ import annotations

from typing import Callable, Protocol, Sequence

from ..research.contracts import ResearchCandidate, ResearchDocument
from ..security.truth import ClaimAssessment
from .contracts import Lesson, Skill, SkillLevel
from .providers import EducationProvider


class ResearchEvidenceProvider(Protocol):
    """Host-controlled research source used only to supply evidence."""

    def discover(self, query: str) -> Sequence[ResearchCandidate]: ...
    def ingest(self, candidate: ResearchCandidate) -> ResearchDocument: ...


class TruthVerifier(Protocol):
    """Host-controlled truth boundary for educational claims."""

    def assess(self, claim: str, evidence_urls: Sequence[str], source_confidences: Sequence[float], contradictory: bool = False) -> ClaimAssessment: ...


LessonFactory = Callable[[ResearchDocument, SkillLevel, Sequence[str]], Lesson | None]


class ResearchBackedEducationProvider:
    """Turns verified research documents into education-provider lessons.

    Research supplies evidence only; it never grants publishing, payment, or
    execution authority. The caller supplies the lesson factory so model or
    domain-specific generation remains replaceable.
    """

    def __init__(
        self,
        research: ResearchEvidenceProvider,
        skills_provider: EducationProvider,
        lesson_factory: LessonFactory,
    ) -> None:
        if not hasattr(research, "discover") or not hasattr(research, "ingest"):
            raise TypeError("research provider is invalid")
        if not hasattr(skills_provider, "skills"):
            raise TypeError("skills provider is invalid")
        if not callable(lesson_factory):
            raise TypeError("lesson_factory must be callable")
        self.research = research
        self.skills_provider = skills_provider
        self.lesson_factory = lesson_factory

    def skills(self, domain: str) -> Sequence[Skill]:
        return self.skills_provider.skills(domain)

    def lessons(self, domain: str, level: SkillLevel, goals: Sequence[str]) -> Sequence[Lesson]:
        candidates = self.research.discover(domain)
        lessons: list[Lesson] = []
        for candidate in candidates:
            document = self.research.ingest(candidate)
            lesson = self.lesson_factory(document, level, goals)
            if lesson is not None:
                lessons.append(lesson)
        return tuple(lessons)


class TruthCheckedEducationProvider:
    """Filters education content through the existing conservative truth engine."""

    def __init__(self, provider: EducationProvider, truth: TruthVerifier) -> None:
        if not hasattr(provider, "skills") or not hasattr(provider, "lessons"):
            raise TypeError("education provider is invalid")
        if not hasattr(truth, "assess"):
            raise TypeError("truth verifier is invalid")
        self.provider = provider
        self.truth = truth

    def skills(self, domain: str) -> Sequence[Skill]:
        return self.provider.skills(domain)

    def lessons(self, domain: str, level: SkillLevel, goals: Sequence[str]) -> Sequence[Lesson]:
        accepted: list[Lesson] = []
        for lesson in self.provider.lessons(domain, level, goals):
            if not lesson.evidence_urls:
                continue
            assessment = self.truth.assess(
                f"{lesson.title}\n{lesson.content}",
                lesson.evidence_urls,
                (float(lesson.metadata.get("confidence", 0.0)),),
                False,
            )
            if not assessment.verified or assessment.confidence < 0.60:
                continue
            metadata = dict(lesson.metadata)
            metadata["truth_confidence"] = assessment.confidence
            accepted.append(
                Lesson(
                    lesson.lesson_id,
                    lesson.title,
                    lesson.domain,
                    lesson.skill_ids,
                    lesson.content,
                    lesson.evidence_urls,
                    lesson.level,
                    metadata,
                )
            )
        return tuple(accepted)
