# SRP Theory Map

One-page view of the SRP theory stack. Not an implementation spec.

Frozen theory version: `v1.0`

For system-level architecture, see [SRP Semantic Evolution Architecture](SRP_SEMANTIC_EVOLUTION_ARCHITECTURE.md).

## Parameter Calibration Layer

```text
Parameter Space Model
        |
        v
Parameter Registry
        |
        v
Sensitivity Experiments
        |
        v
Validated Baseline Report
        |
        v
Parameter Interaction Analysis
        |
        v
Phase I Calibration Closure
        |
        v
Phase II Constrained Calibration Boundary
        |
        v
Calibration Round Result Model
        |
        v
Acceptable Region Evidence
        |
        v
Phase II Closure Validation Suite
        |
        v
Boundary Validation Report
        |
        v
Future Adaptive Semantic Evolution
```

Status: Frozen

Scope:

- parameter observability
- boundary validation
- constrained calibration boundary
- calibration result modeling

Non-goals:

- parameter optimization
- adaptive policy learning
- runtime self-modification

Phase I calibration links the validated baseline studies and the first interaction observation into one frozen research layer.
The Phase I Observability Report captures the paper-facing data package for parameter observability before boundary validation.
The Phase I observability export package provides repeated transition observations, parameter statistics, and a markdown summary for the observability layer.
Phase II defines the constrained evaluation boundary for future calibration work without entering optimization or adaptive execution.
Calibration Round Result Model freezes how acceptable-region evidence is recorded across calibration rounds.
Phase II Closure Validation Suite verifies the frozen Phase II regions under controlled runtime variations without creating new boundaries.
The Phase II Closure Validation Report consolidates the closure evidence package for the research baseline.
The Phase II Validation Appendix provides the auditable records behind the closure evidence package.
The Phase II Boundary Validation Report packages the paper-facing boundary evidence for Phase II.
The Phase II boundary export package provides `candidate_results.csv` and `feasible_region.json` for the optimization handoff.
The Phase II figure export package provides `feasible_heatmap` and `coverage_summary` plots for the paper.
The Phase II Density Baseline Report compares coarse, standard, and dense grids to check whether the feasible region is stable across sampling density.
The Phase II density baseline export package provides `density_results.csv`, `density_summary.json`, and `density_coverage` plots for baseline analysis.
The Phase II Boundary Generalization Report compares feasible-region overlap across coarse, standard, and dense grids and records IoU against the reference grid.
The Phase II boundary generalization export package provides `generalization_results.csv`, `generalization_summary.json`, and `boundary_iou_heatmap` plots for overlap analysis.
The Phase III-A Baseline Comparison Report contrasts the constrained optimization path against a naive full-grid sweep and records search reduction plus top-match behavior.
The Phase III-A Objective Sensitivity Report compares rankings under multiple objective-weight settings and records Top-k overlap plus rank correlations.
The Experiment Environment Freeze captures the reproducibility assumptions used by the current experiment baseline.

The legacy measurement stack under `srp_experiment/` remains a maintained background layer for runtime feasibility and benchmark evidence.
It does not replace the calibration / validation stack under `experiments/`.
Phase-scoped experiment configs live under `configs/`, and `experiments/config.py` provides the typed loader for the phase-specific research settings.

```text
Phase III-A Constrained Parameter Optimization Boundary
        |
        v
Constrained Parameter Optimization Protocol
        |
        v
Optimization Report
        |
        v
Optimization Analysis
        |
        v
Baseline Comparison Report
        |
        v
Objective Sensitivity Report
        |
        v
Governance Review
        |
        v
Future Adaptive Semantic Evolution
```

Semantic backend comparison study:

```text
Semantic Backend Comparison Protocol
        |
        v
Semantic Backend Comparison Report
        |
        v
Evidence Source Augmentation Analysis
        |
        v
Evidence Escalation Analysis
        |
        v
Evidence Escalation Appendix
```

This study is parallel to Phase III-A. It compares evidence sources without changing the parameter optimization boundary.
The evidence escalation protocol defines when vector evidence should remain sufficient and when stronger semantic evidence should be consulted.
The evidence escalation appendix provides the auditable records behind the escalation routing policy.
The result package under `experiments/results/semantic_backend_comparison/` captures the paper-facing comparison data, summary, and figure export.

Research freeze package:

```text
SRP Research Freeze V1
```

This freeze package captures the current research baseline across runtime, calibration, validation, optimization, and evidence studies.

Paper construction:

