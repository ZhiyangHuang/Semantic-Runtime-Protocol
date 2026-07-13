# SRP Version Conflict Validation

This document records the validation boundary for version-history conflict evidence.
It confirms that SRP distinguishes ordinary branching from explicit conflict evidence.

The central question is:

> When does a version history disagreement become conflict evidence instead of just a valid branch?

The answer is: only when the detector sees explicit conflict evidence.

---

## Validation Matrix

| Invariant | Test | Current Status |
| --- | --- | --- |
| Branch is not conflict | `test_version_conflict.py` | pass |
| Duplicate transition produces conflict | `test_version_conflict.py` | pass |
| Divergent semantic update produces conflict | `test_version_conflict.py` | pass |
| Checkpoint does not resolve conflict | `test_version_conflict.py` | pass |
| Conflict detection is deterministic | `test_version_conflict.py` | pass |

---

## Observed Properties

- a parent can have multiple children without being a conflict
- duplicate transition evidence is reported as a conflict
- semantic divergence is only reported when it carries explicit conflict evidence
- checkpoint creation does not mutate the version graph or clear conflict evidence
- repeated detection over the same graph is stable

---

## Residual Risks

- conflict resolution remains intentionally out of scope
- deeper semantic divergence heuristics are still evidence-only
- checkpoint selection does not perform automatic branch arbitration

