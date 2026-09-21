# SRP Decision Layer 05: Qwen Head and Jev-Style Benchmark

This is the hardest branch in the decision-layer sequence.
It compares SRP-native learned decision heads against Jev-style typed decision models while keeping SRP Governance as the only authority.

## Goal

Evaluate whether stronger decision intelligence improves the evidence supplied to SRP Governance:

```text
LLM / Qwen head / Jev-style decision model -> decision signal -> evidence -> governance -> execution
```

The research question is:

```text
Can calibrated probabilistic decision-making improve semantic-state transition governance without becoming the authority that governs mutation?
```

## Compared Systems

- `rules_only`: deterministic SRP governance without learned decision evidence.
- `deberta`: local encoder classifier from the earlier branch.
- `qwen_head`: Qwen sequence classification or LoRA decision head.
- `jev_api`: external Jev-style API if available.
- `open_jev_style`: local open implementation such as decider/open-jev-style model if it is stable enough.
- `structured_llm`: ordinary structured-output LLM baseline.

## Qwen Decision Head

The Qwen branch should avoid free-form generation for the decision itself.

Preferred shape:

```text
Qwen base -> pooled/last hidden representation -> decision head -> ACCEPT / REJECT / REVIEW logits
```

On an RTX 3060 Ti 8GB target, start with:

- small Qwen family model where feasible,
- frozen base model,
- LoRA adapters,
- trainable classification head.

## Jev-Style Integration

Jev or Jev-style models should answer typed questions:

- Choice: `ACCEPT / REJECT / REVIEW`
- Score: evidence strength
- Noul-style boolean: contract consistency, authority sufficiency, review requirement

The returned probability is recorded as decision evidence.
It cannot directly approve mutation.

## Benchmark Matrix

Use the same SRP transition dataset and replay cases for every model:

| System | Decision Source | Local | Calibration | Governance |
| --- | --- | --- | --- | --- |
| rules_only | deterministic rules | yes | n/a | rules |
| deberta | encoder classifier | yes | required | rules |
| qwen_head | sequence classifier / LoRA head | yes | required | rules |
| structured_llm | JSON structured output | optional | weak/required | rules |
| open_jev_style | typed local decision model | yes | required | rules |
| jev_api | typed external decision model | no | evaluate | rules |

## Metrics

Primary:

- invalid acceptance rate
- false rejection rate
- review routing rate
- authority violation rate
- calibration error
- Brier score
- negative log likelihood

Operational:

- latency
- VRAM or memory footprint
- cost per 1,000 transitions
- dependency risk
- API/version drift risk

## Recommended Locations

- `experiments/decision_layer/qwen_head/`
- `experiments/decision_layer/jev_style/`
- `experiments/decision_layer/benchmark/`
- `experiments/decision_layer/benchmark/matrix.py`
- `experiments/decision_layer/benchmark/report.py`

## Implementation Steps

1. Define a common decision-model interface.
2. Add a structured-output LLM baseline as a weak comparison.
3. Add Qwen-head training or inference wrapper.
4. Add Jev-style typed decision adapter behind an optional dependency boundary.
5. Run every model through the same governance replay harness.
6. Report quality, calibration, latency, cost, and dependency tradeoffs.

## Success Criteria

- All decision sources emit the same normalized decision record.
- SRP Governance receives decision signals but remains the only authority.
- The benchmark can run without Jev access by skipping external API cases.
- The report distinguishes local SRP-native models from external vendor baselines.

## Research Boundary

Do not rename SRP as a Jev-based system.
Jev-style models are baselines or optional decision-evidence components.

The strongest acceptable conclusion is:

```text
Calibrated decision intelligence can improve evidence quality for SRP Governance, but does not replace the governance boundary.
```
