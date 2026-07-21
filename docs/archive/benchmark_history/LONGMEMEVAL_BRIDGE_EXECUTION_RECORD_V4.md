# LongMemEval Bridge Execution Record V4

Date: 2026-07-21

## Authorization Basis

- Bridge architecture: `BRIDGE_ARCHITECTURE_FROZEN`
- Adapter status: `ADAPTER_IMPLEMENTED_AND_VALIDATED`
- Runner status: `RUNNER_IMPLEMENTED_AND_VALIDATED`
- Metrics/report status: `METRICS_REPORT_MAPPING_VALIDATED`
- Compatibility status: `COMPATIBILITY_GATE_PASSED`

## Repository Provenance

- commit hash: `be79305811f69c839c947e7018aa3559e7553d25`
- note: v1-v3 bridge outputs are retained as iteration history; v4 is the corrected official bridge artifact

## Bridge Configuration

- bridge name: `longmemeval`
- bridge version: `bridge_migration_v1`
- source config: `configs/external_validation_longmemeval_evidence.env`
- bridge output dir: `experiments/results/longmemeval_full_v4`

## External Validation Runtime

- provider: `local_vllm`
- backend: `vllm`
- endpoint: `http://172.25.253.78:8000`
- model: `Qwen/Qwen3-4B-AWQ`
- tokenizer: `Qwen/Qwen3-4B-AWQ`
- prompt template id: `longmemeval_shared_generation_prompt_v1`
- temperature: `0.0`
- max output tokens: `96`
- sample limit: `0`

## Execution Command

```text
python -c "from experiments.benchmarks.longmemeval import run_longmemeval_bridge; print(run_longmemeval_bridge(output_dir='experiments/results/longmemeval_full_v4'))"
```

## Expected Artifact Contract

- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

