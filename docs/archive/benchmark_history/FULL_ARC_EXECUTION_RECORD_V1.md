# Full ARC Execution Record V1

Date: 2026-07-21

This record captures the authorized full ARC execution scope for the current release branch.

## Authorization Basis

- `FULL_BENCHMARK_EXECUTION_AUTHORIZATION_CHECKLIST.md`
- `BENCHMARK_PHASE_STATUS_SUMMARY.md`
- `ARC_PRE_FLIGHT_AUDIT.md`

Authorization status at time of run:
- `AUTHORIZED`

## Execution Scope

- benchmark: `ARC`
- subset: `ARC-Easy`
- split: `test`
- dataset source: `hf:allenai/ai2_arc`
- data_root: `hf:allenai/ai2_arc|ARC-Easy|test`
- sample policy: full dataset for the selected subset
- variants: `baseline`, `srp`

## Configuration

- model: `Qwen/Qwen3-4B-AWQ`
- prompt format: `arc_mcq_v1`
- temperature: `0.0`
- max output tokens: `8`
- system prompt: `Answer with the single best choice label only.`
- srp mode: `context_recovery`
- output directory: `experiments/results/arc_full_v1/`

## Execution Notes

- the full ARC run must not overwrite `arc_smoke`
- the run must preserve raw predictions, metrics, metadata, and report artifacts
- the run must not modify `paper/` or evidence manifests

