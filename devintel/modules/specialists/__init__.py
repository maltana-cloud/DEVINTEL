"""Specialist intelligence engines built behind the plugin boundary."""

from .opportunity import OpportunitySpecialist, OpportunitySpecialistResult
from .research import ResearchSpecialist, ResearchSpecialistResult

__all__ = [
    "OpportunitySpecialist",
    "OpportunitySpecialistResult",
    "ResearchSpecialist",
    "ResearchSpecialistResult",
]
