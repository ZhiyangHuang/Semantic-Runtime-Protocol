# Semantic Runtime Protocol

SRP is a semantic runtime protocol that models evolving semantic state through explicit transitions, constraints, traces, and replayable history.

Milestone 1 establishes a verified transition kernel: `Event -> Constraint -> Operator -> Transition -> Trace -> Replay`.

Milestone 2 extends the kernel with deterministic decision boundaries, semantic commits, version DAGs, replay checkpoints, and evidence-based conflict analysis.

Milestone 2 also adds a bounded resolution-decision layer that turns verified conflict evidence into future semantic intent without rewriting history.

The system separates semantic mutation, historical versioning, replay acceleration, and archive evidence retrieval into independent runtime layers.

Current validation covers deterministic execution, branching history, checkpoint isolation, replay equivalence, and conflict evidence lookup.

SRP is not a model cache, not a plain RAG stack, and not a lightweight wrapper around version control; it is a protocol for runtime semantic evolution and verifiable history.

This repository implements SRP as a model-independent semantic runtime protocol.

## Protocol Positioning

SRP manages `semantic runtime state`, not token hidden state. It does not cache transformer `K/V` tensors and it does not depend on model-internal KV cache reuse.

SRP should be understood as a protocol over semantic state:

- It preserves typed semantic objects, runtime metadata, and verification history.
- It uses stable recovery templates to improve `prompt-prefix stability`.
- It can benefit systems that support prefix caching, but KV cache reuse is only an optional experimental signal, not a core SRP dependency.

## Architecture

The project-level architecture is documented in [SRP Semantic Evolution Architecture](SRP_SEMANTIC_EVOLUTION_ARCHITECTURE.md).
That document is the best starting point for understanding how representation, evolution, execution, and evaluation fit together.

## Milestone 2 Overview

For the paper-style one-page summary, see [SRP Runtime Kernel Milestone 2: Governed Semantic Evolution Runtime](SRP_RUNTIME_KERNEL_MILESTONE_2_PAPER_SUMMARY.md).
For the milestone landing page, see [SRP Runtime Kernel Milestone 2](SRP_RUNTIME_KERNEL_MILESTONE_2_LANDING.md).
For the final verified Milestone 2 boundary snapshot, see [SRP Runtime Kernel Milestone 2 Final State](SRP_RUNTIME_KERNEL_MILESTONE_2_FINAL_STATE.md).
For a short, citation-friendly snapshot of the version-aware runtime, see [SRP Runtime Kernel Milestone 2 Overview](SRP_RUNTIME_KERNEL_MILESTONE_2_OVERVIEW.md).
For the current verified boundary snapshot, see [SRP Runtime Kernel Milestone 2 Status Summary](SRP_RUNTIME_KERNEL_MILESTONE_2_STATUS_SUMMARY.md).

## Milestone 3 Preview

For the boundary preview of adaptive semantic evolution, see [SRP Runtime Kernel Milestone 3: Adaptive Semantic Evolution Boundary](SRP_RUNTIME_KERNEL_MILESTONE_3_BOUNDARY_PREVIEW.md).

## Experimental Infrastructure

SRP now includes a parameter calibration framework for evaluating runtime behavior before future adaptive evolution.
For a stack-level overview of how the legacy measurement stack and the calibration / validation stack relate, see [SRP Experiment Stack Overview](SRP_EXPERIMENT_STACK_OVERVIEW.md).

Current validated sensitivity studies:

- `activation_threshold`
  - semantic mutation behavior
- `recovery_min_evidence`
  - evidence-based recovery governance
- `preserve_evidence`
  - history and audit retention trade-off
- `archive_relations`
  - archive evidence boundary

Current validated interaction study:

- `activation_threshold x recovery_min_evidence`
  - boundary interaction between semantic mutation and recovery governance

For the baseline empirical summary, see [SRP Sensitivity Baseline Report](SRP_SENSITIVITY_BASELINE_REPORT.md).
For the interaction model, see [SRP Parameter Interaction Analysis Model](SRP_PARAMETER_INTERACTION_ANALYSIS_MODEL.md).
For the Phase I calibration closure, see [SRP Parameter Calibration Phase I Report](SRP_PARAMETER_CALIBRATION_PHASE_I_REPORT.md).
For the Phase I observability report, see [SRP Phase I Observability Report](SRP_PHASE_I_OBSERVABILITY_REPORT.md).
For the calibration round result model, see [SRP Calibration Round Result Model](SRP_CALIBRATION_ROUND_RESULT_MODEL.md).
For the calibration roadmap freeze, see [SRP Calibration Roadmap Freeze](SRP_CALIBRATION_ROADMAP_FREEZE.md).
For the Phase II closure validation model, see [SRP Phase II Closure Validation Model](SRP_PHASE_II_CLOSURE_VALIDATION_MODEL.md).
For the experiment environment freeze, see [SRP Experiment Environment Freeze](SRP_EXPERIMENT_ENV_FREEZE.md).

### Phase II Closure Validation

Phase II closure validation is a separate validation layer, not calibration.
For the closure evidence package, see [SRP Phase II Closure Validation Report](SRP_PHASE_II_CLOSURE_VALIDATION_REPORT.md).
For the Phase II boundary validation report, see [SRP Phase II Boundary Validation Report](SRP_PHASE_II_BOUNDARY_VALIDATION_REPORT.md).
For the Phase II density baseline report, see [SRP Phase II Density Baseline Report](SRP_PHASE_II_DENSITY_BASELINE_REPORT.md).
For the Phase II boundary generalization report, see [SRP Phase II Boundary Generalization Report](SRP_PHASE_II_BOUNDARY_GENERALIZATION_REPORT.md).
For the Phase III-A baseline comparison report, see [SRP Phase III-A Baseline Comparison Report](SRP_PHASE_III_A_BASELINE_COMPARISON_REPORT.md).
For the Phase V retention and drift baseline report, see [SRP Phase V Retention and Drift Report](SRP_PHASE_V_RETENTION_REPORT.md).
For the Phase V retention sensitivity plan, see [SRP Phase V Retention Sensitivity Plan V1](SRP_PHASE_V_RETENTION_SENSITIVITY_PLAN_V1.md).
For the audit evidence appendix, see [SRP Phase II Validation Appendix](SRP_PHASE_II_VALIDATION_APPENDIX.md).
For the Phase I observability data export, see `experiments/results/phase_i/`.
For the Phase II boundary candidate export, see `experiments/results/phase_ii_boundary/`.
For the Phase II boundary figures, see `experiments/results/phase_ii_boundary/figures/`.
For the Phase II density baseline export, see `experiments/results/phase_ii_density_baseline/`.
For the Phase V retention and drift export, see `experiments/results/phase_v_retention/`.

