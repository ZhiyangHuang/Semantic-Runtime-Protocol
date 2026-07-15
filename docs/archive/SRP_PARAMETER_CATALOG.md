# SRP Parameter Catalog

This document is the concrete catalog of SRP parameters.
It sits between the theoretical parameter space model and any runtime registry.

The catalog answers:

- what parameter exists now
- which module owns it
- whether it is fixed, tunable, adaptive, or derived
- what metric it is expected to affect
- what default or current value is observed

---

## 1. Catalog Legend

### 1.1 Classes

- `Fixed`: protocol constant, not tuned in ordinary experiments
- `Tunable`: runtime parameter, eligible for sweep or calibration
- `Adaptive`: intended for Milestone 3 or later learning-based adaptation
- `Derived`: computed value, not directly hand-tuned

### 1.2 Status

- `Draft`: defined conceptually, not yet standardized
- `Experimental`: present in code or experiments, still under evaluation
- `Validated`: supported by repeated experiments
- `Frozen`: part of the stable protocol boundary

---

## 2. Catalog

| Parameter | Module | Class | Status | Default / Current | Range / Notes | Metric | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `lifecycle_retained_importance` | Lifecycle | Tunable | Frozen | `0.35` | minimum importance for retention | retention quality | `LifecyclePolicy` |
| `lifecycle_retained_passes` | Lifecycle | Tunable | Frozen | `2` | minimum verification passes | stability / retention | `LifecyclePolicy` |
| `lifecycle_archived_importance` | Lifecycle | Tunable | Frozen | `0.3` | archive-risk threshold | archival precision | `LifecyclePolicy` |
| `lifecycle_archived_drift_count` | Lifecycle | Tunable | Frozen | `2` | archival-risk drift count | archive recall | `LifecyclePolicy` |
| `lifecycle_archived_failure_count` | Lifecycle | Tunable | Frozen | `2` | archival-risk failure count | archive recall | `LifecyclePolicy` |
| `lifecycle_decayed_floor` | Lifecycle | Tunable | Frozen | `0.05` | lower bound for decay | stability | `LifecyclePolicy` |
| `lifecycle_decayed_multiplier` | Lifecycle | Tunable | Frozen | `0.92` | decay multiplier | stability / drift | `LifecyclePolicy` |
| `activation` | Activation | Derived | Experimental | event payload value | direct state update value | state responsiveness | `ActivationUpdateOperator` |
| `activation_delta` | Activation | Tunable | Experimental | event payload value | incremental activation update | responsiveness | `ActivationUpdateOperator` |
| `activation_threshold` | Activation / Approximation | Tunable | Experimental | `0.2` in approximation operator | sweep candidate for approximation and selection | semantic fidelity / compression | `ApproximationOperator` |
| `approximation_target_id` | Approximation | Fixed | Experimental | optional payload field | not a numeric knob | representative selection | `ApproximationOperator` |
| `preserve_fields` | Approximation | Tunable | Experimental | `["entity_type", "name"]` | payload projection policy | information retention | `ApproximationOperator` |
| `merged_unit_id` | Merge | Fixed | Experimental | event payload fallback | identity of merged result | merge correctness | `MergeOperator` |
| `canonical_name` | Merge | Fixed | Experimental | source canonical name fallback | structural identity field | semantic fidelity | `MergeOperator` |
| `aliases` | Merge | Derived | Experimental | list payload | merged alias set | identity continuity | `MergeOperator` |
| `provenance` | Merge | Derived | Experimental | list payload | merged provenance set | traceability | `MergeOperator` |
| `lineage` | Merge | Derived | Experimental | list payload | merged lineage set | history continuity | `MergeOperator` |
| `semantic_payload` | Merge | Fixed | Experimental | payload or source payload | merged payload container | semantic fidelity | `MergeOperator` |
| `minimum_source_units` | Merge | Tunable | Experimental | `2` implicit | merge requires at least two sources | merge validity | `MergeOperator` |
| `evidence_refs` | Forgetting | Fixed | Experimental | optional payload list | evidence preservation input | auditability | `ForgettingOperator` |
| `preserve_evidence` | Forgetting | Tunable | Experimental | `True` | gate for evidence requirement | traceability | `ForgettingOperator` |
| `archive_relations` | Forgetting | Tunable | Experimental | `True` | whether relation markers are archived | archive completeness | `ForgettingOperator` |
| `target_unit_ids` | Forgetting | Fixed | Experimental | event payload or targets | forgetting target set | forgetting validity | `ForgettingOperator` |
| `decision_candidate_limit` | Decision | Tunable | Draft | not yet centralized | candidate cap for ranking | runtime cost | `DecisionEngine` |
| `constraint_weight` | Decision | Tunable | Draft | not yet centralized | ranking weight | decision quality | `DecisionEngine` |
| `metric_weight` | Decision | Tunable | Draft | not yet centralized | ranking weight | decision quality | `DecisionEngine` |
| `history_weight` | Decision | Tunable | Draft | not yet centralized | ranking weight | replay / history quality | `DecisionEngine` |
| `operator_priority` | Decision | Tunable | Draft | not yet centralized | ranking priority | operator selection | `DecisionEngine` |
| `checkpoint_interval` | Checkpoint | Tunable | Draft | not yet centralized | checkpoint frequency | replay acceleration | `CheckpointManager` |
| `checkpoint_retention` | Checkpoint | Tunable | Draft | not yet centralized | retained checkpoint count / window | storage and replay cost | `CheckpointManager` |
| `checkpoint_anchor_policy` | Checkpoint | Tunable | Draft | not yet centralized | anchor selection policy | replay stability | `CheckpointManager` |
| `archive_threshold` | Archive | Tunable | Draft | not yet centralized | archive trigger threshold | archive precision | `ArchiveService` |
| `archive_priority` | Archive | Tunable | Draft | not yet centralized | archive precedence | archive utility | `ArchiveService` |
| `archive_retention_window` | Archive | Tunable | Draft | not yet centralized | how long evidence is retained | governance memory | `ArchiveService` |
| `minimum_evidence` | Recovery | Tunable | Draft | not yet centralized | evidence floor for recovery | recovery success | `RecoveryOperator` |
| `minimum_confidence` | Recovery | Tunable | Draft | not yet centralized | confidence floor | recovery precision | `RecoveryOperator` |
| `evidence_weight` | Recovery | Tunable | Draft | not yet centralized | evidence weighting | recovery quality | `RecoveryOperator` |
| `archive_priority` | Recovery | Tunable | Draft | not yet centralized | archive source preference | recovery quality | `RecoveryOperator` |
| `trace_priority` | Recovery | Tunable | Draft | not yet centralized | trace source preference | replay fidelity | `RecoveryOperator` |
| `activation_decay_rate` | Activation | Tunable | Draft | not yet centralized | proposed runtime sweep variable | replay fidelity / responsiveness | `ActivationUpdateOperator` |
| `activation_boost_rate` | Activation | Tunable | Draft | not yet centralized | proposed runtime sweep variable | responsiveness | `ActivationUpdateOperator` |
| `merge_similarity_threshold` | Merge | Tunable | Draft | not yet centralized | proposed runtime sweep variable | semantic accuracy | `MergeOperator` |
| `recovery_min_evidence` | Recovery | Tunable | Draft | not yet centralized | proposed runtime sweep variable | recovery success | `RecoveryOperator` |
| `adaptive_activation_weight` | Activation | Adaptive | Draft | future Milestone 3 | learned weight | long-term stability | `AdaptivePolicy` |

