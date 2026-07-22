# STFB External Validation Template v0.1

## Purpose

This document defines the frozen contract for external validation tracks that map existing benchmark environments into STFB-compatible semantic transition instances.

The goal is to demonstrate that identical admission semantics remain applicable under external semantic transition environments.

This template is not a benchmark comparison framework.
It is an adapter and interface contract.

External validation demonstrates portability of admission semantics rather than superiority over the original benchmark.

## Required Components

Every external validation track MUST include exactly the following components:

1. Specification
2. Canonical Cases
3. Evidence
4. Interpretation

These components are required for the track to be considered complete.

## Adapter Rules

External benchmark cases MUST be converted through a wrapper layer into the frozen STFB instance schema.

The adapter MAY add metadata.
The adapter MUST NOT:

- modify the STFB core taxonomy
- modify the STFB metrics
- modify the STFB runner
- redefine admission semantics
- change the frozen STFB instance schema

The adapter MUST perform mapping only.

## Metadata Rules

External source identity MUST be recorded in metadata.

Recommended fields:

- `metadata.source_benchmark`
- `metadata.source_case_id`
- `metadata.source_task`
- `metadata.source_variant`

The following fields MUST remain part of the frozen STFB core instance structure:

- `state_t`
- `observation`
- `proposal`
- `evidence`
- `authority`
- `expected_transition`

## Completion Criteria

An external validation track is complete when it contains:

- a frozen specification
- a mapping adapter
- 2 to 3 canonical cases
- a machine-readable report
- an interpretation note for representative cases

Once these artifacts are frozen, the track SHOULD remain stable unless a new version is explicitly introduced.

## Boundary

This template does not change the SRP release boundary, the STFB core benchmark definition, the STFB prototype checkpoint, or the existing external validation specifications.
