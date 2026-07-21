# Benchmark Smoke Execution Guide

This guide turns the smoke experiment plan into an executable runbook.

This document is preparation only:
- do not execute benchmarks
- do not download datasets
- do not create result artifacts
- do not modify `paper/`
- do not modify evidence manifests

---

## 1. Environment Preconditions

### Required Python environment

- Python must be available in the repository environment used for SRP experiments.
- The environment must be able to import the existing `experiments.*` packages.
- The environment must already support the local benchmark helpers under `experiments/common/local_llm.py`.

### Required packages

Observed from the repository:
- no `requirements.txt` was found
- no `pyproject.toml` was found
- no lockfile was found

Implication:
- the execution environment must already contain whatever dependencies are needed for:
  - the shared benchmark layer
  - the MMLU adapter
  - the ARC adapter
  - the local OpenAI-compatible client

### Model endpoint requirement

- A reachable OpenAI-compatible local model endpoint must be available.
- `experiments/common/local_llm.py` defaults to `LOCAL_MODEL_URL` and `SRP_MODEL`.
- The endpoint must support `/v1/chat/completions`.

### Configuration requirements

- A benchmark smoke config must specify:
  - dataset source or root
  - sample size
  - subject or split selection
  - model identifier
  - prompt format
  - output directory
  - SRP variant settings

### Missing pieces

- No benchmark-specific smoke config files currently exist.
- No benchmark smoke execution command has been wired into `scripts/run_reproduction.py`.
- No smoke result directories exist yet for `mmlu_smoke` or `arc_smoke`.

---

## 2. MMLU Smoke Command Plan

### Expected command

Illustrative only:

```bash
python -m experiments.benchmarks.mmlu.runner
```

If the runner is extended to accept explicit smoke settings, the command should be able to pass:
- dataset root
- sample limit
- subject subset
- model config
- output directory

### Required config

- dataset source: real MMLU source recognized by the adapter
- sample size: approximately 50 samples
- subjects: a small subject slice, for example 5 subjects with 10 questions each
- model config: local endpoint, model name, temperature, max tokens
- output directory: `experiments/results/mmlu_smoke/`

### Expected artifact path

```text
experiments/results/mmlu_smoke/
```

### Expected artifact files

- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

---

## 3. ARC Smoke Command Plan

### Expected command

Illustrative only:

```bash
python -m experiments.benchmarks.arc.runner
```

### Required config

- dataset selection: `ARC-Easy` only for the smoke run
- sample size: approximately 50 samples
- model config: local endpoint, model name, temperature, max tokens
- output directory: `experiments/results/arc_smoke/`

### Expected artifact path

```text
experiments/results/arc_smoke/
```

### Expected artifact files

- `config.json`
- `raw_predictions.jsonl`
- `metrics.json`
- `metadata.json`
- `report.md`

---

## 4. Configuration Files

Proposed smoke config files for documentation purposes:

```text
configs/
    benchmarks/
        mmlu_smoke.json
        arc_smoke.json
```

Status:
- not created yet
- only needed if the execution flow is made config-file-driven

If the current framework uses direct Python config objects instead of files, these documents remain optional.

---

## 5. Execution Flow

### Step 1: Prepare environment

- confirm Python can import the repository packages
- confirm the local model endpoint is reachable
- confirm any dataset access requirements are satisfied

### Step 2: Validate endpoint

- send a lightweight generation request through `experiments/common/local_llm.py`
- confirm the endpoint returns a response and usage metadata

### Step 3: Run MMLU smoke

- execute the smoke-sized MMLU run
- write artifacts to `experiments/results/mmlu_smoke/`

### Step 4: Inspect artifacts

- verify files exist
- verify metrics were generated automatically
- verify report content is derived from metrics and predictions

### Step 5: Run ARC smoke

- execute the smoke-sized ARC run
- write artifacts to `experiments/results/arc_smoke/`

### Step 6: Inspect artifacts

- verify files exist
- verify choice handling and scoring outputs
- verify report and metadata consistency

---

## 6. Artifact Validation Checklist

For each benchmark:

- raw predictions exist
- metrics generated automatically
- report generated
- metadata recorded
- no manual edits were applied after generation
- artifact hashes are present where supported

Additional consistency checks:
- config matches the run settings
- artifact paths match the declared smoke output directory
- the report reflects the generated metrics rather than handwritten values

---

## 7. Rollback / Failure Handling

### Dataset unavailable

- stop the benchmark run
- do not synthesize results
- record a failure note for the missing dataset source

### Endpoint unavailable

- stop before benchmark execution
- validate the local model endpoint separately
- do not create partial benchmark artifacts as if the run had succeeded

### Scorer failure

- keep raw predictions if they were generated
- mark metrics generation as failed
- do not patch metrics manually

### Artifact writer failure

- preserve any raw generation output if available
- fix the writer before retrying
- do not claim benchmark completion

---

## 8. Final Run Authorization Checklist

Before actual execution, all must be true:

- [ ] command verified
- [ ] config verified
- [ ] output path verified
- [ ] no paper files touched
- [ ] baseline and SRP variants defined
- [ ] dataset source identified
- [ ] endpoint reachable
- [ ] artifact contract confirmed

---

## Summary

This guide is the last preparation step before smoke execution.

If the commands, configs, endpoint, and output paths are all confirmed, the next step is to run:
- MMLU smoke first
- artifact review second
- ARC smoke third
- artifact review fourth

Only after both smoke runs succeed should full benchmark execution be considered.

