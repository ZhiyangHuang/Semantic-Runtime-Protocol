# SRP Decision Layer 03: DeBERTa Baseline

This branch is the first model implementation branch.
It trains a small encoder classifier as a local SRP transition validator while preserving deterministic governance authority.

## Goal

Train a DeBERTa-v3 classifier for:

```text
S_t + Delta + Evidence + Governance Context -> ACCEPT / REJECT / REVIEW
```

The classifier output is decision evidence.
It must not execute mutations or bypass SRP Governance.

## Recommended Model

Start with:

- `microsoft/deberta-v3-xsmall` for quick smoke tests.
- `microsoft/deberta-v3-small` for the first serious baseline.

This is easier and lower-risk than starting with Qwen Decision Head because the task is classification-first.

## Input Template

Use a stable text schema rather than raw JSON:

```text
[STATE]
contract.requires_evidence = true
policy.source = trusted
authority.source = governance

[OBSERVATION]
...

[EVIDENCE]
...

[CANDIDATE TRANSITION]
state.value: A -> B

[GOVERNANCE CONTEXT]
...
```

## Outputs

The model returns raw logits for:

- `ACCEPT`
- `REJECT`
- `REVIEW`

Softmax probabilities are model confidence, not governance authority.

## Recommended Locations

- `experiments/decision_layer/deberta/`
- `experiments/decision_layer/deberta/dataset.py`
- `experiments/decision_layer/deberta/train.py`
- `experiments/decision_layer/deberta/evaluate.py`
- `experiments/decision_layer/deberta/metrics.py`
- `experiments/decision_layer/deberta/tests/`

## Metrics

Report classification and probability quality:

- accuracy
- macro-F1
- confusion matrix
- negative log likelihood
- Brier score
- expected calibration error
- invalid-accept rate after governance replay

## Governance Integration

Deployment must keep this shape:

```text
DeBERTa probability -> Evidence -> SRP Governance -> approve / reject / review
```

Never:

```text
DeBERTa ACCEPT -> mutation
```

## Implementation Steps

1. Add the text serializer for SRP decision examples.
2. Add dataset loading from the schema branch output format.
3. Add a minimal training script using Hugging Face `Trainer`.
4. Add evaluation metrics, including calibration-aware metrics.
5. Add a governance replay check showing that the classifier cannot override deterministic rejection.
6. Add CPU-only smoke tests using a tiny fixture model or mocked logits.

## Hardware Assumption

The first serious run should target an RTX 3060 Ti 8GB environment.
Use short sequence lengths and small batches first:

```text
max_length: 512
batch_size: 8-16
epochs: 3-5
learning_rate: 2e-5
weight_decay: 0.01
```

## Success Criteria

- Training can run from a documented dataset path.
- Evaluation produces both classification and calibration metrics.
- Governance replay confirms model evidence cannot mutate state by itself.
- The result is strong enough to compare against rules-only and later Qwen/Jev-style baselines.

## Research Boundary

This branch tests whether a small local classifier can predict SRP admissibility signals.
It does not claim that learned probabilities are calibrated until the calibration branch verifies them.