Validated checks:

- boundary stability
- cross-condition validation
- reproducibility
- evidence consistency

It verifies frozen Phase II regions under controlled runtime variations and does not search for new parameter regions.

### Stack Framing

Legacy measurement stack:

- `srp_experiment/`
- historical runtime evaluation
- compression / recovery / benchmark evidence

Calibration and validation stack:

- `experiments/`
- parameter boundary discovery
- closure validation
- paper-facing Phase II boundary validation report generation
- future adaptive boundary preparation

Config layer:

- `configs/phase_ii_validation.env`
- `configs/phase_iii_a.env`
- `configs/semantic_backend_comparison.env`
- `configs/phase_v_retention.env`
- phase-scoped experiment settings
- legacy `.env` remains the measurement default
- `experiments/config.py` loads typed phase configs

Phase III-A boundary preview:

- [SRP Constrained Parameter Optimization Boundary](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_BOUNDARY.md)
- [SRP Constrained Parameter Optimization Protocol](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_PROTOCOL.md)
- [SRP Constrained Parameter Optimization Round 1 Report](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_ROUND_1_REPORT.md)
- [SRP Phase III-A Baseline Comparison Report](SRP_PHASE_III_A_BASELINE_COMPARISON_REPORT.md)
- [SRP Phase III-A Objective Sensitivity Report](SRP_PHASE_III_A_OBJECTIVE_SENSITIVITY_REPORT.md)
- [SRP Constrained Parameter Optimization Round 1 Analysis](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_ROUND_1_ANALYSIS.md)
- [SRP Phase II Boundary Generalization Report](SRP_PHASE_II_BOUNDARY_GENERALIZATION_REPORT.md)
- [SRP Phase V Retention and Drift Evaluation](SRP_PHASE_V_RETENTION_DRIFT_EVALUATION.md)
- [SRP Phase V Retention and Drift Report](SRP_PHASE_V_RETENTION_REPORT.md)
- [SRP Phase V Retention Sensitivity Plan V1](SRP_PHASE_V_RETENTION_SENSITIVITY_PLAN_V1.md)
- constrained optimization over validated feasible regions
- not reinforcement learning
- not adaptive execution
- naive full-grid comparison baseline for governed optimization
- objective-weight stability analysis for governed optimization

Semantic backend comparison study:

- [SRP Semantic Backend Comparison Protocol](SRP_SEMANTIC_BACKEND_COMPARISON_PROTOCOL.md)
- [SRP Semantic Backend Comparison Report](SRP_SEMANTIC_BACKEND_COMPARISON_REPORT.md)
- [SRP Evidence Escalation Analysis](SRP_EVIDENCE_ESCALATION_ANALYSIS.md)
- [SRP Evidence Escalation Protocol](SRP_EVIDENCE_ESCALATION_PROTOCOL.md)
- [SRP Evidence Escalation Appendix](SRP_EVIDENCE_ESCALATION_APPENDIX.md)
- semantic backend comparison result package: `experiments/results/semantic_backend_comparison/`
- vector-only baseline vs local semantic evidence augmentation
- evidence-source comparison without authority transfer
- [SRP Phase V Retention and Drift Evaluation](SRP_PHASE_V_RETENTION_DRIFT_EVALUATION.md)
- [SRP Phase V Retention and Drift Report](SRP_PHASE_V_RETENTION_REPORT.md)
- [SRP Phase V Retention Sensitivity Plan V1](SRP_PHASE_V_RETENTION_SENSITIVITY_PLAN_V1.md)
- [SRP Phase VI Relation-Aware Recovery Design V1](SRP_PHASE_VI_RELATION_AWARE_RECOVERY_DESIGN.md)
- [SRP Phase VI Relation-Aware Recovery Plan V1](SRP_PHASE_VI_RELATION_AWARE_RECOVERY_PLAN_V1.md)
- [SRP Phase VI Relation-Aware Recovery Experiment Package](experiments/evaluation/phase_vi_relation_recovery/)
- [SRP Phase VI Relation-Aware Recovery Report](SRP_PHASE_VI_RELATION_AWARE_RECOVERY_REPORT.md)
- [SRP Phase VII Parameter Sensitivity and Stability Plan V1](SRP_PHASE_VII_PARAMETER_SENSITIVITY_STABILITY_PLAN_V1.md)
- [SRP Phase VII Parameter Sensitivity and Stability Report](SRP_PHASE_VII_PARAMETER_STABILITY_REPORT.md)
- [SRP Phase VII-B Parameter Sensitivity and Governance Tradeoff Plan V1](SRP_PHASE_VII_PARAMETER_SENSITIVITY_PLAN_V1.md)
- [SRP Phase VII-B Parameter Sensitivity and Governance Tradeoff Report](SRP_PHASE_VII_PARAMETER_SENSITIVITY_REPORT.md)
- [SRP Phase VIII Cross-Domain Validation Plan V1](SRP_PHASE_VIII_CROSS_DOMAIN_VALIDATION_PLAN_V1.md)
- [SRP Phase VIII Cross-Domain Validation Report](SRP_PHASE_VIII_CROSS_DOMAIN_VALIDATION_REPORT.md)
- [SRP Phase VIII-B Representation Invariance Report](SRP_PHASE_VIII_B_REPRESENTATION_INVARIANCE_REPORT.md)
- [SRP Phase VIII-B Representation Invariance Plan V1](SRP_PHASE_VIII_B_REPRESENTATION_INVARIANCE_PLAN_V1.md)
- [SRP Phase VIII-C Implementation Independence Report](SRP_PHASE_VIII_C_IMPLEMENTATION_INDEPENDENCE_REPORT.md)
- [SRP Phase VIII-C Implementation Independence Plan V1](SRP_PHASE_VIII_C_IMPLEMENTATION_INDEPENDENCE_PLAN_V1.md)
- [SRP External Validation Plan V1](SRP_EXTERNAL_VALIDATION_PLAN_V1.md)
- [SRP External Validation Implementation Plan V1](SRP_EXTERNAL_VALIDATION_IMPLEMENTATION_PLAN_V1.md)
- [SRP External Validation Baseline Capability Matrix V1](SRP_EXTERNAL_VALIDATION_BASELINE_CAPABILITY_MATRIX_V1.md)
- external validation LoCoMo ingestion slice: `experiments/results/external_validation_locomo_mvp/`
- LoCoMo calibration-aware rerun: `experiments/results/external_validation_locomo_calibration_aware/`
- LoCoMo manual sanity calibration slice: `experiments/results/external_validation_locomo_sanity/`
- [LoCoMo Calibration Note](SRP_LOCOMO_CALIBRATION_NOTE.md)
- [LongMemEval Calibration Note](SRP_LONGMEMEVAL_CALIBRATION_NOTE.md)
- [SRP LoCoMo Calibration-Aware External Validation Report](SRP_EXTERNAL_VALIDATION_LOCOMO_CALIBRATION_AWARE_REPORT.md)
- [SRP External Validation Adapter Calibration Note](SRP_EXTERNAL_VALIDATION_ADAPTER_CALIBRATION_NOTE.md)
- LongMemEval calibration-aware rerun: `experiments/results/external_validation_longmemeval_calibration_aware/`
- LongMemEval evidence run: `experiments/results/external_validation_longmemeval_evidence/`
- [SRP LongMemEval External Validation Evidence Report](SRP_EXTERNAL_VALIDATION_LONGMEMEVAL_EVIDENCE_REPORT.md)
- [SRP LongMemEval Evidence Audit Note](SRP_LONGMEMEVAL_EVIDENCE_AUDIT_NOTE.md)
- [SRP LongMemEval Scorer Alignment Audit](SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md)
- [SRP Evidence Audit Specification V1](SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md)
- LongMemEval evidence contract: `configs/external_validation_longmemeval_evidence.env`
- LongMemEval evidence run entrypoint: `experiments/evaluation/run_longmemeval_evidence.py`
- phase V retention and drift result package: `experiments/results/phase_v_retention/`
- phase VI relation-aware recovery result package: `experiments/results/phase_vi_relation_recovery/`
- phase VII parameter stability result package: `experiments/results/phase_vii_parameter_stability/`
- phase VII-B parameter sensitivity result package: `experiments/results/phase_vii_parameter_sensitivity/`
- phase VIII cross-domain validation result package: `experiments/results/phase_viii_cross_domain/`
- phase VIII representation invariance result package: `experiments/results/phase_viii_representation_invariance/`
- phase VIII implementation independence result package: `experiments/results/phase_viii_implementation_independence/`
- meaning-level semantic coverage and drift measurement after governed transition

