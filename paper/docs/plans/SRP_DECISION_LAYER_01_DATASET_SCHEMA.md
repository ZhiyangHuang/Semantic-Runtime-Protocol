# SRP Decision Layer 01: Dataset Schema

This is the lowest-risk implementation branch for adding a learned decision layer to SRP.
It does not train a model and does not change runtime governance behavior.
The branch only freezes the data contract used by later DeBERTa, distillation, Qwen-head, and Jev-style experiments.

## Goal

Define a reproducible SRP transition decision dataset:

```text
S_t + Delta + Evidence + Governance Context -> ACCEPT / REJECT / REVIEW
```

The learned model is never treated as authority.
It produces decision evidence that remains subordinate to deterministic SRP Governance.

## Scope

- Define the canonical example schema.
- Define label meanings and labeling rules.
- Define train/validation/test split rules.
- Define artifact locations for generated datasets.
- Define minimum validation checks before model work begins.

## Non-Goals

- No model training.
- No online decision model.
- No Jev API integration.
- No change to SRP acceptance semantics.
- No paper claim expansion.

## Dataset Unit

Each example should represent one candidate semantic transition:

```json
{
  "id": "srp_transition_000001",
  "scenario_id": "authority_missing_evidence_v1",
  "state": {
    "contract": {},
    "policy": {},
    "authority": {}
  },
  "observation": {},
  "evidence": [],
  "candidate_transition": {
    "operation": "update",
    "subject": "semantic_state.value",
    "old_value": "A",
    "new_value": "B"
  },
  "governance_context": {
    "requires_evidence": true,
    "authority_source": "governance"
  },
  "label": "REJECT",
  "label_reason": "Contract requires evidence and no admissible evidence is present.",
  "source": {
    "generator": "srp_rules",
    "version": "v1"
  }
}
```

## Labels

- `ACCEPT`: the candidate transition is admissible if deterministic governance also passes.
- `REJECT`: the candidate transition violates contract, evidence, authority, or state invariants.
- `REVIEW`: the case is ambiguous, contradictory, underspecified, or intentionally delegated to a human/review queue.

## Label Source Priority

1. SRP deterministic governance rules.
2. Existing SRP replay or benchmark traces.
3. Human review for ambiguous cases.
4. Teacher model annotations only as auxiliary evidence, never as ground truth.

## Split Rules

Split by `scenario_id` or transition family rather than random example rows.
This avoids leakage where near-identical transitions appear in both train and test.

Recommended initial split:

```text
train: 70%
validation: 15%
test: 15%
```

## Recommended Locations

- `data/decision_layer/schema/`
- `data/decision_layer/generated/`
- `experiments/decision_layer/schema.py`
- `experiments/decision_layer/validate_dataset.py`
- `experiments/decision_layer/tests/`

## Validation Checks

- Every example has one of `ACCEPT`, `REJECT`, or `REVIEW`.
- Every example has `state`, `candidate_transition`, `evidence`, and `governance_context`.
- IDs are unique.
- Scenario-level split leakage is rejected.
- Label distribution is reported.
- Source provenance is recorded for every example.

## Success Criteria

- A stable schema is committed.
- A small fixture dataset exists for tests.
- Dataset validation can run without model dependencies.
- Later model branches can consume the dataset without redefining labels.

## Implementation Steps

1. Add dataclasses or typed dictionaries for the decision dataset schema.
2. Add JSONL fixture examples covering all three labels.
3. Add a validator that checks schema, labels, provenance, and split leakage.
4. Add unit tests for valid, invalid, and leakage cases.
5. Document how deterministic governance labels are produced.

## Research Boundary

This phase preserves the SRP principle:

```text
Prediction != Evidence
Evidence != Authority
Authority != Execution
```

The dataset may train a model to predict decisions, but the trained model must not replace governance authority.
