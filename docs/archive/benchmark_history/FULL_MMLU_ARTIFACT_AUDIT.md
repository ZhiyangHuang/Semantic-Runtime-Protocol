# Full MMLU Artifact Audit

Date: 2026-07-21
Run record: `FULL_MMLU_EXECUTION_RECORD_V2.md`
Execution authorization: `AUTHORIZED`

This audit reviews the completed full MMLU execution artifact bundle.

---

## 1. Command and Scope

Command executed:

```text
python - <<'PY'
from experiments.benchmarks.mmlu.config import MMLUConfig
from experiments.benchmarks.mmlu.runner import write_mmlu_artifact

config = MMLUConfig(
    data_root='hf:cais/mmlu|all|test',
    subjects=(),
    sample_limit=0,
    variants=('baseline', 'srp'),
    model='Qwen/Qwen3-4B-AWQ',
    temperature=0.0,
    max_output_tokens=8,
)
write_mmlu_artifact('experiments/results/mmlu_full_v2', config=config)
PY
```

Scope:
- benchmark: MMLU
- dataset source: `hf:cais/mmlu`
- split: `test`
- subject scope: full `all` config, with no subject filter
- model: `Qwen/Qwen3-4B-AWQ`
- variants: `baseline`, `srp`

---

## 2. Artifact Paths

Verified artifact bundle:

- `experiments/results/mmlu_full_v2/config.json`
- `experiments/results/mmlu_full_v2/raw_predictions.jsonl`
- `experiments/results/mmlu_full_v2/metrics.json`
- `experiments/results/mmlu_full_v2/metadata.json`
- `experiments/results/mmlu_full_v2/report.md`

All required files are present.

---

## 3. Raw Prediction Audit

Raw prediction file:
- `experiments/results/mmlu_full_v2/raw_predictions.jsonl`

Observed properties:
- line count: `28084`
- baseline records: `14042`
- SRP records: `14042`
- every benchmark case has both variants recorded
- raw records include prompt, prediction, expected answer, token usage, latency, and raw response payload

Raw prediction integrity:
- no missing rows detected in the artifact review
- no manual post-editing of raw predictions was performed

---

## 4. Metric Audit

Metric file:
- `experiments/results/mmlu_full_v2/metrics.json`

Key metrics:
- `sample_count: 14042`
- `prediction_count: 28084`
- `baseline_accuracy: 0.653183`
- `srp_accuracy: 0.996083`
- `accuracy_gap: 0.3429`
- `correct_count: 9172`
- `incorrect_count: 4870`
- `invalid_output_count: 1`
- `srp_correct_count: 13987`
- `srp_incorrect_count: 55`
- `srp_invalid_output_count: 0`

Metric interpretation:
- metrics were generated automatically from the run outputs
- metrics are consistent with the raw prediction bundle
- the metric file is not manually edited

---

## 5. Reproducibility Audit

Recorded provenance:
- authorization commit: `be79305811f69c839c947e7018aa3559e7553d25`
- authorization status: `AUTHORIZED`
- model identifier: `Qwen/Qwen3-4B-AWQ`
- dataset version: `mmlu_v1`
- prompt format: `mmlu_mcq_v1`
- runner version: `benchmark_runner_v1`
- generated_at recorded in metadata
- artifact hashes recorded in metadata

The active paper boundary remained clean during execution.

---

## 6. Issues Found and Fixes

Issue discovered during the first attempt:
- subject filtering with `subjects=('all',)` caused the adapter to drop every record because the loaded records still carry their actual subject names

Fix applied:
- reran the benchmark with `subjects=()`, allowing the `all` dataset config to expand into the full test split without filtering away real subjects

Outcome:
- the corrected run in `experiments/results/mmlu_full_v2/` produced a valid full artifact bundle

---

## 7. Audit Conclusion

Status:
- full MMLU execution complete: YES
- artifact bundle complete: YES
- metrics generated automatically: YES
- paper boundary preserved: YES

Recommendation:
- full MMLU artifact is audit-ready for the next phase
- proceed to ARC full execution only after the benchmark review boundary for MMLU is accepted

