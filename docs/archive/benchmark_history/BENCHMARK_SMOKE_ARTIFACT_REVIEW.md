# Benchmark Smoke Artifact Review

## Scope

Reviewed artifacts:
- `experiments/results/mmlu_smoke/`
- `experiments/results/arc_smoke/`

Review references:
- `BENCHMARK_SMOKE_EXPERIMENT_PLAN.md`
- `BENCHMARK_SMOKE_EXECUTION_GUIDE.md`

This is a review only:
- no paper files were modified
- no evidence manifests were modified
- no benchmarks were rerun
- no metrics were changed

---

## 1. Artifact Contract Comparison

### MMLU

- `config.json`: present
- `raw_predictions.jsonl`: present
- `metrics.json`: present
- `metadata.json`: present
- `report.md`: present

### ARC

- `config.json`: present
- `raw_predictions.jsonl`: present
- `metrics.json`: present
- `metadata.json`: present
- `report.md`: present

### Contract compatibility

The two smoke bundles share the same artifact contract:
- same file set
- same shared runner lineage
- same shared artifact writer lineage
- same metadata hash structure

Provenance completeness is also aligned:
- both bundles record dataset source/reference
- both bundles record model identifier
- both bundles record generation parameters
- both bundles record artifact hashes in metadata

Conclusion:
- artifact schema compatibility: pass
- provenance completeness: pass
- artifact writer consistency: pass

---

## 2. Pipeline Consistency

Both smoke runs used the shared benchmark execution path:
- `experiments/benchmarks/common/runner.py`
- `experiments/benchmarks/common/artifact.py`
- `experiments/benchmarks/common/report.py`
- `experiments/benchmarks/common/metrics.py`

Benchmark-specific layers were limited to:
- `experiments/benchmarks/mmlu/adapter.py`
- `experiments/benchmarks/arc/adapter.py`

Observed benchmark-specific deviations:
- dataset source strings differ because the datasets are different
- prompt text differs because MMLU and ARC preserve their own question/choice formatting
- metrics naming stays compatible, but the primary metric is still accuracy for both

No duplicate runner or duplicate artifact writer was introduced.

Conclusion:
- shared runner: pass
- shared schema: pass
- shared artifact writer: pass
- shared metrics flow: pass

---

## 3. Raw Prediction Audit

### Record completeness

Each raw prediction record contains:
- `case_id`
- `prompt`
- `prediction`
- `expected_answer`
- `variant`
- `latency_seconds`
- `token_usage`
- `raw_response`
- `reference_answer`
- `score`
- `is_correct`
- `error`

### Baseline and SRP counts

Both smoke artifacts contain:
- 100 total prediction rows
- 50 `baseline` rows
- 50 `srp` rows

### Audit result

- raw prediction completeness: pass
- baseline / SRP count parity: pass
- model response preservation: pass
- token usage preservation: pass
- latency preservation: pass

---

## 4. Metric Audit

Metrics were derived from generated predictions rather than hand-edited.

### MMLU smoke

- sample count: `50`
- prediction count: `100`
- correct count: `36`
- incorrect count: `14`
- failed prediction count: `0`
- accuracy: `0.72`
- baseline accuracy: `0.72`
- SRP accuracy: `1.0`

### ARC smoke

- sample count: `50`
- prediction count: `100`
- correct count: `46`
- incorrect count: `4`
- failed prediction count: `0`
- accuracy: `0.92`
- baseline accuracy: `0.92`
- SRP accuracy: `0.96`

### Metric audit result

- metrics derived from predictions: pass
- sample counts recorded: pass
- correctness counts recorded: pass
- failure counts recorded: pass

Important note:
- these smoke metrics validate pipeline correctness only
- they are not evidence of benchmark superiority

---

## 5. Reproducibility Audit

### MMLU smoke

- dataset source/reference: `hf:cais/mmlu|abstract_algebra,anatomy,astronomy,business_ethics,clinical_knowledge|validation`
- dataset version: `mmlu_v1`
- model identifier: `Qwen/Qwen3-4B-AWQ`
- generation parameters: `temperature=0.0`, `max_output_tokens=8`
- artifact hashes: present in `metadata.json`

### ARC smoke

- dataset source/reference: `hf:allenai/ai2_arc|ARC-Easy|test`
- dataset version: `arc_v1`
- model identifier: `Qwen/Qwen3-4B-AWQ`
- generation parameters: `temperature=0.0`, `max_output_tokens=8`
- artifact hashes: present in `metadata.json`

### Reproducibility result

- dataset source captured: pass
- dataset version/reference captured: pass
- model identifier captured: pass
- generation parameters captured: pass
- artifact hashes captured: pass

---

## 6. Issues Found

### MMLU answer=0 parsing bug

Issue:
- zero-valued answer labels were initially treated as falsy in the adapter
- this caused valid answers to be mis-normalized

Fix applied:
- replaced truthiness checks with explicit `None` handling
- preserved zero-valued answer labels during normalization

Verification:
- MMLU smoke was rerun after the fix
- the rerun produced a complete artifact bundle
- the rerun artifacts are the reviewed ones

### Remaining risks

- smoke sample sizes are intentionally small
- ARC smoke uses ARC-Easy only
- full benchmark execution has not yet been run
- HumanEval remains design-only

---

## 7. Recommendation

**A. Ready for full benchmark execution**

Reason:
- both MMLU and ARC smoke runs produced complete, compatible, reproducible artifact bundles
- the shared runner, shared schema, shared artifact writer, and shared metrics flow were validated on two different benchmark schemas
- the only substantive adapter bug found during smoke was fixed and re-validated

Constraints on this recommendation:
- this recommendation applies to pipeline readiness, not to paper claims
- full benchmark execution still needs its own execution boundary and review pass

