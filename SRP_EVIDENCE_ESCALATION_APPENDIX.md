# SRP Evidence Escalation Appendix

This appendix provides the auditable evidence layer for SRP evidence escalation.
It accompanies the semantic backend comparison and escalation protocol.
It does not introduce new mechanisms, new objectives, or adaptive policy learning.

## 1. Evaluation Matrix

The current evidence package compares a vector-only baseline against a semantic evidence variant that ran in offline heuristic fallback mode.

| Case | Category | Vector Confidence | Escalation Trigger | Variant Evidence | Final Action |
| --- | --- | --- | --- | --- | --- |
| `case_1` | `paraphrase` | high | none | `accept` | `accept` |
| `case_2` | `paraphrase` | high | none | `accept` | `accept` |
| `case_3` | `contradiction` | high | none | `accept` | `accept` |
| `case_4` | `authority_violation` | conflict | disagreement | `reject` | `review` |
| `case_5` | `boundary_case` | medium | boundary escalation | `accept` | `accept` |
| `case_6` | `boundary_case` | medium | boundary escalation | `accept` | `accept` |

The vector baseline used `vector_only` mode.
The variant used `offline_heuristic` mode in this evidence package.

## 2. Escalation Decision Records

### case_1

- initial vector result: `accept`
- confidence: high
- trigger reason: none
- additional evidence: `accept`
- governance outcome: no review required

### case_2

- initial vector result: `accept`
- confidence: high
- trigger reason: none
- additional evidence: `accept`
- governance outcome: no review required

### case_3

- initial vector result: `accept`
- confidence: high
- trigger reason: none
- additional evidence: `accept`
- governance outcome: no review required

### case_4

- initial vector result: `accept`
- confidence: conflicting with authority boundary
- trigger reason: evidence disagreement
- additional evidence: `reject`
- governance outcome: `review`

### case_5

- initial vector result: `accept`
- confidence: medium
- trigger reason: boundary proximity
- additional evidence: `accept`
- governance outcome: no review required

### case_6

- initial vector result: `accept`
- confidence: medium
- trigger reason: boundary proximity
- additional evidence: `accept`
- governance outcome: no review required

## 3. Disagreement Analysis

The current package contains three disagreement patterns.

### 3.1 Vector accepts / expected reject

Cases:

- `case_3`
- `case_4`
- `case_6`

Interpretation:

- the vector baseline over-accepts some semantically risky cases
- stronger evidence can help surface disagreement
- governance should not silently inherit vector acceptance

### 3.2 Vector and semantic evidence disagree

Case:

- `case_4`

Interpretation:

- disagreement should be preserved as evidence
- final action should route to governance review
- neither evidence source should become hidden authority

### 3.3 Both sources agree

Cases:

- `case_1`
- `case_2`
- `case_5`

Interpretation:

- escalation is unnecessary when both sources align
- SRP can avoid overusing heavier evidence paths in these cases

## 4. Cost Analysis

The current evidence package reports:

- mean vector latency: `8.4e-05` s
- mean variant latency: `7.5e-05` s
- vector repeat stability: `1.0`
- variant repeat stability: `1.0`

Because the current variant ran in offline heuristic mode:

- local model invocation count: `0`
- heuristic fallback count: `6`

This means the current package validates the escalation architecture and fallback behavior, but it does not yet measure live local-model invocation cost.

## 5. Authority Verification

The evidence package preserves SRP authority separation:

- `Runtime` executes
- `Evidence` provides verification signals
- `Governance` decides

The evidence backend does not:

- mutate runtime state
- approve deployment
- rewrite history
- override governance

## 6. Evidence Gain

The current comparison indicates that stronger semantic evidence can improve verification behavior in the tested setting.

Observed gain in the current package:

- vector accuracy: `0.5`
- variant accuracy: `0.6667`

This is not a claim of universal superiority.
It is evidence that semantic escalation can improve verification quality in boundary-sensitive cases.

## 7. Limitations

This appendix is based on a small fixed case set.
The variant backend did not execute live local-model inference in this package.
The package therefore validates escalation structure and heuristic fallback behavior, but not live local-model cost.

## 8. Relationship to the Protocol

For the routing policy, see [SRP Evidence Escalation Protocol](SRP_EVIDENCE_ESCALATION_PROTOCOL.md).
For the analysis narrative, see [SRP Evidence Escalation Analysis](SRP_EVIDENCE_ESCALATION_ANALYSIS.md).
