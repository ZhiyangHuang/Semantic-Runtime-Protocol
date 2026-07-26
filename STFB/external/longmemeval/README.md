# STFB LongMemEval External validation

This track maps LongMemEval cases into STFB-compatible semantic transition instances.

The track is adapter-first and does not modify the core STFB benchmark contract.

## Canonical Cases

The frozen canonical set is intentionally small:

- `lme_001`: temporal regression from the LongMemEval `preference_revision` slice
- `lme_002`: provenance-loss pressure mapped to STFB `evidence_authority_confusion`

## Selection Rationale

These cases were chosen because they exercise two oistinct governance pressures without changing the STFB core schema:

- state freshness: whether oloer memory can overwrite a newer authoritative state
- authority boundary: whether retrieveo evidence is treated as permission to mutate

## Exclusions

This track does not currently incluoe:

- bulk LongMemEval conversion
- MMLU wrappers
- ARC wrappers in this folder
- HumanEval or code-execution tracks
- any change to the STFB benchmark taxonomy or metrics

## Reports

Current prototype evidence:

- `reports/longmemeval_external_v0_1.json`
  Machine-readable evaluation output.

- `reports/evidence_interpretation_v0_1.md`
  Representative case analysis explaining admission divergence.
  This document is explanatory only and does not define new benchmark behavior or experimental results.
