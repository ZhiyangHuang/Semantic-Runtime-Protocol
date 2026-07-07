# Semantic Runtime Protocol

This repository implements SRP as a model-independent semantic runtime protocol.

## Protocol Positioning

SRP manages `semantic runtime state`, not token hidden state. It does not cache transformer `K/V` tensors and it does not depend on model-internal KV cache reuse.

SRP should be understood as a protocol over semantic state:

- It preserves typed semantic objects, runtime metadata, and verification history.
- It uses stable recovery templates to improve `prompt-prefix stability`.
- It can benefit systems that support prefix caching, but KV cache reuse is only an optional experimental signal, not a core SRP dependency.

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

## Export Helpers

The easiest way to export SRP runs to CSV is:

```bash
python srp_experiment/export_csv.py --cycles 1 --output-csv srp_experiment/tmp/srp_records.csv
```

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
- `runtime_round`
- `runtime_history_length`
- `semantic_drift`
- `semantic_stability`
- `validation_passed`
- `critical_failures`
- `failure_summary_flat_*`
- `lifecycle_summary_flat_*`
- `object_update_summary_flat_*`
- `policy_flat_*`

## Output

The exporter flattens the nested lifecycle and policy summaries into CSV-friendly columns.
It preserves:

- `task_id`
- `task_source`
- `lifecycle_summary_flat`
- `object_update_summary_flat`
- `policy_flat`
- `runtime` and `validation` fields from `run_srp()`

## Notes

- `lifecycle_summary_flat` is designed for CSV and ablation.
- `object_update_summary_flat` keeps object-level lifecycle updates visible in the same table.
- `policy_flat` keeps lifecycle thresholds visible in the same table.
- The exporter accepts either task JSON, task directories, or JSONL streams.
