# Configs Index

This folder stores reusable experiment configurations.

Not every config here has the same status.

## Canonical Configs For The Current Paper

- `longbench_v2_multimodel_100_1000.json`
  - main reusable public-benchmark config
- `longbench_v2_multimodel_100_1000_smoke.json`
  - safest LongBench smoke config
- `first_paper_formal_local.json`
  - canonical local formal paper-facing batch

Canonical decision table:

- [CANONICAL_CONFIG_MAP.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/configs/CANONICAL_CONFIG_MAP.md)

## Secondary But Still Useful

- `first_paper_priority_local.json`
  - narrower local plan for paper-priority reruns
- `local_batch.json`
  - general local batch template
- `openai_batch.json`
  - general OpenAI batch template
- `default_batch.json`
  - generic batch fallback

## Exploratory / Legacy Comparison Configs

- `comparison_pack_local.json`
- `risk_test_srp_vs_hybrids_5_7.json`
- `risk_test_refactored_srp_vs_hybrids_5_7.json`

These should not be treated as the current main-paper formal path unless the paper scope is explicitly expanded.

## Generated Configs

- `generated/`

This directory stores launcher-generated session configs.
They are valid run inputs, but they are session artifacts rather than hand-maintained canonical plans.

Generated-config notes:

- [generated/README.md](C:/Users/ZhiyangHuang/Semantic-Runtime-Protocol/srp_experiment/configs/generated/README.md)

## Rule

If you are unsure which config to use:

1. use `longbench_v2_multimodel_100_1000_smoke.json` for safe startup
2. use `longbench_v2_multimodel_100_1000.json` for the main public-benchmark long-horizon plan
3. use `first_paper_formal_local.json` for the current local paper-facing package
