# SRP Decision Layer 04: Distillation and Calibration

This branch adds the higher-value training loop after the basic DeBERTa baseline exists.
It uses teacher decisions to accelerate student training, then calibrates student probabilities before governance use.

## Goal

Build a selective distillation pipeline:

```text
SRP rules + strong teacher -> soft labels -> student model -> calibration -> governance evidence
```

Teacher and student outputs are evidence-producing components only.
They do not become authority.

## Teacher Role

The teacher may be:

- local Qwen
- remote GPT/Claude-style model
- Jev if access is available
- ensemble of the above

The teacher provides:

- soft class probabilities
- uncertainty
- rationale for audit and disagreement review

The teacher does not provide ground truth.

## Ground Truth Rule

Hard labels must come from:

1. SRP deterministic governance,
2. validated replay traces,
3. human review for ambiguous or contradictory cases.

Teacher output is auxiliary supervision.

## Distillation Record

```json
{
  "example_id": "srp_transition_000001",
  "hard_label": "ACCEPT",
  "teacher_probability": {
    "ACCEPT": 0.82,
    "REJECT": 0.02,
    "REVIEW": 0.16
  },
  "teacher_confidence": 0.82,
  "teacher_reason": "Evidence supports the transition, but authority wording is partially ambiguous.",
  "disagreement": false,
  "review_required": false
}
```

## Selective Distillation

Keep easy high-confidence teacher cases for automatic soft-label training.
Route low-confidence or rule-disagreeing cases to review.

Suggested routing:

- keep: top probability >= 0.85 and no rule disagreement
- review: top probability < 0.70
- inspect: teacher label disagrees with SRP hard label

## Loss Shape

Train the student with a mixed objective:

```text
L = alpha * CE(student_logits, hard_label)
  + beta  * KL(student_distribution_T, teacher_distribution_T)
```

Distillation temperature is not the same as deployment calibration temperature.

## Calibration

After training, calibrate on a held-out validation split:

- temperature scaling first
- optionally isotonic regression later

Report:

- expected calibration error
- Brier score
- negative log likelihood
- reliability diagram data
- pre/post calibration comparison

## Recommended Locations

- `experiments/decision_layer/distillation/`
- `experiments/decision_layer/distillation/teacher_records.py`
- `experiments/decision_layer/distillation/selective_filter.py`
- `experiments/decision_layer/distillation/train_student.py`
- `experiments/decision_layer/calibration/`
- `experiments/decision_layer/calibration/temperature.py`
- `experiments/decision_layer/calibration/report.py`

## Implementation Steps

1. Add the teacher annotation record format.
2. Add selective filtering for keep/review/disagreement cases.
3. Add a mixed hard-label and soft-label student loss.
4. Add temperature scaling on validation logits.
5. Add metrics and artifacts comparing raw and calibrated probabilities.
6. Add a governance replay test using calibrated probabilities as evidence only.

## Success Criteria

- Distillation can run without changing deterministic labels.
- Disagreements are preserved as review artifacts.
- Calibration improves or transparently reports probability quality.
- Governance replay confirms that calibrated probability still cannot authorize mutation alone.

## Research Boundary

This branch supports the claim:

```text
Use distillation to compress semantic decision intelligence while keeping state-transition authority outside the learned model.
```

It must not claim that a teacher or student model replaces SRP Governance.
