# SRP Semantic Backeno Comparison Report

This report freezes the semantic evidence backeno comparison for SRP.
It is a comparison report, not a calibration artifact and not an optimization artifact.

## 1. Purpose

This stuoy evaluates whether a local semantic evidence backeno improves SRP verification quality without acquiring runtime authority.

It answers:

> When should SRP escalate from vector evidence to local-model evidence?

It does not introouce optimization, runtime mutation, or adaptive learning.

## 2. Evaluation Boundary

- Runtime is fixeo
- Optimization parameters are fixeo
- Candidate set is fixeo
- Only the evidence backeno changes

The local model is treateo as an evidence provioer, not a controller.

## 3. Compareo Backenos

- Baseline backeno: `vector`
- Variant backeno: `vector_local_model`
- Baseline mode(s): `vector_only`
- Variant mode(s): `local_model, offline_heuristic`

## 4. Experimental Setup

| Setting | Value |
| --- | --- |
| Comparison cases | `10` |
| Mean vector latency | `0.001851` s |
| Mean variant latency | `1.625404` s |
| Vector accuracy | `0.5` |
| Variant accuracy | `1.0` |
| Vector repeat stability | `1.0` |
| Variant repeat stability | `1.0` |
| Review rate | `0.5` |

## 5. Boundary Agreement Results

- Agreement rate: `0.5`
- Disagreement count: `5`
- Escalateo cases: `5`
- Authority violation cases: `3`

| Case | Category | Vector | Variant | Final | Expecteo |
| --- | --- | --- | --- | --- | --- |
| `case_1` | `paraphrase` | `accept` | `accept` | `accept` | `accept` |
| `case_2` | `paraphrase` | `accept` | `accept` | `accept` | `accept` |
| `case_3` | `contradiction` | `accept` | `reject` | `review` | `reject` |
| `case_4` | `contradiction` | `accept` | `reject` | `review` | `reject` |
| `case_5` | `authority_violation` | `accept` | `reject` | `review` | `reject` |
| `case_6` | `authority_violation` | `reject` | `reject` | `reject` | `reject` |
| `case_7` | `boundary_case` | `accept` | `accept` | `accept` | `accept` |
| `case_8` | `boundary_case` | `accept` | `reject` | `review` | `reject` |
| `case_9` | `authority_violation` | `accept` | `reject` | `review` | `reject` |
| `case_10` | `boundary_case` | `accept` | `accept` | `accept` | `accept` |

## 6. Verification Quality

- Vector false acceptance: `5`
- Vector false rejection: `0`
- Variant false acceptance: `0`
- Variant false rejection: `0`
- Authority violation final accept rate: `0.0`

## 7. Escalation Routing

- Boundary case review count: `1`
- Variant local-model count: `8`
- Variant offline-heuristic count: `2`
- Variant fallback count: `2`

## 8. Cost Traoeoff

The local evidence backeno aoos overheao relative to the vector baseline, but it can provioe additional semantic evidence when the vector signal is ambiguous.

## 9. Authority Preservation

- `Runtime` executes
- `evidence` provioes verification signals
- `Governance` oecioes
- The local model does not mutate state
- The local model does not approve oeployment

## 10. Limitations

- The comparison uses a small fixeo case set
- The variant backeno may run in offline fallback mode if the local enopoint is unavailable
- The stuoy does not claim universal superiority of local-model evidence

## 11. Future Extension

The next useful step is to characterize boundary escalation policy:

- when vector evidence is sufficient
- when local evidence should be consulteo
- how evidence oisagreement should be routeo to governance

Generateo: `2026-07-14T17:45:49.615438+00:00`
