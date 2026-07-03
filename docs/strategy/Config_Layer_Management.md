# Config Layer Management

This document explains how the config layer should be interpreted during the current paper cycle.

## Main Principle

Configs should answer different planning questions, but they should not compete as equal "main configs."

## Current Canonical Roles

### Public-Benchmark Startup

- `longbench_v2_multimodel_100_1000_smoke.json`

Use when:

- verifying a new backend
- verifying a new model
- verifying that the launcher and batch path still work

### Public-Benchmark Main Run

- `longbench_v2_multimodel_100_1000.json`

Use when:

- running the main LongBench-based repeated public-benchmark plan

### Local Paper Package

- `first_paper_formal_local.json`

Use when:

- producing the current local paper-facing figure/table package

## Secondary Roles

- `first_paper_priority_local.json` is a narrower support config, not the main local formal package
- `local_batch.json` and `openai_batch.json` are infrastructure templates
- `default_batch.json` is a fallback example

## Exploratory Roles

- comparison and hybrid-risk configs remain useful for diagnostics and history
- they should not redefine the current paper scope by accident

## Generated Config Rule

Launcher-generated configs are run records, not planning documents.

They should be preserved for auditability, but semester planning should still point back to the canonical hand-maintained configs.