Research freeze package:

- [SRP Research Freeze V1](SRP_RESEARCH_FREEZE_V1.md)
- frozen baseline for Phase I, Phase II, Phase III-A, and evidence studies
- keeps runtime, calibration, validation, optimization, and evidence layers separated

Paper construction:

- [SRP Paper Structure V1](SRP_PAPER_STRUCTURE_V1.md)
- [SRP Contribution Map V1](SRP_CONTRIBUTION_MAP_V1.md)
- [SRP Abstract V1](SRP_ABSTRACT_V1.md)
- [SRP Introduction V1](SRP_INTRODUCTION_V1.md)
- [SRP Related Work V1](SRP_RELATED_WORK_V1.md)
- [SRP System Model V1](SRP_SYSTEM_MODEL_V1.md)
- [SRP Method Overview V1](SRP_METHOD_OVERVIEW_V1.md)
- [SRP Experiments Overview V1](SRP_EXPERIMENTS_OVERVIEW_V1.md)
- [SRP Discussion V1](SRP_DISCUSSION_V1.md)
- [SRP Experiments V1](SRP_EXPERIMENTS_V1.md)
- [SRP Main Results Summary V1](SRP_MAIN_RESULTS_SUMMARY_V1.md)
- [SRP Ablation Plan V1](SRP_ABLATION_PLAN_V1.md)
- [SRP Parameter Recommendation Policy V1](SRP_PARAMETER_RECOMMENDATION_POLICY_V1.md)
- [SRP Parameter Recommendation Analysis V1](SRP_PARAMETER_RECOMMENDATION_ANALYSIS_V1.md)
- [SRP Limitations V1](SRP_LIMITATIONS_V1.md)
- [SRP Conclusion V1](SRP_CONCLUSION_V1.md)
- [SRP Paper Draft V1](SRP_PAPER_DRAFT_V1.md)
- [SRP Paper Draft V2](SRP_PAPER_DRAFT_V2.md)
- [SRP Paper Draft V3](SRP_PAPER_DRAFT_V3.md)
- [SRP Paper Final V1](SRP_PAPER_FINAL_V1.md)
- [SRP Phase V Retention Drift Evaluation](SRP_PHASE_V_RETENTION_DRIFT_EVALUATION.md)
- [SRP Phase VI Relation-Aware Recovery Design V1](SRP_PHASE_VI_RELATION_AWARE_RECOVERY_DESIGN.md)
- [SRP Phase VI Relation-Aware Recovery Plan V1](SRP_PHASE_VI_RELATION_AWARE_RECOVERY_PLAN_V1.md)
- [SRP Main Results Summary V1](SRP_MAIN_RESULTS_SUMMARY_V1.md)
- [SRP Phase VI Relation-Aware Recovery Report](SRP_PHASE_VI_RELATION_AWARE_RECOVERY_REPORT.md)
- [SRP Phase VII Parameter Sensitivity and Stability Report](SRP_PHASE_VII_PARAMETER_STABILITY_REPORT.md)
- [SRP Phase VII-B Parameter Sensitivity and Governance Tradeoff Report](SRP_PHASE_VII_PARAMETER_SENSITIVITY_REPORT.md)
- [SRP Phase VIII Cross-Domain Validation Plan V1](SRP_PHASE_VIII_CROSS_DOMAIN_VALIDATION_PLAN_V1.md)
- [SRP Phase VIII Cross-Domain Validation Report](SRP_PHASE_VIII_CROSS_DOMAIN_VALIDATION_REPORT.md)
- [SRP Phase VIII-B Representation Invariance Report](SRP_PHASE_VIII_B_REPRESENTATION_INVARIANCE_REPORT.md)
- [SRP Phase VIII-B Representation Invariance Plan V1](SRP_PHASE_VIII_B_REPRESENTATION_INVARIANCE_PLAN_V1.md)
- [SRP Phase VIII-C Implementation Independence Report](SRP_PHASE_VIII_C_IMPLEMENTATION_INDEPENDENCE_REPORT.md)
- [SRP Phase VIII-C Implementation Independence Plan V1](SRP_PHASE_VIII_C_IMPLEMENTATION_INDEPENDENCE_PLAN_V1.md)
- [SRP External Validation Plan V1](SRP_EXTERNAL_VALIDATION_PLAN_V1.md)
- [SRP External Validation Implementation Plan V1](SRP_EXTERNAL_VALIDATION_IMPLEMENTATION_PLAN_V1.md)
- [SRP External Validation Baseline Capability Matrix V1](SRP_EXTERNAL_VALIDATION_BASELINE_CAPABILITY_MATRIX_V1.md)
- external validation LoCoMo ingestion slice: `experiments/results/external_validation_locomo_mvp/`
- [SRP External Validation Adapter Calibration Note](SRP_EXTERNAL_VALIDATION_ADAPTER_CALIBRATION_NOTE.md)
- phase VIII representation invariance result package: `experiments/results/phase_viii_representation_invariance/`
- phase VIII implementation independence result package: `experiments/results/phase_viii_implementation_independence/`
- [Research Freeze Policy](RESEARCH_FREEZE_POLICY.md)
- [SRP Paper Completion Checklist](SRP_PAPER_COMPLETION_CHECKLIST.md)
- writing and positioning guide for the frozen research baseline
- frozen claims, contribution map, and paper outline