```text
SRP Paper Structure V1
        |
        v
SRP Contribution Map V1
        |
        v
SRP Abstract V1
        |
        v
SRP Introduction V1
        |
        v
SRP Related Work V1
        |
        v
SRP System Model V1
        |
        v
SRP Method Overview V1
        |
        v
SRP Experiments Overview V1
        |
        v
SRP Discussion V1
        |
        v
SRP Experiments V1
```

This paper structure document turns the frozen baseline into a publication-ready outline and claim map.
The contribution map freezes the paper's core claims and narrative coordinate system.
The abstract freezes the paper's external-facing summary without reopening the research baseline.
The introduction converts the abstract into a problem-gaps-insight-contributions narrative.
The related work section positions SRP against retrieval, memory, agents, RL, and controlled systems without collapsing SRP into any of them.
The system model provides the paper's technical core: authority separation, semantic transition flow, and phase formalization.
The method overview turns the system model into the paper's executable phase structure.
The experiments overview maps the method claims to the evidence package without reopening the research baseline.
The discussion explains why the frozen boundaries, constrained optimization, and evidence escalation matter as a governance-first semantic evolution framework.
The experiments section turns the overview into the paper's concrete experimental claims and results.
The main results summary condenses the frozen evidence chain into a compact claim-to-result table for the abstract, conclusion, and results overview.
The ablation plan freezes the paper-facing causality story by testing which separations break when boundary validation, evidence escalation, or governance is removed.
The parameter recommendation policy freezes how Phase III-A recommendations should be interpreted so they are not mistaken for runtime default updates.
The parameter recommendation analysis freezes how a recommended configuration should be interpreted under the evaluated objective without turning it into a default update.
The limitations document freezes the paper's claim boundary so the conclusion stays within the evaluated workload, objective, evidence, and governance assumptions.
The conclusion document freezes the final claim synthesis so the paper can close without reopening the research baseline.
The paper draft turns the frozen artifacts into a manuscript skeleton and claim-to-evidence matrix.
The paper draft V2 compresses the opening manuscript into prose for the abstract, introduction, and framework sections.
The paper draft V2 also compresses the experiment chain into RQ-linked evidence prose for the experiments section.
The paper draft V3 compresses the analysis, ablation, discussion, limitations, and conclusion into the manuscript closing sections.
The paper final draft merges the manuscript into a single posting-oriented artifact with terminology and claim-strength normalization.
The Phase V retention/drift evaluation freezes the next preservation-focused research boundary without turning it into a runtime update policy.
The Phase V retention/drift baseline implementation lives in `experiments/evaluation/phase_v_retention/` and writes the paper-facing result package under `experiments/results/phase_v_retention/`.
The Phase V retention sensitivity plan freezes the next paper-facing follow-on study so relation preservation, evidence preservation, recovery strictness, and activation gating can be analyzed separately without collapsing them into a single optimization target.
The Phase VI relation-aware recovery design freezes the next reconstruction-focused boundary so SRP can recover semantic neighborhoods through anchor expansion and closure validation rather than isolated unit retrieval.
The Phase VI relation-aware recovery plan freezes the minimal verification boundary for three recovery variants so relation-aware recovery can be tested without turning Phase VI into a full graph benchmark.
The Phase VI relation-aware recovery implementation lives in `experiments/evaluation/phase_vi_relation_recovery/` and is intended to produce a paper-facing result package under `experiments/results/phase_vi_relation_recovery/` once the MVP experiment is run.
The Phase VI relation-aware recovery report freezes the first MVP result package so the relation-aware recovery baseline can be read alongside Phase V retention as the next reconstruction-focused evidence layer.
The Phase VI relation-aware recovery result package now lives in `experiments/results/phase_vi_relation_recovery/` and records the first MVP comparison between vector-only, relation expansion, and relation closure.
The Phase VII parameter sensitivity and stability plan freezes the next parameter-analysis boundary so recommendation variance and reconstruction variance can be measured separately from the recovery-mode comparison.
The Phase VII parameter sensitivity and stability report freezes the first seed-stability result package so governed recommendations can be shown stable under repeated evaluation with the same workload, objective, and evidence backend.
The Phase VII-B parameter sensitivity and governance tradeoff plan freezes the next governance-analysis boundary so archive retention, evidence preservation, relation depth, and activation gating can be analyzed separately from the stability study.
The Phase VII-B parameter sensitivity and governance tradeoff report freezes the first sensitivity result package so SRP parameter behavior can be read as a tradeoff surface rather than a single best configuration.
The Phase VII-B parameter sensitivity result package lives in `experiments/results/phase_vii_parameter_sensitivity/` and records the first one-factor sweep across archive retention, evidence preservation, relation depth, and activation threshold.
The Phase VIII cross-domain validation plan freezes the next generality boundary so SRP can be tested across code evolution memory, knowledge reasoning, and agent planning workloads without changing the governance core.
The Phase VIII cross-domain validation result package now lives in `experiments/results/phase_viii_cross_domain/` and records the first cross-domain MVP comparison across code memory, knowledge reasoning, and agent planning workloads.
The Phase VIII-B representation invariance plan freezes the next representation boundary so SRP can be tested across encoders and parsers without changing the governance core.
The Phase VIII-B representation invariance result package now lives in `experiments/results/phase_viii_representation_invariance/` and records the encoder/parser MVP across four encoders and three parsers.
Its primary summary criteria are hierarchy consistency rate and governance consistency rate.
The Phase VIII-C implementation independence plan freezes the backend boundary so SRP can be tested across storage implementations without changing the governance core.
The Phase VIII-C implementation independence result package now lives in `experiments/results/phase_viii_implementation_independence/` and records the backend MVP across flat, graph, and vector-overlay stores.
The External Validation Plan freezes the public-benchmark boundary so SRP can be compared against established memory and retrieval baselines under externally recognized workloads.
The External Validation Implementation Plan freezes the adapter and evaluation contract for the public benchmark suite so benchmarks can enter SRP without changing the governance core.
The External Validation Baseline Capability Matrix freezes the comparison contract for retrieval, relation, temporal, update, and governance capabilities across baseline families.
The external-validation LoCoMo ingestion slice now lives in `experiments/results/external_validation_locomo_mvp/` and is treated as an adapter calibration artifact rather than a paper result.
The calibration-aware LoCoMo rerun now lives in `experiments/results/external_validation_locomo_calibration_aware/` and separates official benchmark score, semantic diagnostics, attribution distribution, and promotion gate.
The LoCoMo manual sanity calibration slice now lives in `experiments/results/external_validation_locomo_sanity/` and is used to inspect adapter-level behavior before any external-validity claim is promoted.
The paper-facing LoCoMo calibration note now lives in `SRP_LOCOMO_CALIBRATION_NOTE.md` and summarizes the calibration boundary for the appendix or evaluation methodology section.
The LongMemEval calibration-aware rerun now lives in `experiments/results/external_validation_longmemeval_calibration_aware/` and serves as the next external-validity calibration checkpoint.
The LongMemEval calibration note now lives in `SRP_LONGMEMEVAL_CALIBRATION_NOTE.md` and marks the next external-validity calibration checkpoint.
The LongMemEval evidence contract now lives in `configs/external_validation_longmemeval_evidence.env` and freezes the shared local-vLLM generation backend across baselines and SRP.
The LongMemEval evidence-run entrypoint now lives in `experiments/evaluation/run_longmemeval_evidence.py` and produces the first shared-generation evidence bundle when promoted.
The LongMemEval evidence run now lives in `experiments/results/external_validation_longmemeval_evidence/` and records the first external-validity evidence slice under the frozen runtime manifest.
The LongMemEval evidence audit note now lives in `SRP_LONGMEMEVAL_EVIDENCE_AUDIT_NOTE.md` and keeps the promotion gate explicit.
The evidence audit specification now lives in `SRP_EVIDENCE_AUDIT_SPECIFICATION_V1.md` and freezes the runtime reproducibility, scorer correctness, metric correctness, and promotion gates for future evidence runs.
The LongMemEval scorer alignment audit now lives in `SRP_LONGMEMEVAL_SCORER_ALIGNMENT_AUDIT.md` and freezes the final scorer-promotion gate.
That slice now includes answer-attribution traces and a scoring calibration matrix so adapter, recovered state, and scorer behavior can be audited case by case.
The corresponding calibration note lives in `SRP_EXTERNAL_VALIDATION_ADAPTER_CALIBRATION_NOTE.md`.
The Research Freeze Policy freezes the current SRP theory boundary and defines when evidence is strong enough to justify revising core claims.
The SRP Paper Completion Checklist tracks what remains before the paper is publication-ready.

