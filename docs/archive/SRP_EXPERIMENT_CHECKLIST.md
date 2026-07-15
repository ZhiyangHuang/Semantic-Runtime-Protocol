# SRP Experiment Platform Checklist

This checklist is the platform and measurement closure document.

Its job is to freeze the metric contract, lock lifecycle attribution, and keep the reporting surface stable while policy research continues in a separate plan.

Stage 2 is now frozen. The next algorithm-facing phase is documented in [SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md](SRP_CORE_ALGORITHM_EVOLUTION_PLAN.md).

---

## 1. P0 Platform Closure

Goal: freeze the experiment result schema and metric contract across all lifecycle stages.

### 1.1 Unified Result Schema

Status: `uncompleted`

Needs:

- `experiment_result_schema_v1.json`
- one canonical record layout for:
  - `representation`
  - `compression`
  - `reconstruction`
  - `allocation`
  - `repair`
  - `execution`
  - `metrics`

### 1.2 Metric Contract Freeze

Status: `partial`

Already verified:

- `semantic_similarity`
- `validation_coverage`
- `validation_alignment`
- `recovered_object_count`
- `hallucinated_count`
- `object_inflation_ratio`
- `prompt_tokens`
- `completion_tokens`
- `total_tokens`

Needs contract freeze:

- `integrity_gap`
- `semantic_compression_loss`
- `object_retention`
- `weighted_object_retention`
- `lost_important_object_count`
- `structured_state_package_present`
- `recovered_object_type_counts`
- `repair_attempted`
- `repair_context_flat`
- `coverage_before_repair`
- `coverage_after_repair`
- `critical_failures_before`
- `critical_failures_after`
- `compressed_size`
- `compression_ratio`
- `state_committed`

### 1.3 Lifecycle Contract Rule

Every metric should be derivable from a named lifecycle stage:

- `source`
- `compressed`
- `recovered`
- `allocated`
- `executed`
- `repaired`

---

## 2. P0 Lifecycle Attribution

Goal: isolate causal boundaries between representation, recovery, allocation, execution, and repair.

### 2.1 Already Present In Code

- `object_lifecycle`
- `source_object_count`
- `compressed_object_count`
- `recovered_object_count`
- `repaired_object_count`
- `validation_coverage`
- `validation_alignment`
- `state_allocation_result`

### 2.2 Still Needed For Clean Attribution

- `source_to_compressed_recall`
- `compressed_to_recovered_recall`
- `recovered_to_repaired_recall`
- `lifecycle_inflation`
- stage-level object counts for `allocated` and `executed`

### 2.3 Interpretation Rule

Lifecycle attribution should answer:

- where a dependency was lost
- where hallucination entered
- whether allocation changed fidelity or only partitioning

Current note:

- the first fixed harness bundle has already run
- lifecycle attribution is now usable for comparing recovery and repair paths
- stage-level `allocated` and `executed` counts still need a dedicated benchmark pass if you want a stronger causal split

---

## 3. P0 Recovery and Integrity Surface

Goal: keep recovery outputs measurable without treating recovery policy as the whole research problem.

### 3.1 Already Verified

- `structured_state_package_present`
- `recovered_state_package`
- `reconstruction_result`
- `reconstruction_precision`
- `reconstruction_selectivity`
- `minimality_score`

### 3.2 Needs Standardization

- `important_recall`
- `task_critical_recall`
- `task_critical_precision`
- `reconstruction_efficiency`
- `hallucinated_count` in recovery-policy comparisons

### 3.3 Integrity Metrics Needing Final Definition

- `integrity_gap`
- `semantic_compression_loss`
- `weighted_object_retention`
- `lost_important_object_count`

---

## 4. P0 Repair Diagnostics

Goal: keep repair as a robustness and causal-diagnostics layer.

### 4.1 Already Verified

- repair can be triggered after validation failure
- repaired recovery path is executed
- repaired validation is re-run

### 4.2 Still Missing as Stable Report Fields

- `repair_attempted`
- `coverage_before_repair`
- `coverage_after_repair`
- `repair_gain`
- `critical_failures_before`
- `critical_failures_after`

### 4.3 Interpretation Rule

Repair should be reported as:

- robustness under corruption
- causal recovery of missing state
- not as the primary bottleneck unless evidence changes

---

## 5. P0 Reporting Contract

Goal: keep experiment records comparable across runs.

### 5.1 Shared Fields

- `experiment_id`
- `task_id`
- `date`
- `dataset`
- `model`
- `context_budget`
- `config_summary`
- `ablation`
- `status`
- `result_summary`
- `metric_values`
- `short_conclusion`
- `next_action`

### 5.2 Current Status Labels

- `completed`
- `running`
- `planned`
- `blocked`
- `archived`

---

## 6. Platform Status Summary

- completed: core runtime pipeline, structured recovery, allocation, repair diagnostics, unified result schema, lifecycle attribution, integrity metric standardization, and the first fixed harness bundle
- in progress: LongBench v2 sanity coverage and benchmark-pressure upgrades for the weakly separated object-aware compression line
- deferred to policy plan: deeper evaluator studies and broader allocation benchmarks