### Parameter Calibration Status

Phase I calibration is frozen.
Phase II boundary is defined.

Completed:

- Parameter observability validation
- Boundary-focused sensitivity studies
- Pairwise interaction observation

Validated parameter axes:

- `activation_threshold`
- `recovery_min_evidence`
- `preserve_evidence`
- `archive_relations`
- `relation_depth`

Current scope:

- Parameter behavior characterization, sensitivity analysis, and boundary validation

Not started:

- Parameter optimization
- Adaptive parameter policies
- Learning-based calibration

### Parameter Calibration Roadmap

Current status:

- Phase I: Parameter observability and boundary validation (Frozen)
- Phase II: Constrained calibration boundary (Defined)

Phase II does not introduce optimization or adaptive parameter updates.
It defines future evaluation boundaries while preserving SRP governance constraints.

### Calibration Infrastructure

Phase II constrained calibration is supported by:

- Parameter Calibration Protocol
- Calibration Round Boundary
- Calibration Round Result Model
- Calibration Evidence Records

Calibration outputs represent acceptable parameter regions, not optimized parameter values.

## Freeze Checklist

For the architectural boundary checklist, see [SRP Runtime Kernel Freeze Checklist](SRP_RUNTIME_KERNEL_FREEZE_CHECKLIST.md).

## Project Status

SRP has completed the construction of a governed semantic evolution runtime. Future extensions must preserve deterministic mutation, evidence-based governance, event-derived history, and bounded learning authority.

### Phase II Closure Validation

Status:

- Active validation layer

Scope:

- Verification of frozen calibration boundaries

Validated dimensions:

- boundary stability
- cross-condition robustness
- reproducibility
- evidence consistency

Non-goals:

- parameter optimization
- adaptive updates
- learning-based control

### Stack Framing

Legacy measurement stack:

- `srp_experiment/`
- historical runtime evaluation
- compression / recovery / benchmark evidence

Calibration and validation stack:

- `experiments/`
- parameter boundary discovery
- closure validation
- paper-facing Phase II boundary validation report generation
- future adaptive boundary preparation

Phase III-A boundary preview:

- [SRP Constrained Parameter Optimization Boundary](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_BOUNDARY.md)
- [SRP Constrained Parameter Optimization Protocol](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_PROTOCOL.md)
- [SRP Constrained Parameter Optimization Round 1 Report](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_ROUND_1_REPORT.md)
- [SRP Phase III-A Baseline Comparison Report](SRP_PHASE_III_A_BASELINE_COMPARISON_REPORT.md)
- [SRP Constrained Parameter Optimization Round 1 Analysis](SRP_CONSTRAINED_PARAMETER_OPTIMIZATION_ROUND_1_ANALYSIS.md)
- constrained optimization over validated feasible regions
- not reinforcement learning
- not adaptive execution
- naive full-grid comparison baseline for governed optimization

## State Definition

`SemanticState` is a protocol-layer state object, not a passive memory container.

```text
SemanticState =
    TypedSemanticRepresentation
  + Runtime Metadata
  + Global Verification History
  + Optional Derived State Views
```

`TypedSemanticRepresentation` is the primary state. `Runtime Metadata` and `Global Verification History` track state lifecycle over time. `Derived State Views` include `state_vector`, embedding views, and drift views, but they do not replace object state.

## Operators

SRP is organized around five fixed operators:

1. `parse`: text -> typed semantic objects
2. `compress`: state -> compact runtime package
3. `recover`: package -> recoverable prompt/state
4. `validate`: source vs recovered -> alignment, coverage, drift
5. `observe/update`: validation -> runtime metadata and history update

The current pipeline maps directly onto these operators:

- `parse_semantic_state()` provides typed semantic objects
- `compress_state()` builds the compact runtime package
- `recover_state()` reconstructs the recoverable state view
- `validate_state()` computes alignment, coverage, and drift
- `SemanticState.observe_verification()` updates runtime metadata and global history

## Model Roles

SRP separates the `generation model` from the `semantic evaluator`.

- Generation model: local Qwen or another OpenAI-compatible LLM used for compression and recovery text generation
- Semantic evaluator: rule-based matching, `HashingSemanticEncoder`, optional `E5SmallEncoder`, and related drift / rerank logic

SRP is rule-first and evaluator-optional:

- `rule-only`: object state, runtime metadata, and rule saliency are sufficient for the core protocol
- `encoder-assisted`: embeddings add drift diagnostics and optional reranking
- `judge-assisted`: local LLM judge only adds soft saliency evidence for hard chunk ranking cases

`LLM judge` is only an optional arbitration layer. It is not the base verifier, and judge failure does not block the rule-only SRP path.

## Quick Start

1. Set the local model URL used by the OpenAI-compatible backend:

```bash
setx LOCAL_MODEL_URL http://172.25.253.78:8000
```

2. Run a single SRP pass and export the records:

