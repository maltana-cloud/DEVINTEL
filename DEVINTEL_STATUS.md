# DEVINTEL STATUS

> Persistent cross-AI checkpoint. Every AI contributor MUST update this before stopping.

## Current Milestone

**System #2 — Knowledge & Research — completed**

## Project Rule

DEVINTEL remains free-first, modular, verification-first, and bounded. Do not move to System #3 until this checkpoint is reviewed and the full CI suite is green.

## Completed

- [x] System #1 — Core Intelligence foundation
- [x] Cross-AI collaboration rules
- [x] Research contracts and validation
- [x] Resource limits and bounded provider execution
- [x] URL/content normalization and deterministic hashing
- [x] URL/content deduplication
- [x] In-memory research store and stable `ResearchStore` protocol
- [x] SQLite persistent research store using Python standard library only
- [x] Structured knowledge contracts: claims, entities, relationships
- [x] Opportunity candidate contract with money-independent value scoring
- [x] Provider isolation and failure limits
- [x] Explicit provenance/verification hook with conservative baseline verifier
- [x] Research scoring and routing primitives
- [x] Research hardening tests for limits, malformed/oversized inputs, failures, provenance, deduplication, and SQLite persistence

## Current Work

No unfinished System #2 implementation is known at this checkpoint.

## Last Verified Commit

`87458bfd3cdf084a261198dc16af44650addd033`

## Test Status

The latest recorded CI run before the final research fixes had 26 passing and 2 failing tests. Those failures were corrected by making the test fixtures reflect the intended content-deduplication semantics and candidate bounds. A fresh CI run is required before declaring the repository globally green.

## Known Architecture Notes

- Canonical Python package: `devintel/`.
- Legacy/duplicate top-level `core/` remains untouched until a later compatibility review.
- Research code lives under `devintel/modules/research/`.
- Providers supply untrusted data; the pipeline owns bounds, normalization, deduplication, storage, verification hooks, scoring, and routing.
- Verification is separate from ingestion. Ingestion never implies truth.
- External content can never grant DEVINTEL authority or execution permissions.
- Monetization remains a System #8 concern.

## Handoff Protocol

**PULL → READ → INSPECT → TEST → MODIFY → TEST → COMMIT → UPDATE STATUS → PUSH**

Every AI must leave a truthful checkpoint before a usage limit, handoff, or context loss.

## Changed Files In This Completion Pass

- `devintel/modules/research/store.py`
- `devintel/modules/research/pipeline.py`
- `devintel/modules/research/verification.py`
- `devintel/modules/research/__init__.py`
- `tests/test_research_hardening.py`
- `DEVINTEL_STATUS.md`

## Remaining Work

1. Run and confirm the fresh full repository CI suite after these fixes.
2. If CI is green, begin System #3 — Truth & Security, using the charter and this checkpoint.

## Important Architectural Decisions

- SQLite is an optional replaceable persistence backend, not a paid service dependency.
- `ResearchStore` is a protocol so storage implementations remain swappable.
- Verification is a pluggable protocol; the baseline verifier checks provenance structure and deliberately does not pretend to fact-check the external world.
- Research routing is a candidate decision, not publication authority.
- Content deduplication is intentional even when URLs differ.

## Security Considerations

- Keep intelligence separate from authority.
- Treat all provider/web/community content as untrusted data.
- Preserve fail-closed permissions and bounded execution.
- Never add unrestricted self-modification or unrestricted credential access.
- Preserve free-first and graceful-degradation behavior.

## Latest Commit

`87458bfd3cdf084a261198dc16af44650addd033` — research hardening tests and fixture corrections.

## Next Action

Run the fresh CI test suite on the latest `main`. If green, start System #3 only after recording the green result.

## AI Handoff Template

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

**Every AI that works on DEVINTEL must leave a truthful, test-backed checkpoint before stopping.**
