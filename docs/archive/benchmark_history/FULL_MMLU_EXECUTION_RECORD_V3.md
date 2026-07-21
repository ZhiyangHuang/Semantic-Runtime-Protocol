# Full MMLU Execution Record V3

Date: 2026-07-21
Authorization commit/hash: `be79305811f69c839c947e7018aa3559e7553d25`
Authorization status: `AUTHORIZED`

## Execution Configuration

- Benchmark: `mmlu`
- Dataset source: `hf:cais/mmlu`
- Dataset split: `test`
- Subject scope: full dataset via `all` config, with no subject filter
- Sample policy: full benchmark execution
- Model identifier: `Qwen/Qwen3-4B-AWQ`
- Variants: `baseline`, `srp`
- Temperature: `0.0`
- Max output tokens: `8`
- Prompt format: `mmlu_mcq_v1`
- SRP mode: `context_recovery`

## Output Directory

- `experiments/results/mmlu_full_v3/`

## Planned Command

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
write_mmlu_artifact('experiments/results/mmlu_full_v3', config=config)
PY
```

## Notes

- v1 was a diagnostic attempt with a subject-filter mismatch.
- v2 is the official historical full artifact but is now marked methodologically invalid because the SRP prompt-visible recovered context leaked `expected_answer`.
- v3 is the corrected rerun after removing the gold-answer field from prompt-visible SRP context and adding a shared leakage guard.

