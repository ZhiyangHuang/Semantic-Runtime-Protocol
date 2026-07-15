# LoCoMo Calibration Note

Before public benchmark validation, we calibrated the LoCoMo ingestion path to verify the benchmark adapter, the temporal attribution protocol, and the failure-attribution boundary.

This calibration study was intentionally separated from the final external-validation results. It did not modify the SRP mechanism, benchmark workload, baseline implementations, or random seeds.

The calibration process validated three independent components:

1. Adapter correctness
   - The LoCoMo data adapter was verified through semantic invariant checks, ensuring that benchmark conversations and questions were transformed into SRP-compatible semantic states.
2. Temporal attribution protocol
   - We separated `memory_status`, `generation_status`, and `scorer_status` so scorer disagreement would not be misattributed to memory failure.
3. Failure decomposition
   - The calibration report decomposes errors into memory failures, generation failures, scorer mismatches, and unresolved cases.

This note belongs in the evaluation methodology or appendix, not in the paper's main results table.
