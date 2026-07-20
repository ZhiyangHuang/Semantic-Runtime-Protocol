# Boundary Reporting

This module generates reproducible governance boundary reports for Semantic Runtime Protocol.

It is not a benchmark implementation.

The purpose is to produce auditable artifacts describing:

- admissible transitions
- rejected transitions
- authority separation
- replay consistency

## Scope

This package is a v1.1 prototype scaffold. It defines the artifact contract and module boundaries for reproducible boundary-report generation work.

It intentionally does not implement:

- benchmark loading
- LLM API integration
- retrieval backends
- vector databases
- optimization search
- dashboards

## Output Contract

Expected report bundle:

```text
boundary_report/
├── cases.jsonl
├── decisions.jsonl
├── summary.json
├── report.md
└── metadata.json
```

## Entry Point

Prototype CLI:

```text
python -m experiments.validation.boundary_reporting.runner \
  --cases fixtures/minimal_cases.jsonl \
  --output results/ \
  --adapter fixture \
  --contract runtime_contract_id \
  --seed 0
```

## Adapter Layer

The adapter layer maps raw evaluation slices into the shared `BoundaryCase` contract.

It exists so multiple slices can share the same evaluator and reporter without turning the module into a benchmark framework.

## Matrix Layer

The matrix layer checks adapter contract consistency across multiple slices.

Boundary reporting evaluates reproducibility of governance artifacts, not the superiority of semantic transition generators.

## Audit Invariant

`Adapter != Governance`

Adapters translate raw slices into `BoundaryCase` records.
They do not decide admissibility, authority, or execution.
