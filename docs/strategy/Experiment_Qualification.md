# Experiment Qualification

## Purpose

Experiment Qualification (`EQ`) is the readiness gate for all formal SRP paper experiments.

Its job is simple:

- verify that the experiment harness is trustworthy
- detect regressions before paper-facing runs
- prevent invalid infrastructure from producing formal evidence

For this first SRP paper, `EQ` matters more than further protocol expansion.

## Rule

Formal paper runs SHALL be launched only through the qualification gate.

If the qualification report is not `QUALIFIED`, the run is not formal evidence.

## Output

The qualification system produces one unified report with:

- per-check `PASS` or `FAIL`
- check details
- overall status:
  - `QUALIFIED`
  - `NOT_QUALIFIED`

## EQ Checks

### EQ-1 Runtime Equivalence

Goal:

- confirm that deterministic execution and backend-mediated mock execution are protocol-equivalent

Pass:

- all regression tasks report `overall_pass = true`
- `commit_decision_match = true`
- `contract_satisfaction`, `alignment`, and `drift` stay within configured tolerance

Fail:

- any regression task reports `protocol_behavior_mismatch`
- or any exit criterion fails

### EQ-2 Pipeline Consistency

Goal:

- confirm that SRP produces consistent behavior across:
  - `run_srp()`
  - `run_method()`
  - experiment summarization path

Pass:

- key protocol fields match for the same task and cycle:
  - `representation`
  - `recovered_text`
  - `state_committed`
  - `validation_contract_satisfaction`
  - `validation_alignment`
  - `validation_drift`
  - `validation_passed`

Fail:

- any key protocol field differs without an intentional reason

### EQ-3 Determinism

Goal:

- confirm that repeated harness runs with the same mock configuration are stable

Pass:

- repeated small runs produce identical summaries and detailed rows

Fail:

- repeated runs drift without configuration changes

### EQ-4 Schema Completeness

Goal:

- confirm that experiment outputs expose the minimum required paper-facing fields

Pass:

- every result row includes:
  - `task_id`
  - `method`
  - `cycle`
  - `drift`
  - `task_success`
  - `query_success`
  - `tokens`
  - `latency_seconds`
  - `state_committed`
  - `validation_contract_satisfaction`
  - `validation_alignment`
  - `validation_drift`
  - `validation_passed`

Fail:

- any required field is missing
- or a required protocol field is `None`

### EQ-5 Metric Sanity

Goal:

- confirm that the verifier still distinguishes:
  - good recovery
  - bad recovery
  - answer leakage

Pass:

- good recovery commits
- bad recovery rolls back
- leakage rolls back

Fail:

- any of those three behaviors is inverted

### EQ-6 Regression Set

Goal:

- keep a stable regression anchor for future protocol changes

Regression tasks:

- `pref_low_latency`
- `long_context_summary`
- `iterative_cycles`

Pass:

- all regression tasks remain qualified under `EQ-1`

Fail:

- any regression task loses equivalence

## Exit Criteria

The overall experiment environment is `QUALIFIED` only if:

1. `EQ-1` passes
2. `EQ-2` passes
3. `EQ-3` passes
4. `EQ-4` passes
5. `EQ-5` passes
6. `EQ-6` passes

If any check fails:

- stop formal experiment execution
- inspect the qualification report
- fix the earliest relevant cause
- rerun `EQ`

## Recommended Workflow

1. Run `Experiment Qualification`
2. Inspect the qualification report
3. If `QUALIFIED`, launch the formal experiment
4. Archive the qualification report with the experiment outputs

## Scope Rule

`EQ` is not meant to prove that every metric is theoretically perfect.

It is meant to prove that the infrastructure is stable enough that the resulting paper evidence is worth trusting.
