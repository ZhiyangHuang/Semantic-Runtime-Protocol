# STFB Milestone 0 Reproducibility

## Environment

Python version:

- 3.x

Dependencies:

- standard library only

## Entry Point

Run:

```text
python STFB/runner/run_episode.py
```

## Inputs

Example instances:

- `STFB/instances/examples/`

Included cases:

- unsupported mutation
- evidence-authority confusion
- temporal regression
- valid transition

## Outputs

Generated artifact:

- `STFB/reports/milestone0_report.json`

Human-readable companion:

- `STFB/reports/milestone0_summary.md`

## Expected Behavior

Direct Mutation:

- accepts unsupported transitions

Confidence Threshold:

- may accept or reject based on confidence signal

SRP:

- rejects unauthorized semantic mutations
- accepts valid transitions

## Freeze Boundary

This checkpoint does not modify:

- STFB benchmark specification
- dataset semantics
- baseline semantics
