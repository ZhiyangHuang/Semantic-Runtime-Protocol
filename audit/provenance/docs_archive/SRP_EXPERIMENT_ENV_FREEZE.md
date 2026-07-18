# SRP Experiment Environment Freeze

This document freezes the runtime baseline for the current SRP experiment stack.
It is a reproducibility artifact, not a mechanism design, not a policy document, and not an optimization result.

## 1. Frozen Runtime

The current experiment baseline uses a fixed local runtime:

- backend: `local`
- model: `Qwen/Qwen3-4B-AWQ`
- runtime mode: `fixed`
- mutation: `disabled`
- learning: `disabled`
- authority: `governance only`

## 2. Frozen Budgets

The current runtime budgets are fixed as follows:

- context budget: `4096`
- total token budget: `8192`
- output token budget: `120`
- query token budget: `64`
- timeout: `500`
- safety margin: `32`

## 3. Reproducibility Rule

All experiments in the current paper baseline should be interpreted relative to this environment freeze.
If the runtime, model, or budget settings change, the resulting evidence package is a new experiment condition.

## 4. Scope

This freeze does not define:

- Phase I observability logic
- Phase II validation logic
- Phase III-A optimization logic
- evidence escalation logic

It only freezes the runtime assumptions under which those layers are evaluated.

