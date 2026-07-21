# Full MMLU Execution Record V1

Date: 2026-07-21
Authorization commit/hash: `be79305811f69c839c947e7018aa3559e7553d25`
Authorization status: `AUTHORIZED`

## Execution Configuration

- Benchmark: `mmlu`
- Dataset source: `hf:cais/mmlu`
- Dataset split: `test`
- Subject scope: `all`
- Sample policy: full benchmark execution
- Model identifier: `Qwen/Qwen3-4B-AWQ`
- Variants: `baseline`, `srp`
- Temperature: `0.0`
- Max output tokens: `8`
- Prompt format: `mmlu_mcq_v1`
- SRP mode: `context_recovery`

## Output Directory

- `experiments/results/mmlu_full_v1/`

## Planned Command

```text
python - <<'PY'
from experiments.benchmarks.mmlu.config import MMLUConfig
from experiments.benchmarks.mmlu.runner import write_mmlu_artifact

config = MMLUConfig(
    data_root='hf:cais/mmlu|all|test',
    subjects=('all',),
    sample_limit=0,
    variants=('baseline', 'srp'),
    model='Qwen/Qwen3-4B-AWQ',
    temperature=0.0,
    max_output_tokens=8,
)
write_mmlu_artifact('experiments/results/mmlu_full_v1', config=config)
PY
```

## Notes

- This record is created before execution as part of the release audit trail.
- The run must not modify `paper/` or any evidence manifest during execution.
- Smoke artifacts remain isolated in their own directories.