```bash
python srp_experiment/export_csv.py --cycles 1 --output-csv srp_experiment/tmp/srp_records.csv
```

3. If you want to run tests:

```bash
python -m unittest discover -s srp_experiment/tests -v
```

### Test Layout

The test suite is split into three layers:

- `test_encoder.py`: small, stable unit coverage for encoder and chunking primitives.
- `test_srp_runtime.py`: core runtime coverage for the current SRP pipeline.
- `test_srp_runtime_legacy_compat.py`: legacy compatibility coverage for older `query_expectations` and `expected_keywords` paths.
- `test_longbench_v2_prototype.py`: LongBench v2 prototype coverage for import, task shaping, and group splitting.

This separation keeps the main runtime tests focused while preserving historical compatibility coverage and the LongBench prototype path as explicit, isolated checks.

## Experiment Workflow

Use this order when you start a new measurement-first experiment:

1. Read the next-phase roadmap in [SRP_NEXT_PHASE_TASKS.md](SRP_NEXT_PHASE_TASKS.md)
2. Select the platform closure items from [SRP_EXPERIMENT_CHECKLIST.md](SRP_EXPERIMENT_CHECKLIST.md)
3. Review the policy comparison plan in [SRP_POLICY_EVALUATION_PLAN.md](SRP_POLICY_EVALUATION_PLAN.md)
4. Review unfinished upgrade work in [SRP_REMAINING_TASKS.md](SRP_REMAINING_TASKS.md)
5. Export CSV outputs with `srp_experiment/export_csv.py`

Current documented phase:

- `Semantic Runtime Theory -> Evaluation -> Implementation`

Theory stack:

- [SRP Design Rationale](SRP_DESIGN_RATIONALE.md)
- [SRP Core Assumptions](SRP_CORE_ASSUMPTIONS.md)
- [SRP Theory Map](SRP_THEORY_MAP.md)
- [SRP Semantic State Model](SRP_SEMANTIC_STATE_MODEL.md)
- [SRP Semantic Degradation Model](SRP_SEMANTIC_DEGRADATION_MODEL.md)
- [SRP Preservation Objective Formalization](SRP_PRESERVATION_OBJECTIVE_FORMALIZATION.md)
- [SRP Runtime Representation Design](SRP_RUNTIME_REPRESENTATION_DESIGN.md)
- [SRP Policy Mechanism Design](SRP_POLICY_MECHANISM_DESIGN.md)
- [SRP Runtime Lifecycle Design](SRP_RUNTIME_LIFECYCLE_DESIGN.md)
- [SRP Mechanism Attribution Framework](SRP_MECHANISM_ATTRIBUTION_FRAMEWORK.md)
- [SRP Evaluation Objective Matrix](SRP_EVALUATION_OBJECTIVE_MATRIX.md)

Execution stack:

- platform closure is tracked in `SRP_EXPERIMENT_CHECKLIST.md`
- policy comparison is tracked in `SRP_POLICY_EVALUATION_PLAN.md`
- coverage attribution is tracked in `SRP_COVERAGE_ATTRIBUTION_PLAN.md`
- mechanism attribution protocol is tracked in `SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md`
- runtime representation rationale is tracked in `SRP_RUNTIME_REPRESENTATION_V2_ARCHITECTURE.md`
- runtime representation specification is tracked in `SRP_RUNTIME_REPRESENTATION_V2_SPEC.md`
- remaining upgrade work is tracked in `SRP_REMAINING_TASKS.md`

Recommended sequence:

- route: roadmap -> checklist -> policy plan -> CSV
- keep one `experiment_id` per record
- use the same `task_id` and `context_budget` when comparing ablations
- prefer explicit metric values over prose when you write the records

Field naming rule:

- use the shared underscore-style names from `SRP_NEXT_PHASE_TASKS.md`
- keep `experiment_id`, `task_id`, `config_summary`, `result_summary`, and `metric_values` consistent everywhere
- canonical nested result records now live under `experiment_result` with schema `experiment_result.v1`
- `experiment_result_schema_v1.json` now constrains nested `repair.diagnostics` and `metrics.integrity_retention_metrics` fields, not just top-level section presence
- `lifecycle_attribution` now has schema-level stage and transition summaries for `present / object_count / raw_object_count / recall / precision`
- `lifecycle_attribution` retained/missing/hallucinated object-detail lists are now schema-checked for `object_id / type / value / confidence / evidence_pointer`
- `compressed_size`, `compression_ratio`, `structured_state_package_present`, and `lifecycle_inflation` are now frozen into the canonical record, CSV flatten, and markdown audit

### Experiment ID naming example

Use this pattern:

```text
srp_<phase>_<task>_<ablation>_<run>
```

Examples:

- `srp_meas_longbench_textrec_r01`
- `srp_meas_longbench_structrec_r02`
- `srp_v2_mcq_objaware_r01`
- `srp_paper_repair_r03`

Suggested meanings:

- `<phase>`: `meas`, `v2`, or `paper`
- `<task>`: short task family or dataset id
- `<ablation>`: `textrec`, `structrec`, `objaware`, `repair`, or `encoder`
- `<run>`: `r01`, `r02`, `r03`, etc.

Current status summary:

- completed: measurement infrastructure, recovery source analysis, recovery policy baseline, state-allocation comparison, graph v1 / v1.5 work, semantic extraction audit, SRR v2 prototype, policy Pareto analysis, and the first policy boundary analysis
- completed: policy sensitivity, policy boundary robustness, and policy boundary drift under the current workload family
- active: coverage attribution analysis, stage-wise loss measurement, design rationale, and mechanism attribution / ablation protocol
- pending: paper-ready figures, standardized metric exports, later strong-baseline comparisons, and Graph v2 implementation after rationale is frozen

## Analysis Pyramid

```text
Theory -> State / Degradation / Objectives -> Representation / Policy / Lifecycle -> Attribution / Evaluation -> Implementation
```

The point of this stack is that SRP is not only a memory system; it is also a measurable and explainable runtime semantic analysis framework.

The current theory stack is intentionally compressed. The stable references are the design rationale, core assumptions, theory map, state / degradation / objective documents, representation / policy / lifecycle documents, mechanism attribution framework, and evaluation objective matrix.

Boundary analysis is now considered closed for the current workload family:

- allocation, dependency, and validation boundaries are stable across seeds
- long-horizon drift does not move the current boundary cascade
- dependency-F1 remains workload-sensitive, so it is treated as an adversarial boundary rather than a universal one