```text
Long-running Semantic Runtime
        |
        v
Semantic Degradation
        |
        v
Semantic State
        |
        v
Preservation Objectives
        |
        v
Runtime Representation
        |
        v
Semantic Evolution Framework
        |
        v
Runtime Object Model
        |
        v
Semantic Unit Model
        |
        v
Semantic Unit Field Spec
        |
        v
Semantic Graph Model
        |
        v
Semantic Constraint System
        |
        v
Semantic Graph Algorithms
        |
        v
Semantic Operator Algebra
        |
        v
Semantic Versioning Model
        |
        v
Formal Semantics
        |
        v
Semantic Metric Space
        |
        v
Runtime Semantics
        |
        v
Semantic Time Model
        |
        v
Semantic Lifecycle Model
        |
        v
State Compaction Model
        |
        v
Archive Representation Model
        |
        v
Archive Index Model
        |
        v
Archive Query Model
        |
        +----------------+
        |                |
        v                v
Recovery          Audit / Analysis
        |
        v
Archive Query Service Spec
        |
        v
Minimal Runtime Kernel
        |
        v
Runtime Data Contract
        |
        v
Runtime Event Contract
        |
        v
Runtime Event Interface
        |
        v
Runtime Event Processing Model
        |
        v
Runtime Kernel Target
        |
        v
Runtime Kernel Interface
        |
        v
Runtime Kernel API Map
        |
        v
Runtime Kernel Adapter Plan
        |
        v
Runtime Kernel Migration Checklist
        |
        v
Kernel Callsite Map
        |
        v
Runtime Kernel Phase Migration Map
        |
        v
Semantic Evolution Trace Model
        |
        v
Semantic Evolution Trace Spec
        |
        v
Replay Spec
        |
        v
Runtime Recording Layer Alignment
        |
        v
Runtime Component Interface Spec
        |
        v
Minimal Runtime Kernel Reference Plan
        |
        v
Runtime Kernel Milestone 1 Interface Spec
        |
        v
Runtime Kernel Class File Map
        |
        v
Runtime Kernel Milestone 2 Plan
        |
        v
Runtime Kernel Milestone 2 Implementation Checklist
        |
        v
Runtime Kernel Milestone 2 Reference Interface Spec
        |
        v
Runtime Kernel Milestone 2 Integration Validation
        |
        v
Runtime Kernel Milestone 2 Branching Validation
        |
        v
Version Conflict Model
        |
        v
Version Conflict Validation
        |
        v
Version Conflict Query Model
        |
        v
Conflict Archive Evidence Adapter Model
        |
        v
Version Resolution Decision Model
        |
        v
Runtime Governance Model
        |
        v
Runtime Kernel Milestone 2 Paper Summary
        |
        v
Runtime Kernel Milestone 2 Landing
        |
        v
Runtime Kernel Milestone 2 Final State
        |
        v
Runtime Kernel Milestone 2 Overview
        |
        v
Runtime Kernel Milestone 2 Status Summary
        |
        v
Runtime Kernel Milestone 3 Boundary Preview
        |
        v
Runtime Kernel Freeze Checklist
        |
        v
Runtime Decision Boundary Model
        |
        v
Semantic Commit Model
        |
        v
Runtime Checkpoint Model
        |
        v
Semantic Evolution Rules
        |
        v
Policy Mechanisms
        |
        v
Runtime Lifecycle
        |
        v
Evaluation + Attribution
        |
        v
Implementation Choice
```

