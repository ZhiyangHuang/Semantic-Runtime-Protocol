# SRP Next-Phase Tasks

This is the Phase V roadmap for SRP.

It is organized into three layers:

- `P0` platform closure
- `P1` policy evaluation
- `P3` deferred research

The system is now in a scientific evaluation phase, not a component implementation phase.

Stage 2 is now frozen as a reusable measurement layer.
The next algorithm-facing phase is documented in [SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md](SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md) and [SRP_COVERAGE_ATTRIBUTION_PLAN.md](SRP_COVERAGE_ATTRIBUTION_PLAN.md).

The key shift is:

```text
chunk-preserving SRP
-> state-preserving SRP
```

---

## 1. P0 Platform Closure

These tasks freeze the measurement contract and reporting surface.

### 1.1 Unified Experiment Result Schema

Tasks:

- define `experiment_result_schema_v1.json`
- unify `representation`, `compression`, `reconstruction`, `allocation`, `repair`, `execution`, and `metrics`
- keep the schema consistent across record builder, CSV export, and markdown audit output

Acceptance:

- every experiment record can be serialized into one canonical structure
- the same fields are available in logs, CSV, and markdown reports

### 1.2 Lifecycle Attribution

Tasks:

- standardize `object_lifecycle`
- standardize `source_object_count`
- standardize `compressed_object_count`
- standardize `recovered_object_count`
- standardize `repaired_object_count`
- add stage-level counts for `allocated` and `executed`
- add recall-style transition metrics for source -> compressed -> recovered -> repaired

Acceptance:

- attribution can answer where dependency loss or hallucination entered
- allocation effects can be separated from recovery effects

### 1.3 Integrity and Retention Metrics

Tasks:

- define and export `integrity_gap`
- define and export `semantic_compression_loss`
- standardize `object_retention`
- standardize `weighted_object_retention`
- standardize `lost_important_object_count`
- standardize `recovered_object_type_counts`
- standardize `validation_passed`
- standardize `state_committed`

Acceptance:

- recovery quality and compression quality can be compared using one contract
- the metrics are stage-aware, not ad hoc

### 1.4 Repair Diagnostics

Tasks:

- standardize `repair_attempted`
- standardize `repair_context_flat`
- standardize `coverage_before_repair`
- standardize `coverage_after_repair`
- standardize `repair_gain`
- standardize `critical_failures_before`
- standardize `critical_failures_after`

Acceptance:

- repair is measured as causal robustness, not just fallback behavior

---

## 2. P1 Core SRP Ablations

These experiments should run before benchmark expansion.

### 2.1 Text vs Structured Recovery

Compare:

- `text only`
- `structured only`
- `text + structured`

Primary measures:

- `validation_coverage`
- `important_recall`
- `task_critical_recall`
- `recovered_object_count`
- `hallucinated_count`
- `object_inflation_ratio`

### 2.2 Reconstruction Policy

Compare:

- `unrestricted`
- `constrained`
- `minimal`

Primary measures:

- `validation_coverage`
- `recovered_object_count`
- `hallucinated_count`
- `reconstruction_precision`
- `reconstruction_selectivity`
- `minimality_score`

### 2.3 Object-Aware Compression

Compare:

- `chunk score only`
- `chunk score + object support`

Primary measures:

- `weighted_object_retention`
- `lost_important_object_count`
- `critical_failures_before`

### 2.4 Repair Loop Formal Ablation

Compare:

- `fail -> rollback`
- `fail -> repair -> revalidate`

Primary measures:

- `repair_attempted`
- `coverage_before_repair`
- `coverage_after_repair`
- `repair_gain`
- `token_overhead`

### 2.5 Round 1 Fixed Harness Observations

The first fixed harness bundle has been executed. The initial one-cycle summary is:

| Harness | Suite | Key Observation |
| --- | --- | --- |
| Controlled | `structured_recovery` | `important_recall=1.0`, `task_critical_recall=0.5`, repair triggered |
| Controlled | `object_retention` | `important_recall=1.0`, `task_critical_recall=0.5`, repair triggered |
| Controlled | `repair_loop` | `important_recall=1.0`, `task_critical_recall=0.0`, `token_overhead=0` |
| Recovery | `hybrid_recovery` | highest `validation_coverage=0.536765`, `hallucinated_count=0` |
| Recovery | `text_only_recovery` | `validation_coverage=0.497059`, `hallucinated_count=4` |
| Recovery | `structured_only_recovery` | `validation_coverage=0.407059`, `hallucinated_count=3` |
| Reconstruction | `minimal` | `minimality_score=0.3`, `reconstruction_precision=0.7` |
| Reconstruction | `unrestricted` / `constrained` | `reconstruction_precision=1.0`, `minimality_score=0` |
| Object-aware compression | `chunk_score_only` vs `chunk_score_plus_object_support` | no observable difference on the current benchmark |

Interpretation:

- recovery and reconstruction already provide usable hypotheses
- object-aware compression needs stronger benchmark pressure before it can separate policies
- the first round is sufficient for baseline reporting, but not yet sufficient for claiming object-support benefit

---

## 3. P1 Runtime State Evolution

Phase IV suggests SRP should be evaluated as a semantic runtime system, not only as a compression system.

### 3.1 Runtime Metadata into Allocation

Tasks:

- make importance and runtime metadata affect allocation decisions
- compare static allocation with importance-aware allocation
- keep memory, query, and budget fixed while allocation changes

Acceptance:

- high-importance objects are retained more often
- allocation differences are measurable in active-state composition

### 3.2 Object Lifecycle Tracking

Tasks:

- add `ObjectLifecycleRecord`
- track object creation, compression, recovery, verification, and retention
- track drift or stability across rounds

