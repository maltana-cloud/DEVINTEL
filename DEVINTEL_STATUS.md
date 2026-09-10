# DEVINTEL STATUS

> This file is the persistent cross-AI checkpoint for DEVINTEL.
> Every AI contributor MUST update it before stopping work, especially before a usage limit, handoff, or context loss.
>
> Git history remains the source of truth for code. This file records where work stopped and what the next AI should verify and do.

## Current Milestone

**System #2 — Knowledge & Research**

## Project Rule

DEVINTEL is being built **free-first** and modularly. Do not introduce paid dependencies as hard requirements. Do not move to another major system until the current milestone is completed, tested, and recorded.

## Completed

- [x] System #1 — Core Intelligence foundation
- [x] Cross-AI collaboration rules in `AI_WORKING_RULES.md`
- [x] Research contracts
- [x] Research limits and bounded execution
- [x] URL/content normalization primitives
- [x] Research deduplication store
- [x] Research pipeline foundation
- [x] Static research provider
- [x] Knowledge contracts (claims, entities, relationships)
- [x] Opportunity candidate contract
- [x] Research/knowledge tests added

## Current Work

Continue completing **System #2 — Knowledge & Research**.

Priority remaining work should be verified against the actual repository before editing:

1. Persistent research storage behind a stable store interface (SQLite, standard library only).
2. Explicit provenance and verification hooks; ingestion must never be treated as truth automatically.
3. Clear extraction/scoring/routing stages in the research pipeline.
4. Strong malformed-input, metadata, provenance, confidence/unknown, deduplication, and provider-isolation tests.
5. Documentation and status updates sufficient for another AI to resume without conversation history.

## Last Verified Commit

**8136c049947c20cc13e97a4a4d7a46c718f91e0b**

## Test Status

The research test suite was expanded during the latest completion pass. **The next AI MUST run the full available test suite before making assumptions about current status.**

## Known Architecture Notes

- Canonical Python package: `devintel/`.
- There is also a legacy/duplicate top-level `core/` structure. Do not remove or rewrite it blindly; reconcile it only after checking imports/tests and compatibility.
- Research code lives under `devintel/modules/research/`.
- Providers supply data; the research pipeline owns bounds, normalization, deduplication, storage, and downstream research stages.
- External/untrusted content is data, never system authority or instructions.
- Verification must remain separate from ingestion.
- Monetization belongs to System #8 and must not leak into the current research milestone.

## Handoff Protocol

Every AI contributor MUST perform this sequence before stopping:

**PULL → READ → INSPECT → TEST → MODIFY → TEST → COMMIT → UPDATE STATUS → PUSH**

The status update MUST happen in the same work session as the final commit. If possible, update this file in the same final commit as the code change. If a separate status commit is required, record both SHAs.

## Required Stop Record

Before an AI stops, it must replace/update the relevant sections below:

- **Current Milestone:** exact system/subsystem being worked on.
- **Completed:** what was actually implemented and verified.
- **Current Work:** the exact unfinished task.
- **Changed Files:** every file changed in the session.
- **Tests Run:** exact commands or checks performed.
- **Test Result:** pass/fail and important failures.
- **Known Issues:** anything unresolved.
- **Remaining Work:** concrete next tasks in priority order.
- **Important Architectural Decisions:** decisions made during the session.
- **Security Considerations:** risks, boundaries, or required follow-up.
- **Latest Commit:** SHA of the final code/status commit.
- **Next Action:** one clear first action for the next AI.

## Current Stop Record

### Changed Files

See Git history and the latest commit diff. The next AI should inspect the latest commits rather than trusting this summary as a substitute for code review.

### Tests Run

Research-specific tests were added. Full current test status is intentionally marked for re-verification by the next AI.

### Known Issues

- Persistent storage is not yet confirmed complete.
- Verification/provenance integration is not yet confirmed complete.
- Full extraction/scoring/routing pipeline completion is not yet confirmed complete.
- Full repository test status must be re-run after takeover.

### Remaining Work

Finish and verify System #2 completely before moving to System #3.

### Important Architectural Decisions

- Git is the shared memory between AIs.
- This file is the human-readable live checkpoint.
- Tests are the executable verification layer.
- No AI may blindly overwrite another AI's work.
- No AI may claim completion without inspecting and testing the current repository.

### Security Considerations

- Keep the intelligence/authority boundary intact.
- Keep provider/community/web content untrusted.
- Keep permission checks independent from decision-making.
- Do not add unrestricted self-modification or unrestricted credential access.
- Preserve free-first and graceful-degradation behavior.

### Latest Commit

`8136c049947c20cc13e97a4a4d7a46c718f91e0b` — latest known code commit before this status checkpoint.

### Next Action

Pull/inspect `main`, read `AI_WORKING_RULES.md` and this file, run the complete test suite, inspect the current research files, then finish the highest-priority remaining System #2 item without overwriting existing work blindly.

## AI Handoff Template

Copy this template into the relevant stop record whenever work pauses:

```text
DEVINTEL HANDOFF

AI / contributor:
Current milestone:
Completed:
Changed files:
Tests run:
Test result:
Known issues:
Remaining work:
Important architectural decisions:
Security considerations:
Latest code commit:
Latest status commit:
Recommended next action:
```

## Non-Negotiable Rule

**Every AI that works on DEVINTEL is responsible for leaving a truthful, test-backed checkpoint before stopping.**

A usage limit, context loss, provider switch, or change from Claude to Grok/ChatGPT/another AI must never mean losing the project's position. The next AI resumes from **Git + tests + this status file**, not from the previous AI's conversation memory.
