# LongMemEval Calibration Note

Before promoting LongMemEval to external-validity evidence, we calibrated the LongMemEval ingestion path to verify the benchmark adapter, the temporal attribution protocol, and the failure-attribution boundary.

This calibration study is intentionally separated from the final external-validation results. It does not modify the SRP mechanism, benchmark workload, baseline implementations, or random seeds.

The calibration process validates the same three independent components used for LoCoMo:

1. Adapter correctness
   - LongMemEval questions and conversation histories are transformed into SRP-compatible semantic states through the shared adapter contract.
2. Temporal attribution protocol
   - `memory_status`, `generation_status`, and `scorer_status` are kept separate so scorer disagreement is not mislabeled as a memory failure.
3. Failure decomposition
   - The calibration package decomposes errors into memory failures, generation failures, scorer mismatches, and unresolved cases.

This note belongs in the evaluation methodology or appendix, not in the paper's main results table.