| Layer | Core documents | Question answered |
| --- | --- | --- |
| Problem | [Design Rationale](SRP_DESIGN_RATIONALE.md), [Semantic Degradation Model](SRP_SEMANTIC_DEGRADATION_MODEL.md) | What goes wrong? |
| State | [Semantic State Model](SRP_SEMANTIC_STATE_MODEL.md) | What state evolves? |
| Objectives | [Preservation Objective Formalization](SRP_PRESERVATION_OBJECTIVE_FORMALIZATION.md) | What should be preserved? |
| Representation | [Runtime Representation Design](SRP_RUNTIME_REPRESENTATION_DESIGN.md) | What must be stored? |
| Semantic Evolution | [Semantic Evolution Framework](SRP_SEMANTIC_MEMORY_MAINTENANCE.md) | How does semantic state evolve over time? |
| Object Model | [Runtime Object Model](SRP_RUNTIME_OBJECT_MODEL.md) | What runtime objects exist and who may modify them? |
| Semantic Unit | [Semantic Unit Model](SRP_SEMANTIC_UNIT_MODEL.md) | What is the atomic semantic unit? |
| Semantic Unit Fields | [Semantic Unit Field Specification](SRP_SEMANTIC_UNIT_FIELD_SPEC.md) | What does each unit field mean and who owns it? |
| Semantic Graph Model | [Semantic Graph Model](SRP_SEMANTIC_GRAPH_MODEL.md) | What is the structural graph over semantic units, relations, and paths? |
| Semantic Constraint System | [Semantic Constraint System](SRP_SEMANTIC_CONSTRAINT_SYSTEM.md) | What must never happen across identity, structure, semantics, evolution, and runtime? |
| Semantic Graph Algorithms | [Semantic Graph Algorithms](SRP_SEMANTIC_GRAPH_ALGORITHMS.md) | What graph transformation operators change semantic graphs? |
| Semantic Operator Algebra | [Semantic Operator Algebra](SRP_SEMANTIC_OPERATOR_ALGEBRA.md) | How do semantic graph operators compose, commute, and preserve meaning? |
| Semantic Versioning Model | [Semantic Versioning Model](SRP_SEMANTIC_VERSIONING_MODEL.md) | How do semantic versions branch, merge, rollback, and relate to replay? |
| Formal Semantics | [Formal Semantics](SRP_FORMAL_SEMANTICS.md) | What are the precise mathematical objects and transition laws used by SRP? |
| Semantic Metric Space | [Semantic Metric Space](SRP_SEMANTIC_METRIC_SPACE.md) | How will semantic distances and similarities be defined? |
| Runtime Semantics | [Runtime Semantics](SRP_RUNTIME_SEMANTICS.md) | How does SRP execute legal transitions over time? |
| Semantic Time Model | [Semantic Time Model](SRP_SEMANTIC_TIME_MODEL.md) | How does SRP measure semantic age, drift time, and version time? |
| Semantic Lifecycle Model | [Semantic Lifecycle Model](SRP_SEMANTIC_LIFECYCLE_MODEL.md) | Which lifecycle states are legal, terminal, or reversible? |
| State Compaction Model | [State Compaction Model](SRP_STATE_COMPACTION_MODEL.md) | How is retained archive storage reorganized without changing meaning? |
| Archive Representation Model | [Archive Representation Model](SRP_ARCHIVE_REPRESENTATION_MODEL.md) | What does retained archive storage keep, and how are references indexed? |
| Archive Index Model | [Archive Index Model](SRP_ARCHIVE_INDEX_MODEL.md) | How are retained archive references addressed, validated, and queried? |
| Archive Query Model | [Archive Query Model](SRP_ARCHIVE_QUERY_MODEL.md) | How does SRP ask the archive for evidence without reconstructing state directly? |
| Archive Query Service Spec | [Archive Query Service Spec](SRP_ARCHIVE_QUERY_SERVICE_SPEC.md) | What is the runtime-facing service contract for archive evidence lookup and verification? |
| Minimal Runtime Kernel | [Minimal Runtime Kernel](SRP_MINIMAL_RUNTIME_KERNEL.md) | What are the smallest runtime primitives and operational semantics? |
| Data Contract | [Runtime Data Contract](SRP_RUNTIME_DATA_CONTRACT.md) | What do fields mean, who updates them, and what invariants hold? |
| Event Contract | [Runtime Event Contract](SRP_RUNTIME_EVENT_CONTRACT.md) | What counts as a legal semantic transition? |
| Event Interface | [Runtime Event Interface](SRP_RUNTIME_EVENT_INTERFACE.md) | How are events created, applied, and replayed? |
| Event Processing | [Runtime Event Processing Model](SRP_RUNTIME_EVENT_PROCESSING_MODEL.md) | Who produces, validates, and applies events? |
| Kernel Target | [Runtime Kernel Target](SRP_RUNTIME_KERNEL_TARGET.md) | What is the target execution boundary for semantic state transitions? |
| Kernel Interface | [Runtime Kernel Interface](SRP_RUNTIME_KERNEL_INTERFACE.md) | How does the kernel expose validated submission, application, query, and replay? |
| Kernel API Map | [Runtime Kernel API Map](SRP_RUNTIME_KERNEL_API_MAP.md) | How does the current implementation map to the future kernel API boundary? |
| Kernel Adapter Plan | [Runtime Kernel Adapter Plan](SRP_RUNTIME_KERNEL_ADAPTER_PLAN.md) | How do we migrate from the experimental runtime to the future kernel without breaking evidence? |
| Kernel Migration Checklist | [Runtime Kernel Migration Checklist](SRP_RUNTIME_KERNEL_MIGRATION_CHECKLIST.md) | What must be true before each migration phase may advance? |
| Kernel Callsite Map | [Kernel Callsite Map](SRP_KERNEL_CALLSITE_MAP.md) | Which current callsites map to future kernel boundaries? |
| Kernel Phase Migration Map | [Runtime Kernel Phase Migration Map](SRP_RUNTIME_KERNEL_PHASE_MIGRATION_MAP.md) | Which state transitions should be controlled first in each migration phase? |
| Semantic Evolution Trace Model | [Semantic Evolution Trace Model](SRP_SEMANTIC_EVOLUTION_TRACE_MODEL.md) | How does a semantic unit evolve causally over time? |
| Semantic Evolution Trace Spec | [Semantic Evolution Trace Spec](SRP_SEMANTIC_EVOLUTION_TRACE_SPEC.md) | How is the evolution trace engineered as a queryable causal structure? |
| Replay Spec | [Replay Spec](SRP_REPLAY_SPEC.md) | How is semantic state deterministically reconstructed from event history? |
| Runtime Recording Layer Alignment | [Runtime Recording Layer Alignment](SRP_RUNTIME_RECORDING_LAYER_ALIGNMENT.md) | Which current modules will own event records, trace artifacts, and replay snapshots? |
| Runtime Component Interface Spec | [Runtime Component Interface Spec](SRP_RUNTIME_COMPONENT_INTERFACE_SPEC.md) | What are the minimal executable interfaces for RuntimeEvent, TraceBuilder, and ReplayEngine? |
| Minimal Runtime Kernel Reference Plan | [Minimal Runtime Kernel Reference Plan](SRP_MINIMAL_RUNTIME_KERNEL_REFERENCE_PLAN.md) | What is the smallest standalone reference package boundary for the minimal runtime kernel? |
| Runtime Kernel Milestone 1 Interface Spec | [Runtime Kernel Milestone 1 Interface Spec](SRP_RUNTIME_KERNEL_MILESTONE_1_INTERFACE_SPEC.md) | What are the first frozen Python interfaces for the minimal runtime reference implementation? |
| Runtime Kernel Class File Map | [Runtime Kernel Class File Map](SRP_RUNTIME_KERNEL_CLASS_FILE_MAP.md) | How do the reference implementation classes map to Python modules without circular dependencies? |
| Runtime Kernel Milestone 2 Plan | [Runtime Kernel Milestone 2 Plan](SRP_RUNTIME_KERNEL_MILESTONE_2_PLAN.md) | What are the next kernel-stage contracts for decision boundaries, semantic commits, and checkpoints? |
| Runtime Kernel Milestone 2 Implementation Checklist | [Runtime Kernel Milestone 2 Implementation Checklist](SRP_RUNTIME_KERNEL_MILESTONE_2_IMPLEMENTATION_CHECKLIST.md) | What is the implementation boundary before the Milestone 2 reference interface is written? |
| Runtime Kernel Milestone 2 Reference Interface Spec | [Runtime Kernel Milestone 2 Reference Interface Spec](SRP_RUNTIME_KERNEL_MILESTONE_2_REFERENCE_INTERFACE_SPEC.md) | What are the first Milestone 2 reference contracts for decision, commit, version, and checkpoint? |
| Runtime Kernel Milestone 2 Integration Validation | [Runtime Kernel Milestone 2 Integration Validation](SRP_RUNTIME_KERNEL_MILESTONE_2_INTEGRATION_VALIDATION.md) | Which Milestone 2 invariants are already validated by integration tests? |
| Runtime Kernel Milestone 2 Branching Validation | [Runtime Kernel Milestone 2 Branching Validation](SRP_RUNTIME_KERNEL_MILESTONE_2_BRANCHING_VALIDATION.md) | Which non-linear semantic history invariants are already validated by branching tests? |
| Version Conflict Model | [Version Conflict Model](SRP_VERSION_CONFLICT_MODEL.md) | How does SRP represent branch disagreement without rewriting semantic history? |
| Version Conflict Validation | [Version Conflict Validation](SRP_VERSION_CONFLICT_VALIDATION.md) | Which branch-disagreement invariants are already validated without introducing automatic resolution? |
| Version Conflict Query Model | [Version Conflict Query Model](SRP_VERSION_CONFLICT_QUERY_MODEL.md) | How does SRP ask for conflict evidence without turning the query layer into a resolution engine? |
| Conflict Archive Evidence Adapter Model | [Conflict Archive Evidence Adapter Model](SRP_CONFLICT_ARCHIVE_EVIDENCE_ADAPTER_MODEL.md) | How does SRP enrich conflict evidence through the archive boundary without exposing ArchiveStore directly? |
| Version Resolution Decision Model | [Version Resolution Decision Model](SRP_VERSION_RESOLUTION_DECISION_MODEL.md) | How does SRP convert verified conflict evidence into a bounded future semantic intent without mutating history? |
| Runtime Governance Model | [Runtime Governance Model](SRP_RUNTIME_GOVERNANCE_MODEL.md) | How does SRP separate execution, history, and governance authority in a version-aware semantic runtime? |
| Runtime Kernel Milestone 2 Paper Summary | [Runtime Kernel Milestone 2: Governed Semantic Evolution Runtime](SRP_RUNTIME_KERNEL_MILESTONE_2_PAPER_SUMMARY.md) | What is the paper-style one-page summary of the verified Milestone 2 runtime? |
| Runtime Kernel Milestone 2 Landing | [Runtime Kernel Milestone 2](SRP_RUNTIME_KERNEL_MILESTONE_2_LANDING.md) | What is the concise landing page for the verified Milestone 2 runtime? |
| Runtime Kernel Milestone 2 Final State | [Runtime Kernel Milestone 2 Final State](SRP_RUNTIME_KERNEL_MILESTONE_2_FINAL_STATE.md) | What is the final verified Milestone 2 boundary snapshot? |
| Runtime Kernel Milestone 2 Overview | [Runtime Kernel Milestone 2 Overview](SRP_RUNTIME_KERNEL_MILESTONE_2_OVERVIEW.md) | What is the short, citation-friendly summary of the verified Milestone 2 runtime? |
| Runtime Kernel Milestone 2 Status Summary | [Runtime Kernel Milestone 2 Status Summary](SRP_RUNTIME_KERNEL_MILESTONE_2_STATUS_SUMMARY.md) | What runtime and evidence boundaries are currently confirmed for Milestone 2? |
| Runtime Kernel Milestone 3 Boundary Preview | [Runtime Kernel Milestone 3: Adaptive Semantic Evolution Boundary](SRP_RUNTIME_KERNEL_MILESTONE_3_BOUNDARY_PREVIEW.md) | What research boundary is frozen for adaptive semantic evolution after Milestone 2? |
| Runtime Kernel Freeze Checklist | [Runtime Kernel Freeze Checklist](SRP_RUNTIME_KERNEL_FREEZE_CHECKLIST.md) | What boundary checks should be applied before extending SRP further? |
| Runtime Decision Boundary Model | [Runtime Decision Boundary Model](SRP_RUNTIME_DECISION_BOUNDARY_MODEL.md) | How does SRP choose, reject, and explain operator selection before transition execution? |
| Semantic Commit Model | [Semantic Commit Model](SRP_SEMANTIC_COMMIT_MODEL.md) | When does a transition become part of the accepted semantic history and version DAG? |
| Runtime Checkpoint Model | [Runtime Checkpoint Model](SRP_RUNTIME_CHECKPOINT_MODEL.md) | How does SRP anchor replay efficiently without turning checkpoints into semantic history? |
| Evolution Rules | [Semantic Evolution Rules](SRP_SEMANTIC_EVOLUTION_RULES.md) | Under what conditions should transitions happen? |
| Rule Table | [Semantic Evolution Rule Table](SRP_SEMANTIC_EVOLUTION_RULE_TABLE.md) | What is the decision boundary for each evolution rule? |
| Protocol Map | [Runtime Protocol Map](SRP_RUNTIME_PROTOCOL_MAP.md) | Which module consumes and produces which runtime events? |
| Implementation Alignment | [Implementation Alignment](SRP_IMPLEMENTATION_ALIGNMENT.md) | How does the current code map to runtime roles? |
| Implementation Event Alignment | [Implementation Event Alignment](SRP_IMPLEMENTATION_EVENT_ALIGNMENT.md) | How does current code map to the event processing model? |
| Policy | [Policy Mechanism Design](SRP_POLICY_MECHANISM_DESIGN.md) | How are resources allocated? |
| Lifecycle | [Runtime Lifecycle Design](SRP_RUNTIME_LIFECYCLE_DESIGN.md) | How does state evolve? |
| Analysis | [Mechanism Attribution Framework](SRP_MECHANISM_ATTRIBUTION_FRAMEWORK.md), [Evaluation Objective Matrix](SRP_EVALUATION_OBJECTIVE_MATRIX.md) | Why did preservation change and how is it measured? |
| Assumptions | [Core Assumptions](SRP_CORE_ASSUMPTIONS.md) | What premises ground SRP? |