---

## 3. Observed Code Surfaces

The catalog is intentionally conservative.
It only treats a value as a candidate parameter if it is visible in the current repository.

Observed surfaces include:

- `policy_spec()` and `policy_flat()` in [srp_experiment/srp/state_summaries.py](/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/srp/state_summaries.py)
- `activation_threshold` in [srp_runtime/operators/approximation.py](/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_runtime/operators/approximation.py)
- evidence preservation and archive toggles in [srp_runtime/operators/forgetting.py](/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_runtime/operators/forgetting.py)
- event payload update knobs in [srp_runtime/operators/activation.py](/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_runtime/operators/activation.py)
- budget configuration in [srp_experiment/budgeting.py](/c:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/budgeting.py)

---

## 4. Boundary Rules

The catalog must preserve module ownership.

Rules:

- a parameter should have one primary owner module
- other modules may read it, but should not redefine it
- `Fixed` parameters are part of the frozen protocol boundary
- `Tunable` parameters are eligible for sensitivity analysis
- `Adaptive` parameters are reserved for future learning control
- `Derived` parameters are computed and should not be hand-tuned directly

---

## 5. Registry Bridge

The runtime registry should be generated or maintained from this catalog, not invented independently.

Suggested runtime shape:

```text
srp_runtime/
    config/
        parameter_registry.py
        defaults.py
        validation.py
```

The registry should stay narrower than the catalog.
It should only expose parameters that the runtime actually consumes.

---

## 6. First Calibration Targets

The first useful calibration set should focus on parameters with visible runtime effect and measurable outcomes.

Recommended starting set:

- `activation_threshold`
- `lifecycle_retained_importance`
- `lifecycle_archived_importance`
- `preserve_evidence`
- `archive_relations`
- `decision_candidate_limit`
- `checkpoint_interval`

Recommended metrics:

- semantic fidelity
- replay fidelity
- compression ratio
- recovery success
- runtime cost
- history stability

---

## 7. Next Step

After this catalog is stable, the next artifact should be the runtime registry.

That registry should be a thinner operational layer, not another theory document.

