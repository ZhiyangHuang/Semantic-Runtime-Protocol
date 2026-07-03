# Evaluation Layer Management

This note freezes the evaluation-layer structure for the current semester experiment system.

## Goal

The repository should clearly separate:

- paper primary metrics
- supporting comparison metrics
- SRP protocol validation metrics
- diagnostic-only metrics and fallbacks

so that the paper does not drift into metric sprawl.

## Canonical Evaluation Files

The main evaluation stack is defined by:

- `srp_experiment/run_experiment.py`
- `srp_experiment/srp/validate.py`
- `srp_experiment/eval/scoring.py`
- `srp_experiment/eval/query_flow.py`
- `srp_experiment/eval/llm_judge.py`

These files together define what is measured, how it is scored, and where fallback behavior is allowed.

## Metric Tiers

### Tier 1: Primary Paper Metrics

These are the metrics that should carry the main paper claim.

1. `drift`
2. `validation_contract_satisfaction`
3. `state_committed`

Interpretation:

- `drift` measures semantic stability across cycles
- `validation_contract_satisfaction` measures semantic contract compliance
- `state_committed` measures whether the runtime accepted or rolled back the new state

These together define the paper's core narrative:

- semantic stability
- semantic compliance
- execution stability

### Tier 2: Supporting Comparison Metrics

These are standard comparison metrics that should support, but not replace, the main claim.

- `task_success`
- `query_success`
- `tokens`
- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `latency_seconds`
- `judge_score`

Interpretation:

- task and query success show task-level retention
- token and latency metrics support efficiency and cost comparisons
- judge score is a supporting semantic-equivalence view, not the primary protocol metric

### Tier 3: SRP Protocol Validation Metrics

These metrics define the internal protocol validation layer.

- `validation_score`
- `validation_passed`
- `validation_drift`
- `validation_drift_risk`
- `validation_drift_blocks_commit`
- `validation_coverage`
- `validation_alignment`
- `validation_leakage_detected`
- `max_cycle_drift`
- `blocking_drift`
- `min_keyword_score`
- `min_coverage_score`

Interpretation:

- these explain why SRP committed or rolled back
- these are crucial for protocol debugging and reviewability
- they should be reported selectively in the paper, not all elevated to headline status

### Tier 4: Diagnostic / Fallback Metrics

These exist to preserve robustness and inspectability, not to define the main paper claim.

- proxy query-evaluation fallback behavior
- proxy judge fallback behavior
- usage accounting for query and judge prompts
- partial-crash checkpoints

Interpretation:

- these are infrastructure-confidence signals
- they matter for reproducibility and auditability
- they should not be mistaken for the primary scientific outcome

## Metric Definitions By File

### `drift`

Defined and surfaced through:

- `srp_experiment/run_experiment.py`
- `srp_experiment/eval/__init__.py` and supporting drift helper import path

Role:

- canonical semantic-stability metric for the paper

### `validation_contract_satisfaction`

Defined through:

- `srp_experiment/eval/scoring.py`

Role:

- canonical semantic contract metric
- modern replacement for the old keyword-hit interpretation

### `validation_alignment`

Defined through:

- `srp_experiment/srp/validate.py`

Role:

- typed semantic object alignment score
- key supporting SRP-specific protocol metric

### `state_committed`

Defined through:

- `srp_experiment/srp/pipeline.py`
- surfaced in `srp_experiment/run_experiment.py`

Role:

- execution-level decision metric
- commit / rollback stability view

## Fallback Policy

The current evaluation layer allows controlled fallback in two places:

- `srp_experiment/eval/query_flow.py`
- `srp_experiment/eval/llm_judge.py`

Fallback is allowed when:

- the local model context budget would be exceeded
- the evaluation prompt would fail even though the experiment result itself should still be preservable

This fallback policy is part of runtime robustness, not a redefinition of the main metric.

## Paper-Facing Rule

For the current paper:

- lead with `drift`
- support with `validation_contract_satisfaction`
- interpret execution through `state_committed`
- use efficiency metrics as supporting evidence
- keep alignment, coverage, leakage, and drift-risk metrics available for protocol explanation and appendix/detail tables

## Practical Rule

If a new metric appears, classify it first as one of:

1. primary paper metric
2. supporting comparison metric
3. SRP protocol validation metric
4. diagnostic-only metric

Do not allow a new metric to silently become part of the paper's main claim without updating this file.
