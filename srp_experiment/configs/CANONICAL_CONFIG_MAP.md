# Canonical Config Map

This file records which configs are canonical, which are secondary templates, and which are exploratory or legacy-support plans.

## Tier 1: Canonical Public-Benchmark Configs

These are the main configs for the current LongBench-backed semester phase.

- `longbench_v2_multimodel_100_1000_smoke.json`
  - safest startup config
  - use this first when validating a model/backend pairing

- `longbench_v2_multimodel_100_1000.json`
  - main reusable long-horizon public-benchmark config
  - use this for repeat-aware formal public-benchmark runs

## Tier 2: Canonical Local Paper Package

- `first_paper_formal_local.json`
  - canonical local paper-facing config
  - use this for the current local formal evidence package tied to the first paper draft

## Tier 3: Secondary Templates

- `first_paper_priority_local.json`
  - narrower priority rerun plan
  - preserve, but treat as subordinate to `first_paper_formal_local.json`

- `local_batch.json`
  - generic local template

- `openai_batch.json`
  - generic OpenAI template

- `default_batch.json`
  - generic fallback example

## Tier 4: Exploratory / Historical Support

- `comparison_pack_local.json`
- `risk_test_srp_vs_hybrids_5_7.json`
- `risk_test_refactored_srp_vs_hybrids_5_7.json`

These are preserved for diagnostics and history, but they should not drive the current paper unless the scope is explicitly widened.

## Tier 5: Generated Session Artifacts

- `generated/*.json`

These configs are valid run inputs, but they are session products created by the launcher. They should not be treated as hand-maintained canonical experiment plans.

## Selection Rule

If you are uncertain, choose in this order:

1. `longbench_v2_multimodel_100_1000_smoke.json`
2. `longbench_v2_multimodel_100_1000.json`
3. `first_paper_formal_local.json`

Only drop to lower tiers if the canonical tier does not match the question you are trying to answer.