The next explanation target is design rationale, followed by mechanism attribution / ablation protocol as an implementation-level consequence of that rationale.

## Export Helpers

The easiest way to export SRP runs to CSV is:

```bash
python srp_experiment/export_csv.py --cycles 1 --output-csv srp_experiment/tmp/srp_records.csv
```

The matching markdown audit export is:

```bash
python srp_experiment/export_markdown.py --cycles 1 --output-markdown srp_experiment/tmp/srp_audit.md
```

For the fixed controlled task harness:

```bash
python srp_experiment/run_controlled_harness.py --suite all --output-dir srp_experiment/tmp/controlled_harness
```

It writes:

- `controlled_harness_records.jsonl`
- `controlled_harness_records.csv`
- `controlled_harness_audit.md`
- `controlled_harness_summary.md`

For the fixed text-vs-structured recovery ablation:

```bash
python srp_experiment/run_recovery_ablation.py --suite all --output-dir srp_experiment/tmp/recovery_ablation
```

It writes:

- `recovery_ablation_records.jsonl`
- `recovery_ablation_records.csv`
- `recovery_ablation_audit.md`
- `recovery_ablation_summary.md`

For the fixed reconstruction policy comparison:

```bash
python srp_experiment/run_reconstruction_policy_comparison.py --suite all --output-dir srp_experiment/tmp/reconstruction_policy
```

It writes:

- `reconstruction_policy_records.jsonl`
- `reconstruction_policy_records.csv`
- `reconstruction_policy_audit.md`
- `reconstruction_policy_summary.md`

For the fixed graph recovery evaluation:

```bash
python srp_experiment/run_graph_recovery_evaluation.py --suite all --output-dir srp_experiment/tmp/graph_recovery_ablation
```

It writes:

- `graph_recovery_ablation_records.jsonl`
- `graph_recovery_ablation_records.csv`
- `graph_recovery_ablation_audit.md`
- `graph_recovery_ablation_summary.md`
- `graph_recovery_ablation.json`

For the fixed object-aware compression ablation:

```bash
python srp_experiment/run_object_aware_compression.py --suite all --output-dir srp_experiment/tmp/object_aware_compression
```

It writes:

- `object_aware_compression_records.jsonl`
- `object_aware_compression_records.csv`
- `object_aware_compression_audit.md`
- `object_aware_compression_summary.md`

The object-aware compression harness now covers three pressure scenarios:

- dependency branching
- subject collision
- budget pressure

It also includes a mechanism verification layer that checks whether object support changes chunk scores and top-k selection before you interpret benchmark outcomes.

For the fixed policy intervention sweep:

```bash
python srp_experiment/run_policy_intervention.py --output-dir srp_experiment/tmp/policy_intervention
```

It writes:

- `policy_intervention_records.jsonl`
- `policy_intervention_records.csv`
- `policy_intervention_audit.md`
- `policy_intervention_summary.md`
- `policy_attribution/`

To analyze the policy design space as a Pareto frontier:

```bash
python srp_experiment/run_policy_pareto_analysis.py --records-jsonl srp_experiment/tmp/policy_intervention/policy_intervention_records.jsonl --output-dir srp_experiment/tmp/policy_pareto
```

It writes:

- `pareto_front.json`
- `pareto_front.md`

The policy sweep is currently interpreted as a Pareto tradeoff between validation coverage, graph integrity, and object retention, rather than as a single-best policy search.

For policy sensitivity analysis:

```bash
python srp_experiment/run_policy_sensitivity.py --output-dir srp_experiment/tmp/policy_sensitivity
```

It writes:

- `policy_sensitivity_records.jsonl`
- `policy_sensitivity_records.csv`
- `policy_sensitivity_audit.md`
- `policy_sensitivity_summary.md`

The first sensitivity run is mostly flat on the current fixed benchmark, which is useful as a baseline for later stronger-pressure tasks.

The next research step after sensitivity is policy boundary analysis, which will introduce memory saturation, long-horizon runtime, tighter active-budget regimes, and dependency-F1 pressure to trigger policy transitions.

For policy boundary analysis:

```bash
python srp_experiment/run_policy_boundary_analysis.py --output-dir srp_experiment/tmp/policy_boundary
```

Use `--preset dependency-fine` to run the tighter sweep that is designed to expose the dependency-F1 boundary. Use `--preset dependency-ultrafine` for the narrow 8-to-12 follow-up scan.

It writes:

- `policy_boundary_records.jsonl`
- `policy_boundary_records.csv`
- `policy_boundary_audit.md`
- `policy_boundary_summary.md`

The first boundary run now shows two complementary effects:

- `memory_saturation` exposes an allocation-layer transition
- `validation_pressure` exposes dependency and validation transitions via `dependency_coverage` and `validation_score`
- `dependency_f1_pressure` exposes a sharper dependency-F1 transition on the fine sweep
- the follow-up `dependency-ultrafine` sweep did not expose a new dependency-F1 boundary inside 8 to 12, which is still useful as a resolution-sensitive negative result

Together they separate allocation sensitivity from downstream dependency and validation sensitivity and make the policy boundary analysis stage more useful for paper-level results.

For policy boundary robustness analysis:

```bash
python srp_experiment/run_policy_boundary_robustness.py --records-jsonl srp_experiment/tmp/policy_boundary_v6/policy_boundary_records.jsonl --output-dir srp_experiment/tmp/policy_boundary_robustness
```

It writes:

- `policy_boundary_robustness.json`
- `policy_boundary_robustness.md`

The first robustness run shows allocation, dependency, and validation boundaries are relatively stable across seeds, while dependency-F1 is the most fragile boundary type and depends strongly on workload construction.

For boundary drift under long-horizon evolution:

```bash
python srp_experiment/run_policy_boundary_drift.py --preset dependency-fine --output-dir srp_experiment/tmp/policy_boundary_drift
```

It writes:

- `policy_boundary_drift.json`
- `policy_boundary_drift.md`

The first long-horizon run over `cycles = 1, 3, 5` shows no measurable midpoint drift for allocation, dependency, or dependency-F1 on the current benchmark family.

For mechanism attribution / ablation protocol:

```bash
python srp_experiment/run_mechanism_attribution_ablation.py --output-dir srp_experiment/tmp/mechanism_attribution_ablation
```

It writes:

