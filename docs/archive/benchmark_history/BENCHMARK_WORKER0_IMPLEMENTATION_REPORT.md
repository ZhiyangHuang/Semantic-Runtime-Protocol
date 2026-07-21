# Worker 0 Implementation Report

## Decision

The shared benchmark infrastructure layer was placed under `experiments/benchmarks/common/`.

### Why this location

- It keeps the new benchmark foundation generic instead of tying it to `external_validation`.
- It avoids overloading `experiments/external_validation/` with non-external benchmark responsibilities.
- It gives MMLU, ARC, and HumanEval a single reusable import path.
- It preserves the existing LongMemEval code path unchanged.

## Implemented Shared Contracts

- `BenchmarkAdapter` protocol
- `BenchmarkCase` schema
- `BenchmarkPrediction` schema
- `BenchmarkRunConfig` schema
- `BenchmarkMetricsSchema`
- `BenchmarkRunBundle`
- `BenchmarkRunner`
- `write_benchmark_artifact`
- `render_benchmark_report`

## Validation

- Added shared tests for runner execution, artifact writing, and case serialization.
- No benchmark-specific implementation was added.
- No paper-facing files were modified.

## Migration Note

Future adapters can depend on:
- `experiments/benchmarks/common/schema.py`
- `experiments/benchmarks/common/runner.py`
- `experiments/benchmarks/common/artifact.py`
- `experiments/benchmarks/common/report.py`
- `experiments/benchmarks/common/metrics.py`

The existing LongMemEval implementation remains the current production path and should not be refactored as part of this worker.

