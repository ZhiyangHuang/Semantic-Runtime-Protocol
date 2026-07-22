# Runtime Governance Validation Plan

This plan turns the proposed Phase IX / X / XI additions into a single experimental chapter for SRP.

## Goal

Strengthen the systems claim that SRP is:

1. necessary for safe semantic transition governance,
2. useful for LLM-generated semantic updates, and
3. measurable in runtime overhead.

The intent is not to add more benchmark breadth. The intent is to add necessity, applicability, and cost evidence.

## Design Principles

- Reuse existing harnesses where possible.
- Keep all new experiments aligned with the current SRP claim boundary.
- Measure governance properties directly rather than proxy performance alone.
- Do not widen the abstract or main paper claims until the new evidence lands.

## Phase 0: Freeze the Evaluation Contract

Before any new experiment code lands, freeze a shared runtime governance evaluation contract so that Phase IX, X, and XI all evaluate the same object.

### Recommended Location

- `experiments/runtime_governance/contract.py`

### Contract Shape

```python
class TransitionCase:
    state_before
    delta
    evidence
    governance_policy
    expected_decision


class GovernanceResult:
    accepted
    state_changed
    authority_changed
    rollback_valid
    verification_score
    trace
```

### Purpose

This contract prevents the ablation, LLM integration, and latency work from drifting into three separate protocols.
The `trace` field records the auditable transition event, including timing for `proposal`, `validation`, `evidence`, `governance`, `commit`, and `total` execution.

## Phase IX: Component Ablation and Failure Injection

### Objective

Show that the observed behavior depends on the governance boundary and not on any single subsystem.

### Reuse

- `experiments/mechanism_ablation/`
- `experiments/compatibility/recovery_ablation.py`
- `experiments/compatibility/policy_intervention_harness.py`
- `experiments/compatibility/policy_boundary_harness.py`

### Proposed Outputs

- Invalid transition acceptance rate
- State corruption after reject
- Authority escalation rate
- Rollback correctness

### Suggested Variants

- `full_srp`
- `no_governance`
- `evidence_as_authority`
- `no_validation`
- `no_evidence`
- `direct_mutation`

### Suggested Failure Injections

- evidence inflation
- optimizer hijacking
- authority injection
- invariant violation with high-confidence evidence

### Primary Metrics

- unauthorized transition acceptance
- authority escalation
- state corruption after reject
- rollback correctness

### Recommended Location

If implemented as new code, keep it under a single namespace rather than scattering across multiple packages.

Recommended package:

- `experiments/runtime_governance/ablation.py`
- `experiments/runtime_governance/failure_injection.py`
- `experiments/runtime_governance/runner.py`

## Phase X: LLM Proposal Integration

### Objective

Show that SRP is useful when an LLM proposes semantic transitions but does not receive direct write authority.

### Reuse

- `experiments/compatibility/prompting.py`
- `experiments/common/local_llm.py`
- `experiments/compatibility/srp/`
- `experiments/compatibility/run_transition_reconstruction.py`

### Baseline Comparison

- Direct LLM write
- LLM proposal plus SRP validation and governance

### Suggested Metrics

- correct update rate
- false update rate
- contradiction rate
- unauthorized mutation rate
- rollback correctness
- latency overhead

### Suggested Runtime Shape

```text
LLM -> proposed Delta_t -> SRP validation -> SRP governance -> memory update
```

This should remain a proposal-to-state pipeline, not a benchmark of model quality.

### Recommended Location

- `experiments/runtime_governance/llm_transition/`
- `experiments/runtime_governance/llm_proposals.py`
- `experiments/runtime_governance/llm_runtime_runner.py`

## Phase XI: Runtime Overhead

### Objective

Quantify the operational cost of governance.

### Reuse

- existing timing fields in benchmark and compatibility runners
- any runner that already emits `latency_seconds`

### Suggested Breakdown

- proposal generation
- validation
- evidence evaluation
- governance decision
- state commit

### Suggested Metrics

- validation latency
- evidence latency
- governance latency
- commit latency
- total transition latency

### Trace Boundary

Latency should be captured inside `TransitionTrace` as observational metadata. The executor must keep the same accept/reject semantics regardless of whether timing is enabled.
For Phase X, the proposal generation time should flow into `TransitionCase.metadata["proposal_ms"]` so the same trace schema can record `proposal`, `validation`, `evidence`, `governance`, `commit`, and `total` timing.

### Preferred Summary

Report the latency results as a component breakdown plus a single total overhead line. Keep the discussion focused on governance cost rather than system profiling.

### Recommended Location

- `experiments/runtime_governance/latency.py`

## Suggested Section Order for the Paper

If these experiments are implemented, the paper section order should become:

1. Core Governance Validation
2. Component Ablation and Failure Injection
3. Reconstruction Case Study
4. LLM-based Semantic Transition Integration
5. Transition Configuration Sensitivity and Runtime Cost
6. Robustness
7. External Validation

## Suggested Implementation Order

1. Freeze the shared contract.
2. Add component ablation and failure injection.
3. Add runtime overhead measurement.
4. Add LLM proposal integration.
5. Update the paper tables and narrative.

## Notes

- Avoid adding more external benchmarks before the necessity evidence is in place.
- Avoid changing the abstract to claim improved correctness or safety.
- Keep the new experiments focused on governance admissibility, authority separation, and runtime cost.

## v1.1 Runtime Integration Roadmap

The next extension after Phase IX / X / XI is a runtime integration evaluation that inserts SRP as an admission-control layer in an existing semantic runtime.

- Spec: [docs/plans/RUNTIME_INTEGRATION_EVALUATION_SPEC.md](RUNTIME_INTEGRATION_EVALUATION_SPEC.md)
- Scope: one runtime, one adapter, one workload family, one admission boundary
- Goal: validate runtime insertion without turning SRP into a memory benchmark