---

## 7. P1 Policy Evaluation

These are the next research experiments, not platform bugs.

- reconstruction policy ablation
- text vs structured recovery comparison
- object-aware compression ablation
- stronger allocation benchmark
- task-critical filtering under benchmark pressure
- repair loop formal ablation
- policy design space exploration
- policy mechanism attribution / ablation protocol
- canonical ablation spec: [SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md](SRP_MECHANISM_ATTRIBUTION_ABLATION_PROTOCOL.md)
- A2 dependency-aware retention ablation prototype
- mechanism ablation comparison layer with attribution score

## 8. Phase VI Core Algorithm Evolution

The next work should improve SRP itself rather than expand the Stage 2 measurement layer.

- [x] Build `semantic_failure_taxonomy.json`
- [x] Build `semantic_failure_taxonomy.md`
- [x] Write `SRP_FAILURE_ANALYSIS_REPORT.md`
- [ ] Use the failure taxonomy to drive the semantic state upgrade
- [x] Semantic state representation upgrade: minimal graph v1
- [x] Semantic state representation upgrade: graph v1.5 schema
- [x] Dependency-aware recovery: graph-aware recovery v1
- [x] Dependency-aware recovery: graph recovery evaluation harness
- [x] Graph information gap analysis for graph v1
- [x] Graph representation ablation: graph v1 vs graph v1.5
- [x] Semantic extraction audit
- [x] Runtime Representation v2 / Semantic Extraction Engine v2
- [x] Provenance-aware node typing
- [x] Runtime frame / narrative / conversation layers
- [ ] Coverage Attribution Analysis
- [ ] Stage-wise Loss Matrix
- [x] Policy Pareto Analysis
- [x] Policy Sensitivity Analysis
- [x] Policy Boundary Analysis
- [x] Policy Boundary Robustness
- [x] Policy Boundary Drift
- [ ] Strong baselines
- [ ] Long-horizon evaluation
- [ ] Decoding robustness stress test
- [ ] Reuse the frozen Stage 2 evaluator for all Phase VI comparisons

Round 1 observation:

- recovery and reconstruction already produced separable observations
- object-aware compression did not separate on the current benchmark
- policy intervention now shows a tradeoff: permissive is best for validation coverage, while conservative is best for graph integrity and object retention
- the next policy step is Pareto analysis and sensitivity analysis, not an optimization runner
- the first sensitivity analysis run is mostly flat on the current fixed benchmark, which is itself a useful baseline finding
- the first boundary analysis run is complete; allocation behavior now shows a transition between budgets 32 and 24 on the memory-saturation benchmark
- the validation-pressure benchmark now also shows a validation transition, with `validation_score` changing across the same pressure region
- the policy boundary work now distinguishes allocation transitions from validation transitions
- the boundary robustness run now shows allocation, dependency, and validation boundaries are relatively stable across seeds, while dependency-F1 is the most fragile boundary type
- the long-horizon drift run over cycles 1, 3, and 5 shows no measurable midpoint drift for allocation, dependency, or dependency-F1 on the current benchmark family
- the boundary line is now considered closed for the current workload family; the next explanation target is mechanism causality, not additional boundary search
- the next policy step is mechanism attribution / ablation protocol, not more boundary scans
- mechanism verification now shows object support changes scores, but not the selected top-k set
- the Top-k decision boundary sweep is now complete as Stage 1
- the next object-aware analysis should be a threshold analysis split into:
  - RQ2.1 Budget Threshold: vary `top-k budget` only
  - RQ2.2 Ambiguity Threshold: vary `keyword overlap` only
  - RQ2.3 Support Threshold: vary `object-support strength` only
- decoy count stays fixed inside each RQ until the later difficulty sweep
- the new decision-sensitivity metric is `DBI = object_support_gain / decision_margin`
- after the fixed Stage 2 shape is locked, sample each RQ across multiple seeds and report `mean`, `std`, `95% CI`, and `flip probability`
- graph v1.5 is now the representation upgrade target; keep graph v1 frozen and compare the two versions with the same recovery harness
- next Phase VI.5 task: run the graph representation ablation and check whether `attribute_retention`, `state_retention`, and `lifecycle_accuracy` improve
- graph representation ablation has now been run once; v1.5 improves the new retention metrics and graph integrity while validation coverage stays flat on the current tasks
- semantic extraction audit has now been run; the next bottleneck is provenance / extraction under-specification, so coverage attribution should come before any graph recovery v2

---

## 8. P3 Deferred Research

These stay out of the critical path until the benchmark is stronger.

- encoder vs local LLM judge
- LongBench task-aware object schema
- more complex object taxonomies
- self-improving repair agent
- policy optimization runner
- new metrics for policy attribution

Reason:

- policy design-space exploration is the current research target; automated tuning comes later
- boundary characterization is closed for the current workload family; boundary robustness and drift did not reveal moving thresholds
- the next policy target is mechanism attribution / ablation protocol, not more boundary scans

---

## 9. Platform Rule

Keep causal boundaries isolated and measurable.
