# STFB ARC External Validation

This track maps ARC cases into STFB-compatible semantic transition instances.

The track is adapter-first and does not modify the core STFB benchmark contract.

## Canonical Cases

The frozen canonical set is intentionally small:

- `arc_001`: unsupported inference mapped to STFB `unsupported_mutation`
- `arc_002`: valid reasoning transition as a control case

## Selection Rationale

These cases were chosen because they exercise two complementary pressures under the same wrapper contract:

- unsupported inference: a plausible-looking reasoning transition without mutation authority
- valid reasoning: a supported transition that should remain admissible

## Exclusions

This track does not currently include:

- bulk ARC conversion
- MMLU wrappers in this folder
- HumanEval or code-execution tracks
- any change to the STFB benchmark taxonomy or metrics

## Reports

Current prototype evidence:

- `reports/arc_external_v0_1.json`
  Machine-readable evaluation output.

- `reports/evidence_interpretation_v0_1.md`
  Representative case analysis explaining admission divergence.
  This document is explanatory only and does not define new benchmark behavior or experimental results.

