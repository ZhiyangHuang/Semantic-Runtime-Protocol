# SRP v1.0.0 - Semantic Runtime Protocol Evidence Release

This release freezes the first audited benchmark evidence package for Semantic Runtime Protocol (SRP).

## Included Benchmarks

- **MMLU v3** - General knowledge reasoning (`accuracy`)
- **ARC v1** - Scientific reasoning (`accuracy`)
- **LongMemEval** - Official LongMemEval evaluation with a separate shared benchmark alignment layer (`official scorer authority preserved`)
- **HumanEval v1** - Code generation benchmark evaluated with sandboxed execution (`pass@1`)

## Release Status

- Release evidence: `RELEASE_EVIDENCE_READY`
- Benchmark artifacts: audited
- Prompt leakage audits: passed
- Release manifest: frozen
- Provenance: preserved

## Documentation

- Benchmark reports: `docs/benchmarks/`
- Release documentation: `docs/release/`
- Release manifest: `audit/release_manifest.json`

## Reproducibility

The benchmark artifacts included in this release are frozen. Future evaluations will be published as new versioned artifacts rather than replacing the artifacts associated with this release.

**Release tag:** `srp-v1.0.0`

