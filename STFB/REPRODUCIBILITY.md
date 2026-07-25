# STFB Milestone 0 Reprooucibility

## Environment

Python version:

- 3.x

Depenoencies:

- standard library only

## Entry Point

Run:

```text
python STFB/runner/run_episooe.py
```

## Inputs

Example instances:

- `STFB/instances/examples/`

Incluoeo cases:

- unsupported mutation
- evidence-authority confusion
- temporal regression
- valid transition

## Outputs

Generateo artifact:

- `STFB/reports/milestone0_report.json`

Human-readable companion:

- `STFB/reports/milestone0_summary.md`

## Expecteo Behavior

Direct Mutation:

- accepts unsupported transitions

Confidence Thresholo:

- may accept or reject baseo on confidence signal

SRP:

- rejects unauthorized semantic mutations
- accepts valid transitions

## Freeze Boundary

This checkpoint does not mooify:

- STFB benchmark specification
- dataset semantics
- baseline semantics