```text
P = [Identity, Structure, Value, Stability]
```

```text
importance weighting -> value
dependency retention -> structure
archive / recovery -> identity
lifecycle tracking -> stability
semantic evolution -> activation, consolidation, maintenance, forgetting, recovery
runtime object model -> shared contract, ownership, mutation boundaries
semantic unit model -> atomic unit, identity kernel, unit-level evolution
semantic unit field spec -> field semantics, ownership, mutability, invariants
semantic graph model -> nodes, edges, subgraphs, neighborhoods, semantic paths
semantic constraint system -> identity, structure, semantics, evolution, runtime constraints
semantic graph algorithms -> canonicalization, merge, split, approximation, recovery, pruning, diff, neighborhood search
semantic operator algebra -> operator composition, ordering, commutativity, idempotence, preservation laws
semantic versioning model -> semantic commit DAG, branch, merge, rollback, checkout
formal semantics -> objects, operators, constraints, replay, trace, transition laws
semantic metric space -> future distance model for identity, structure, history, context
runtime semantics -> execution model, runtime steps, constraint gating, determinism
semantic time model -> semantic age, drift time, version time, recovery time
semantic lifecycle model -> active, merged, approximated, archived, forgotten, permanently_removed
state compaction model -> archive blocks, preserved evidence, maintenance traces
archive representation model -> archive store, segments, entries, indices, recovery evidence
archive index model -> unit, lineage, version, trace, evidence indices
archive query model -> lookup, evidence discovery, verification status, incomplete evidence
archive query service spec -> service contract, lookup APIs, verification, warning semantics
minimal runtime kernel -> submit, validate, evaluate, execute, commit, replay, query
runtime data contract -> invariants, events, history, integrity
runtime event contract -> legal transitions, mutation scopes, event schemas
runtime event interface -> decision, event, mutation, replay, permission matrix
runtime event processing model -> producer, validator, applier, lifecycle
runtime kernel target -> minimal execution layer, replay, attribution, invariants
runtime kernel interface -> submit, validate, apply, query, replay
runtime kernel api map -> current implementation, event wrapping, migration boundary
runtime kernel adapter plan -> observation, wrapping, mutation routing, replay enablement
runtime kernel migration checklist -> verification gates, phase exits, block conditions
kernel callsite map -> callsites, hidden mutation inventory, migration status
runtime kernel phase migration map -> phased hotspots, event wrapping, mutation routing, replay enablement
semantic evolution trace model -> causal evolution, drift path, recovery lineage
semantic evolution trace spec -> trace nodes, trace edges, queryable causal structure
replay spec -> deterministic reconstruction, rule versioning, replay drift
runtime recording layer alignment -> state snapshots, trace generation, replay support, projections
runtime component interface spec -> minimal executable interfaces, event identity, causal tracing, deterministic replay
semantic evolution rules -> consolidation, decay, approximation, recovery, garbage collection
runtime kernel milestone 2 plan -> decision boundary, semantic commit, runtime checkpoint
runtime kernel milestone 2 implementation checklist -> decision engine, commit manager, checkpoint manager, boundary freeze
runtime kernel milestone 2 reference interface spec -> decision context, operator candidate, decision result, semantic commit, runtime checkpoint
runtime kernel milestone 2 integration validation -> decision determinism, commit consistency, checkpoint isolation, replay equivalence
runtime kernel milestone 2 branching validation -> version branch creation, branch replay isolation, commit conflict detection, checkpoint branch binding
version conflict model -> conflict evidence, resolution boundary, replay divergence, checkpoint mismatch
runtime decision boundary model -> operator candidates, constraint filtering, metric evidence, decision result
semantic commit model -> commit boundary, validation, version dag, replay relation
runtime checkpoint model -> replay acceleration, checkpoint boundary, version anchor, drift detection
semantic evolution rule table -> triggers, transitions, invariants, forbidden cases
implementation alignment -> module roles, event boundary, mutation boundary
implementation event alignment -> producer, validator, applier, migration boundary
budget allocation -> trade-off behavior
```

```text
Boundary -> when preservation fails
Robustness -> whether preservation is stable
Drift -> whether preservation changes over time
Attribution -> which mechanism caused the change
Ablation -> what changes when a mechanism is removed
```

Graph is one possible implementation choice.
It is not the theory itself.

Short-term memory and long-term memory are treated as maintenance tiers within the same semantic state model:

- short-term memory keeps recently activated, high-salience content near the active runtime boundary
- long-term memory keeps consolidated semantic units, aliases, and recoverable history under decay-based retention

Semantic evolution is the parent layer.
Memory maintenance, forgetting, recovery, consolidation, and garbage collection are sub-rules inside it.