Acceptance:

- SRP can report how each semantic object evolves across rounds
- lifecycle change can be attributed to specific stages

### 3.3 Long-Horizon State Evolution

Tasks:

- measure state drift over many rounds
- compare full context, summary, and SRP-style state handling
- expose accumulation rather than single-step recovery only

Acceptance:

- semantic drift can be plotted across rounds
- SRP can be evaluated as state maintenance under interaction

### 3.4 Policy Design Space Exploration

Tasks:

- interpret policy intervention results as a Pareto frontier
- compare coverage, integrity, and retention together
- sweep threshold, decay, and budget-related policy parameters
- record sensitivity curves for the key policy knobs

Acceptance:

- policy tradeoffs are explicit rather than collapsed into a single winner
- the policy layer stays scientific and interpretable
- automated policy optimization remains deferred unless a later paper needs it

---

## 4. Phase VI Core Algorithm Evolution

The measurement layer is now stable, so the next work should strengthen SRP itself.

Follow the plan in [SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md](SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md).

Priority order:

1. Failure taxonomy analysis
2. Semantic state representation upgrade
3. Dependency-aware recovery
4. Strong baselines
5. Long-horizon evaluation
6. Decoding robustness stress test
7. Policy design space exploration

Current work item:

- first-pass failure taxonomy has been generated from the fixed-harness records
- dominant failures are `object_loss`, `dependency_break`, and `hallucinated_reconstruction`
- `dependency_break` is currently dominated by `constraint_loss` and `identity_collision`
- `SRP_FAILURE_ANALYSIS_REPORT.md` has been written
- use the failure taxonomy to drive the semantic-state upgrade plan
- semantic runtime graph v1 is now implemented as the minimal upgrade target
- the graph stays intentionally small: nodes, edges, lifecycle, and validation
- the recovery layer now has a graph-aware policy path in progress
- the graph recovery evaluation harness has now been implemented and run on the fixed Round 1 task set
- graph mode currently lowers graph repair cost, while validation coverage remains flat on the present tasks
- the next step is to decide whether to strengthen the graph-pressure tasks or use the current harness as the baseline for algorithm evolution
- graph information gap analysis now shows that graph v1 is missing richer node attributes and an explicit modified lifecycle stage
- the next representation step should be a graph v1.5 schema upgrade instead of expanding graph recovery rules
- graph information gap analysis now shows that graph v1 is missing richer node attributes and an explicit modified lifecycle stage
- the next representation step should be a graph v1.5 schema upgrade instead of expanding graph recovery rules
- graph v1.5 schema work has started so the next comparison can isolate representation changes without changing the recovery policy
- Phase VI.5 should now run the graph representation ablation: `graph v1` versus `graph v1.5` on the same fixed recovery harness
- the first graph representation ablation run shows v1.5 improves attribute/state/lifecycle retention and graph integrity, while validation coverage remains flat on the current fixed tasks
- a semantic extraction audit has now been run on the graph representation records; the remaining gap points to provenance / extraction under-specification rather than another recovery-rule expansion
- the next concrete task is coverage attribution analysis, starting from the frozen SRR v2 prototype and the existing extraction audit, not graph recovery v2

### 4.1 Why this comes next

The existing Stage 2 framework already answers the threshold questions.
The next value comes from improving the algorithm, not adding more threshold variables.

### 4.2 Stronger Allocation Benchmark

Tasks:

- construct branching dependency tasks
- construct identity-binding cases with multiple same-name or same-subject objects
- build tasks where required objects exceed active budget
- test closure retention under anchor-heavy compression

Acceptance:

- dependency recall, precision, and waste are separable
- identity binding failures become visible
- minimal, dependency-aware, and random allocation separate clearly

Current status after Round 1:

- recovery and reconstruction already separate on the first fixed bundle
- object-aware compression does not yet separate on the current benchmark
- benchmark upgrade should be targeted only at the weak-pressure object-aware compression line
- the next benchmark upgrade should emphasize dependency branching, subject collision, and budget pressure
- that benchmark upgrade is now being implemented as three fixed pressure scenarios
- the three-scenario upgrade is still not enough to separate the policies, so more decoy interference is needed
- mechanism verification now shows object support changes chunk scores, but not the top-k selection
- the Top-k decision boundary sweep is now complete as Stage 1
- the next compression step should be a three-part threshold analysis:
  - RQ2.1 Budget Threshold: vary `top-k budget` only
  - RQ2.2 Ambiguity Threshold: vary `keyword overlap` only
  - RQ2.3 Support Threshold: vary `object-support strength` only
- decoy count stays fixed inside each RQ until the later difficulty sweep
- the new decision-sensitivity metric is `DBI = object_support_gain / decision_margin`
- after the threshold shape is fixed, sample each RQ across multiple seeds and report `mean`, `std`, `95% CI`, and `flip probability`
- policy intervention has now produced a first sweep over baseline, permissive, balanced, and conservative policies
- the next interpretation step is Pareto analysis, not an optimization runner
- policy sensitivity curves should be added before any automated tuning work

---

## 5. P3 Deferred Research

These items are intentionally postponed until the benchmark and contract are stronger.

- encoder vs local LLM judge
- LongBench task-aware object schema
- more complex object taxonomies
- self-improving repair agent
- policy optimization runner

Reason:

- if the same metric can be improved by multiple mechanisms, the causal boundary is still too weak
- policy optimization is a later engineering extension, not the current research contribution

---

## 6. One-Sentence Positioning

Phase V should move SRP from informative chunk preservation to typed semantic runtime state preservation, because benchmark-critical semantics are lost even when embedding similarity stays high.
