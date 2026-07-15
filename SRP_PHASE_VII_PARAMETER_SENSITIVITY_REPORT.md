# SRP Phase VII-B Parameter Sensitivity and Governance Tradeoff Report

This report freezes the Phase VII-B parameter-sensitivity evidence package for SRP.
It is an evaluation report, not a calibration artifact, not a runtime policy, and not a governed update directive.

## 1. Purpose

Phase VII-B measures how SRP parameters influence semantic fidelity, structural preservation, reconstruction cost, and governance stability under a frozen relation-aware recovery baseline.

## 2. Frozen Scope

| Setting | Value |
| --- | --- |
| Phase | `phase_vii_parameter_sensitivity` |
| Evaluation mode | `governance_tradeoff_analysis` |
| Workload | `phase_vi_relation_recovery_mvp` |
| Objective | `governed_reconstruction` |
| Evidence backend | `relation_closure` |
| Recovery strategy | `relation_closure` |
| Baseline activation threshold | `0.9` |
| Baseline recovery minimum evidence | `1` |
| Baseline preserve evidence | `False` |
| Baseline archive relations | `False` |
| Baseline relation depth | `1` |

The protocol keeps the workload, semantic state family, objective, evidence backend, and recovery strategy fixed.
Only the parameter axes change across runs.

## 3. Metrics Schema

- Schema version: `phase_vii_parameter_sensitivity_metrics_schema.v1`
- Coverage definition: matched semantic units divided by original semantic units
- Drift definition: weighted combination of fact drift, relation drift, and hallucinated relation rate
- Sensitivity definition: one-factor-at-a-time parameter sweeps over a frozen relation-aware recovery baseline
- Evidence cost definition: scalar cost attached to the recovery case

## 4. Summary

| Metric | Value |
| --- | ---: |
| Run count | `10` |
| Mean semantic coverage | `0.718536` |
| Mean semantic drift | `0.138541` |
| Mean fact accuracy | `0.8895` |
| Mean relation accuracy | `0.81845` |
| Mean recovery accuracy | `0.67109` |
| Mean closure accuracy | `0.76635` |
| Mean path preservation | `0.7236` |
| Mean neighborhood completeness | `0.7422` |
| Mean hallucinated relation rate | `0.036` |
| Mean evidence cost | `1.698` |
| Mean coverage delta vs baseline | `-0.009559` |
| Mean drift delta vs baseline | `0.040208` |
| Mean cost delta vs baseline | `0.003` |
| Baseline run | `sensitivity_baseline` |

## 5. Parameter Axis Summary

### baseline

| Value | Coverage | Drift | Relation Acc. | Closure Acc. | Evidence Cost | Delta Drift | Delta Cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | `0.728095` | `0.098333` | `0.865` | `0.7975` | `1.695` | `0.0` | `0.0` |

### archive_relations

| Value | Coverage | Drift | Relation Acc. | Closure Acc. | Evidence Cost | Delta Drift | Delta Cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `True` | `0.758095` | `0.077083` | `0.8825` | `0.82` | `1.815` | `-0.02125` | `0.12` |

### preserve_evidence

| Value | Coverage | Drift | Relation Acc. | Closure Acc. | Evidence Cost | Delta Drift | Delta Cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `True` | `0.738095` | `0.083333` | `0.865` | `0.7975` | `1.755` | `-0.015` | `0.06` |

### relation_depth

| Value | Coverage | Drift | Relation Acc. | Closure Acc. | Evidence Cost | Delta Drift | Delta Cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0` | `0.199643` | `0.628333` | `0.07` | `0.0075` | `1.025` | `0.53` | `-0.67` |
| `2` | `0.839524` | `0.0` | `1.0` | `1.0` | `1.855` | `-0.098333` | `0.16` |
| `3` | `0.849524` | `0.005` | `1.0` | `1.0` | `2.015` | `-0.093333` | `0.32` |

### activation_threshold

| Value | Coverage | Drift | Relation Acc. | Closure Acc. | Evidence Cost | Delta Drift | Delta Cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0.1` | `0.792095` | `0.138333` | `0.8785` | `0.81475` | `1.711` | `0.04` | `0.016` |
| `0.3` | `0.776095` | `0.128333` | `0.877` | `0.81325` | `1.707` | `0.03` | `0.012` |
| `0.5` | `0.760095` | `0.118333` | `0.8755` | `0.8095` | `1.703` | `0.02` | `0.008` |
| `0.7` | `0.744095` | `0.108333` | `0.871` | `0.8035` | `1.699` | `0.01` | `0.004` |

## 6. Pareto Frontier

The frontier lists non-dominated parameter settings under coverage maximization and drift/cost minimization.

| Run | Axis | Value | Coverage | Drift | Cost |
| --- | --- | --- | ---: | ---: | ---: |
| `sensitivity_baseline` | `baseline` | `baseline` | `0.728095` | `0.098333` | `1.695` |
| `sensitivity_archive_relations_true` | `archive_relations` | `True` | `0.758095` | `0.077083` | `1.815` |
| `sensitivity_preserve_evidence_true` | `preserve_evidence` | `True` | `0.738095` | `0.083333` | `1.755` |
| `sensitivity_relation_depth_0` | `relation_depth` | `0` | `0.199643` | `0.628333` | `1.025` |
| `sensitivity_relation_depth_2` | `relation_depth` | `2` | `0.839524` | `0.0` | `1.855` |
| `sensitivity_relation_depth_3` | `relation_depth` | `3` | `0.849524` | `0.005` | `2.015` |
| `sensitivity_activation_threshold_0_1` | `activation_threshold` | `0.1` | `0.792095` | `0.138333` | `1.711` |
| `sensitivity_activation_threshold_0_3` | `activation_threshold` | `0.3` | `0.776095` | `0.128333` | `1.707` |
| `sensitivity_activation_threshold_0_5` | `activation_threshold` | `0.5` | `0.760095` | `0.118333` | `1.703` |
| `sensitivity_activation_threshold_0_7` | `activation_threshold` | `0.7` | `0.744095` | `0.108333` | `1.699` |

## 7. Interpretation

The baseline and sweep results expose how each parameter shifts the tradeoff surface between semantic fidelity, structure preservation, and reconstruction cost.
They do not claim a universally optimal parameter setting.

## 8. Relation to the Paper

Phase VII-B extends the paper's evidence chain by explaining how governed parameters move the system across fidelity-cost tradeoff regions without introducing autonomous adaptation.

Generated: `2026-07-14T22:35:59.193016+00:00`
