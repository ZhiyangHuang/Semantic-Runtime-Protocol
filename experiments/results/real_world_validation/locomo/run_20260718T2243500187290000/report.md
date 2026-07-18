# Real Validation Report

This report bundle is generated from the real-validation branch.

## Metadata

- experiment: `locomo_transition_validation`
- version: `v1`
- generated_at: `2026-07-18T22:43:50.018729+00:00`
- runtime_contract: `srp-real-validation-v1`
- commit: `39053895ef73b6adc5b87a7970c2849636de4eab`
- dataset: `LoCoMo`
- scope: `external_validation`

## Claim Mapping

- claim_id: `authority_independence`
- paper_section: `3.5`
- observable_behavior: `additional evidence improves verification without increasing authority`
- experiment_events: `('contradiction_update', 'temporal_refinement', 'unsupported_mutation')`
- promotion_level: `appendix_support`
- claim_scope: `evaluated setting`

## Metrics

### Transition

- accepted_transitions: `2`
- rejected_transitions: `1`
- invalid_accept_rate: `0.0`

### Governance

- authority_changed_with_evidence: `False`
- recommendation_execution_separated: `True`
- replay_consistency: `1.0`
- authority_escalation_rate: `0.0`
- evidence_improvement: `0.183333`

### Task

- memory_accuracy: `1.0`
- relation_accuracy: `1.0`
- fact_accuracy: `1.0`
- coverage: `1.0`

## Decision

- claim_supported: `True`
- support_level: `appendix`
- scope: `evaluated LoCoMo subset`
- promotion: `appendix`
- reason: `governance preserved authority separation under the evaluated setting`
