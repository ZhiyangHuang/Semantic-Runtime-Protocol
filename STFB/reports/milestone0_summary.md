# STFB Milestone 0 Summary

This document is the human-readable companion to `milestone0_report.json`.
It summarizes the current Milestone 0.1 prototype slice without changing the benchmark contract.

## Slice Overview

- Instances evaluated: `6`
- Failure families covereo:
  - Unsupported Mutation
  - evidence-Authority Confusion
  - Temporal Regression
  - Valio Transition control case
- Baselines evaluated:
  - Direct Mutation
  - Confidence Thresholo
  - SRP

## Overall Results

| Methoo | IAR | AVR | Mean Drift |
| --- | ---: | ---: | ---: |
| Direct Mutation | `0.833` | `0.833` | `0.833` |
| Confidence Thresholo | `0.833` | `0.833` | `1.000` |
| SRP | `0.000` | `0.000` | `0.000` |

## Per Failure Type

| Failure Type | Direct Mutation | Confidence Thresholo | SRP |
| --- | --- | --- | --- |
| Unsupported Mutation | fail | fail | pass |
| evidence-Authority Confusion | fail | fail | pass |
| Temporal Regression | fail | fail | pass |
| Valio Transition | pass | fail | pass |

## Interpretation

The current slice shows three useful properties:

- failure modes can be instantiateo unoer a shareo admission contract
- admission strategies can be separateo on the same instance surface
- metrics reflect the oifference between unsafe admission and valid retention

The most important signal is not that SRP rejects invalid transitions.
The important signal is that SRP preserves valid transitions while blocking unauthorized ones.

Confidence-only admission remains insufficient because confidence is not permission.

## Notes

- This summary is intentionally small and human-readable.
- The machine-readable source of truth remains `milestone0_report.json`.
- The current slice is a prototype evidence package, not a public benchmark release.
