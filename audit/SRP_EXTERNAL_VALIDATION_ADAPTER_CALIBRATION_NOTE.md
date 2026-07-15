# SRP External Validation Adapter Calibration Note

This note records the first public-benchmark ingestion slice for SRP.
It is a calibration artifact, not a paper result, not a benchmark claim, and not a runtime policy.

## 1. Why This Note Exists

The LoCoMo MVP slice confirmed that the external-validation pipeline can ingest the official `locomo10.json` format, pass cases through the semantic adapter layer, and produce a complete record package.
However, the current evaluator and answer-extraction protocol still show a mismatch between semantic-state metrics and public-benchmark answer scoring.

That means the first LoCoMo pass is useful for adapter calibration, but it is not yet safe to promote as a main external-validity result.

## 2. What Worked

- Official LoCoMo ingestion from `data/locomo/locomo10.json`
- Adapter-layer conversion into SRP semantic state
- Shared baseline interface across:
  - `full_context`
  - `sliding_window`
  - `vector_rag`
  - `srp`
- End-to-end record export and report generation

## 3. What Did Not Yet Match

The current slice showed a mismatch between:

- semantic recovery metrics
- answer-similarity scoring
- public-benchmark expectations

In particular:

- `full_context` achieved perfect semantic-state metrics but only moderate answer similarity
- `srp` showed better structure recovery than retrieval-only baselines, but the absolute answer score is still not aligned with a benchmark-grade public claim

This indicates that the benchmark adapter, answer extraction, and official scoring protocol still need calibration before the results should be used as paper evidence.

## 4. Interpretation Boundary

The LoCoMo slice should currently be read as:

> benchmark ingestion validated, metric alignment still under calibration

It should **not** be read as:

> public-benchmark validation complete

## 5. Next Calibration Steps

1. Align the answer-scoring path more closely with LoCoMo's official evaluation protocol.
2. Validate the adapter output against a few manually inspected conversations and QA pairs.
3. Re-run the LoCoMo slice only after the adapter and evaluator agree on the expected answer behavior.
4. Use the manual sanity harness at `experiments/results/external_validation_locomo_sanity/` to inspect per-case adapter behavior, answer attribution traces, the scoring calibration matrix, and the frozen temporal attribution protocol before any public-benchmark claim is promoted.
5. Reinterpret the frozen LoCoMo MVP slice through the calibration-aware rerun at `experiments/results/external_validation_locomo_calibration_aware/` before any external-validity claim is promoted.
6. Consult `SRP_LOCOMO_CALIBRATION_NOTE.md` for the paper-facing calibration summary.
7. Use `SRP_LONGMEMEVAL_CALIBRATION_NOTE.md` as the next calibration checkpoint before external-validity promotion.
8. Promote the slice to the main external-validity section only after calibration stabilizes.

## 6. Relation to the Paper

This note is intentionally kept outside the main result narrative.
It protects the paper from overstating external validity before the public-benchmark interface has been calibrated.