- `comparison.json`
- `comparison.md`
- `baseline/records.jsonl`
- `baseline/records.csv`
- `baseline/records.md`
- `remove_importance_weighting/records.jsonl`
- `remove_importance_weighting/records.csv`
- `remove_importance_weighting/records.md`
- `remove_dependency_retention/records.jsonl`
- `remove_dependency_retention/records.csv`
- `remove_dependency_retention/records.md`

The first mechanism-attribution runs should be interpreted as causal comparisons between the dependency-aware baseline, the no-importance ablation, and the no-dependency ablation, with the boundary family frozen. On the current workload family, the no-importance variant is weaker than the no-dependency variant and tends to show more downstream validation effects than allocation-boundary movement. The latest comparison report also includes selection-overlap and importance-composition diagnostics so A1 can be read as a composition shift rather than a pure boundary mover.

Current attribution matrix v1:

- importance weighting -> semantic selection composition and important-item capture
- dependency-aware retention -> dependency structure and dependency-F1 preservation

The graph recovery evaluation harness compares `text`, `structured`, and `graph` recovery modes on a fixed graph-aware Round 1 task set, and records:

- `validation_coverage`
- `dependency_coverage`
- `dependency_precision`
- `dependency_f1`
- `graph_dependency_closure_rate`
- `graph_recovery_precision`
- `graph_repair_cost`

It is the first core Phase VI experiment built on the minimal Semantic Runtime Graph v1.

The matching graph information gap analysis is:

```bash
python srp_experiment/run_graph_information_gap_analysis.py --output-dir srp_experiment/tmp/graph_information_gap_analysis
```

It writes:

- `graph_information_gap_analysis.json`
- `graph_information_gap_analysis.md`

The next representation step is Semantic Runtime Graph v1.5, which keeps graph v1 frozen and adds richer node identity, attributes, state, and lifecycle fields:

- `srp_experiment/schemas/semantic_runtime_graph_schema_v1_5.json`
- `srp_experiment/tests/test_semantic_runtime_graph_v1_5.py`

To run the graph representation ablation:

```bash
python srp_experiment/run_graph_representation_ablation.py --output-dir srp_experiment/tmp/graph_representation_ablation
```

It writes:

- `graph_representation_ablation_records.jsonl`
- `graph_representation_ablation_records.csv`
- `graph_representation_ablation_audit.md`
- `graph_representation_ablation_summary.md`
- `graph_representation_ablation.json`

The first run keeps validation coverage flat on the current tasks, but graph v1.5 improves `attribute_retention`, `state_retention`, `lifecycle_accuracy`, and `graph_integrity_score` relative to graph v1.

To run the semantic extraction audit:

```bash
python srp_experiment/run_semantic_extraction_audit.py
```

It writes:

- `semantic_extraction_audit_records.jsonl`
- `semantic_extraction_audit_records.csv`
- `semantic_extraction_audit.md`
- `semantic_extraction_audit_summary.md`
- `semantic_extraction_audit.json`

The first audit run indicates the remaining gap is provenance / extraction under-specification rather than graph capacity alone.

The Stage 2 threshold analysis is now split into three single-variable research questions:

- RQ2.1 Budget Threshold: vary `top-k budget` only
- RQ2.2 Ambiguity Threshold: vary `keyword overlap` only
- RQ2.3 Support Threshold: vary `object-support strength` only

Decoy count is held fixed inside each RQ so the threshold analysis stays one-dimensional.
The decision-sensitivity metric is `DBI = object_support_gain / decision_margin`.

To run the threshold analysis:

```bash
python srp_experiment/run_object_aware_threshold_analysis.py --output-dir srp_experiment/tmp/object_aware_threshold_analysis
```

It writes:

- `object_aware_threshold_analysis.json`
- `object_aware_threshold_analysis.md`

To run the sampled Stage 2 statistics:

```bash
python srp_experiment/run_object_aware_threshold_sampling.py --output-dir srp_experiment/tmp/object_aware_threshold_sampling
```

It writes:

- `object_aware_threshold_sampling.json`
- `object_aware_threshold_sampling.md`

The sampling runner keeps the Stage 2 structure fixed and reports per-point `flip probability`, `mean`, `std`, and `95% CI`.

Stage 2 is now frozen as a reusable measurement layer.
The next algorithm-facing work is documented in [SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md](SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md).

To build the first failure taxonomy from the current fixed-harness records:

```bash
python srp_experiment/run_semantic_failure_taxonomy.py --output-dir srp_experiment/tmp/semantic_failure_taxonomy
```

It writes:

- `semantic_failure_taxonomy.json`
- `semantic_failure_taxonomy.md`

To run the full fixed harness bundle in one shot:

```bash
python srp_experiment/run_fixed_harnesses.py --harness all --output-dir srp_experiment/tmp/fixed_harnesses
```

It writes one subdirectory per harness plus a manifest:

- `fixed_harness_bundle_manifest.json`
- `controlled/`
- `recovery/`
- `reconstruction/`
- `object_aware_compression/`

### Batch tasks from JSON files

Run multiple task files and merge everything into one CSV:

```bash
python srp_experiment/export_csv.py \
  --task-json srp_experiment/tmp/task_a.json \
  --task-json srp_experiment/tmp/task_b.json \
  --task-id-prefix batch1- \
  --output-csv srp_experiment/tmp/srp_records_batch.csv
```

### Batch tasks from JSONL

For large experiments, provide one task per line:

```bash
python srp_experiment/export_csv.py \
  --input-jsonl srp_experiment/tmp/tasks.jsonl \
  --task-id-prefix expA- \
  --output-csv srp_experiment/tmp/srp_records_jsonl.csv
```

## Batch Experiment Template

Use this template when you want to run a larger batch and keep the output easy to analyze:

```bash
python srp_experiment/export_csv.py \
  --input-jsonl srp_experiment/data/your_experiment/tasks.jsonl \
  --task-id-prefix your_experiment- \
  --cycles 2 \
  --output-csv srp_experiment/tmp/your_experiment_records.csv
```

Recommended inputs:

- One task per line in JSONL
- Each task includes `id`, `initial_state`, `query_expectations`, and `expected_keywords`
- Use `--task-id-prefix` to keep batch provenance visible in the CSV

## Standard `tasks.jsonl` Example

Each line is one task object:

```jsonl
{"id":"task-001","initial_state":{"constraints":["Preserve the key constraint."],"memory":"Preserve the key constraint and keep the answer concise."},"query_expectations":[[["Preserve the key constraint."]]],"expected_keywords":["constraint","concise"]}
{"id":"task-002","initial_state":{"constraints":["Keep the summary faithful."],"memory":"Keep the summary faithful while allowing minor paraphrase."},"query_expectations":[[["Keep the summary faithful."]]],"expected_keywords":["summary","faithful"]}
{"id":"task-003","initial_state":{"constraints":["Do not introduce unsupported facts."],"memory":"Do not introduce unsupported facts when compressing context."},"query_expectations":[[["Do not introduce unsupported facts."]]],"expected_keywords":["facts","compressing"]}
```

Save it as `srp_experiment/data/your_experiment/tasks.jsonl`, then run:

```bash
python srp_experiment/export_csv.py \
  --input-jsonl srp_experiment/data/your_experiment/tasks.jsonl \
  --task-id-prefix your_experiment- \
  --cycles 2 \
  --output-csv srp_experiment/tmp/your_experiment_records.csv
```

## Common Checks

After exporting, inspect these fields first:

- `task_id`
- `task_source`
- `experiment_result_schema_version`
- `experiment_result_validation_passed`
- `experiment_result_lifecycle_attribution_source_object_count`
- `experiment_result_lifecycle_attribution_transitions_source_to_compressed_recall`
- `experiment_result_lifecycle_attribution_transitions_recovered_to_allocated_recall`
- `experiment_result_lifecycle_attribution_lifecycle_inflation`
- `experiment_result_metrics_integrity_gap`
- `experiment_result_metrics_semantic_compression_loss`
- `experiment_result_metrics_weighted_object_retention`
- `experiment_result_metrics_lost_important_object_count`
- `experiment_result_metrics_structured_state_package_present`
- `experiment_result_metrics_compressed_size`
- `experiment_result_metrics_compression_ratio`
- `repair_diagnostics_coverage_before_repair`
- `repair_diagnostics_coverage_after_repair`
- `repair_diagnostics_repair_gain`
- `repair_diagnostics_critical_failures_before`
- `repair_diagnostics_critical_failures_after`
- `experiment_result_metrics_state_committed`
- `runtime_round`
- `runtime_history_length`
- `semantic_drift`
- `semantic_stability`
- `validation_passed`
- `critical_failures`
- `failure_summary_flat_*`
- `lifecycle_summary_flat_*`
- `object_update_summary_flat_*`
- `repair_context_flat_*`
- `policy_flat_*`

## Output

The exporter flattens the nested lifecycle and policy summaries into CSV-friendly columns.
It preserves:

- `task_id`
- `task_source`
- `experiment_result`
- `experiment_result.lifecycle_attribution`
- `experiment_result.metrics.integrity_retention_metrics`
- `experiment_result.repair.diagnostics`
- `lifecycle_summary_flat`
- `object_update_summary_flat`
- `policy_flat`
- `runtime` and `validation` fields from `run_srp()`

## Markdown Audit

The markdown audit exporter renders directly from `experiment_result.v1`.
It summarizes:

- core validation and integrity metrics
- compression footprint and reconstruction availability
- repair diagnostics
- lifecycle stage counts
- lifecycle transition recall and precision
- retained / missing / hallucinated object-detail tables for key lifecycle transitions

## Semantic Runtime Graph v1

SRP now also emits a minimal semantic runtime graph alongside the object-lifecycle view.
The graph is intentionally small:

- nodes
- edges
- lifecycle
- validation

Schema:

- `srp_experiment/schemas/semantic_runtime_graph_schema_v1.json`

## Recovery Modes

The recovery layer supports a mode switch through `SRP_RECOVERY_MODE`:

- `reconstruction` or unset: legacy reconstruction path
- `text`: text recovery
- `structured`: structured recovery
- `graph`: deterministic graph-aware recovery

## Notes

- `lifecycle_summary_flat` is designed for CSV and ablation.
- `object_update_summary_flat` keeps object-level lifecycle updates visible in the same table.
- `policy_flat` keeps lifecycle thresholds visible in the same table.
- `integrity_gap` measures final validation coverage loss as `1 - validation_coverage`.
- `semantic_compression_loss` measures compression-stage object loss as `1 - source_to_compressed_recall`.
- `compressed_size` is the whitespace-tokenized size of compressed memory.
- `compression_ratio` is `compressed_size / source_size`.
- `structured_state_package_present` indicates whether recovery produced a structured state package for downstream allocation and execution.
- `lifecycle_inflation` is the peak lifecycle stage object-count ratio relative to the source stage.
- `repair_gain` measures `coverage_after_repair - coverage_before_repair`.
- `token_overhead` measures repair-stage total token delta relative to the pre-repair run.
- The controlled harness runs three fixed suites: `structured_recovery`, `object_retention`, and `repair_loop`.
- The controlled harness summary table reports `important_recall`, `task_critical_recall`, and `token_overhead` per suite.
- The recovery ablation summary table reports `validation_coverage`, `important_recall`, `task_critical_recall`, `recovered_object_count`, `hallucinated_count`, and `object_inflation_ratio` per suite.
- The reconstruction policy summary table reports `validation_coverage`, `recovered_object_count`, `hallucinated_count`, `reconstruction_precision`, `reconstruction_selectivity`, and `minimality_score` per suite.
- The object-aware compression summary table reports `validation_coverage`, `weighted_object_retention`, `lost_important_object_count`, and `critical_failures_before` per suite.
- `SRP_OBJECT_SUPPORT_ENABLED` toggles object-aware chunk ranking inside `compress_state()`.
- The object-aware compression harness now runs each scenario twice, once with chunk scoring only and once with chunk scoring plus object support.
- The object-aware compression summary also reports mechanism verification metrics such as score changes, top-k changes, and object-support gain.
- The object-aware compression summary also reports decision boundary metrics such as the first changed Top-k, decision margins, and gain-to-margin ratios.
- The object-aware threshold analysis splits Stage 2 into `RQ2.1 Budget Threshold`, `RQ2.2 Ambiguity Threshold`, and `RQ2.3 Support Threshold`.
- The threshold analysis summary also reports `DBI = object_support_gain / decision_margin` and keeps decoy count fixed within each RQ.
- The fixed harness bundle runs `controlled`, `recovery`, `reconstruction`, and `object_aware_compression` with one command and writes a manifest plus per-harness subdirectories.
- The exporter accepts either task JSON, task directories, or JSONL streams.
