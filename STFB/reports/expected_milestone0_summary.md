# STFB Milestone 0 Expected Summary

This file is a qualitative regression reference for the current Milestone 0 prototype checkpoint.
It is not a replacement for `milestone0_report.json`.

## Expected Qualitative Behavior

- Direct Mutation commits unsupported transitions.
- Confidence Threshold follows the confidence signal and may still admit unsafe transitions.
- SRP rejects unauthorized semantic mutations.
- SRP accepts valid transitions.

## Expected Metric Shape

The prototype slice should continue to show the following rough pattern:

| Method | Expected IAR | Expected AVR | Expected Mean Drift |
| --- | ---: | ---: | ---: |
| Direct Mutation | high | high | high |
| Confidence Threshold | high | high | high |
| SRP | zero | zero | zero |

## Regression Check

If a future code change materially changes this pattern, the change should be treated as a checkpoint review event rather than a silent benchmark update.
