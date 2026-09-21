# SRP Decision Layer 02: Public Data Adapters

This branch is the second easiest step after freezing the SRP decision dataset schema.
It uses public datasets to teach evidence-aware decisions before any SRP-specific model training.

## Goal

Convert existing public datasets into an intermediate evidence-decision format that can support pretraining or warm-starting an SRP decision model.

The target is not a direct SRP transition dataset.
The target is a reusable evidence judgment layer:

```text
claim/query/hypothesis + evidence -> support / contradict / unknown / relevant
```

## Motivation

SRP should not depend on a hand-written problem set that proves itself against self-created examples.
Public datasets provide independent evidence structures that can train or validate whether a model understands support, contradiction, relevance, and uncertainty.

## Candidate Sources

- NLI datasets for `ENTAILMENT / CONTRADICTION / NEUTRAL`.
- FEVER and Climate-FEVER for claim verification.
- SciFact for scientific claim verification.
- BEIR tasks for query-document relevance.
- HotpotQA-style data for multi-evidence aggregation.

## Mapping Principle

Do not claim that public labels are SRP governance labels.
Map them into an intermediate decision format, then adapt to SRP later.

```text
Public data -> Evidence Decision Format -> SRP-specific fine-tuning -> Governance
```

## Intermediate Format

```json
{
  "id": "public_fever_000001",
  "source_dataset": "fever",
  "task_type": "fact_verification",
  "prompt": {
    "claim": "A candidate fact or transition-like assertion."
  },
  "evidence": [
    {
      "text": "Evidence passage.",
      "source": "wikipedia"
    }
  ],
  "label": "SUPPORTED",
  "normalized_label": "ACCEPT_LIKE",
  "notes": "SUPPORTED means evidence supports the claim, not that SRP governance should accept a mutation."
}
```

## Normalized Labels

- `ACCEPT_LIKE`: evidence supports the claim or hypothesis.
- `REJECT_LIKE`: evidence contradicts the claim or hypothesis.
- `REVIEW_LIKE`: evidence is neutral, missing, ambiguous, or insufficient.
- `RELEVANT`: evidence is relevant to the query.
- `IRRELEVANT`: evidence is not relevant to the query.

## Recommended Locations

- `experiments/decision_layer/public_data/`
- `experiments/decision_layer/public_data/adapters/`
- `experiments/decision_layer/public_data/registry.py`
- `data/decision_layer/public/manifest.json`

## Implementation Steps

1. Define the intermediate evidence-decision schema.
2. Add one tiny fixture adapter for each source family:
   - NLI
   - fact verification
   - retrieval relevance
   - multi-evidence QA
3. Add converters from public labels to normalized labels.
4. Add provenance manifests for every converted sample.
5. Add tests that prevent normalized labels from being treated as SRP ground truth.

## Evaluation Hooks

Before SRP-specific training, report:

- label distribution
- source distribution
- average evidence count
- contradiction rate
- unknown/review-like rate
- duplicate or leakage warnings

## Success Criteria

- At least one fixture adapter proves the conversion path.
- Public labels are explicitly separated from SRP labels.
- The converted output can be consumed by later DeBERTa or Qwen-head branches.
- Documentation states that public data teaches evidence judgment, not governance authority.

## Research Boundary

Public data can improve evidence understanding.
It cannot define what an admissible SRP state mutation is.
That final boundary remains SRP-specific and governance-defined.
