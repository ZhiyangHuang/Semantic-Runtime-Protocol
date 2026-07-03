# SRP Submission Freeze Checklist

This checklist defines the submission freeze for the first SRP paper.

The goal is to decide whether the project has reached a submission-ready state and to prevent late-stage scope drift.

## Freeze Principle

The project should freeze when the following are true:

- the paper compiles from scratch
- the evidence package is complete
- the reviewer-facing narrative is stable
- the experiment output is reproducible

At that point, further changes should be limited to submission packaging, not system expansion.

## 1. Compile Pass Checklist

The paper must compile cleanly under the intended submission target.

### Required checks

- `main_submission.tex` compiles from a clean state
- bibliography resolves without missing citation warnings
- all figure paths resolve correctly
- all table inputs resolve correctly
- no placeholder figure blocks remain in the submission target
- no unresolved `\ref` or `\cite` items remain in the final build

### Success criterion

The paper can be built from scratch without manual file edits.

### Failure signals

- missing figures
- broken table includes
- undefined references
- citation key mismatches
- stale auxiliary files causing false success

## 2. Reviewer Simulation Checklist

The submission should be readable as a reviewer-facing artifact.

### Questions to answer

- Can the reviewer identify the one main claim quickly?
- Can the reviewer inspect the main figure without reading the full repository?
- Can the reviewer see where the evidence comes from?
- Can the reviewer tell what the system does and does not claim?
- Can the reviewer understand why EQ matters?

### Success criterion

The paper communicates a narrow, defensible contribution without requiring the reader to reconstruct the system from scratch.

### Failure signals

- too much engineering history in the main text
- unclear separation between main paper and appendix material
- evidence overload without narrative compression
- no obvious answer to "what is the one key takeaway?"

## 3. Artifact Packaging Validation

The final submission package must contain a complete and stable artifact set.

### Required artifacts

- main submission `.tex`
- bibliography
- main 3-panel figure
- drift figure
- contract/commit figure
- paper tables
- quality table
- efficiency table
- guardrail table
- camera-ready table
- evidence manifest
- execution trace log
- execution trace table

### Success criterion

All paper-facing artifacts are present and point to qualified evidence.

### Failure signals

- artifact paths point to legacy or exploratory outputs
- the paper references artifacts that are not present in the repository
- there are multiple competing evidence roots

## 4. Reproducibility Audit Script

The repository should provide a reproducibility audit script that checks:

- the selected submission target
- compile integrity
- evidence artifact presence
- manifest completeness
- output directory consistency
- trace log availability

### Success criterion

The audit script can report whether the current repo state is submission-qualified.

### Failure signals

- manual inspection is required to know whether the package is ready
- the script cannot tell whether outputs are consistent
- the script does not distinguish formal evidence from exploratory results

## 5. Final Submission Zip Generator

The repository should support one command that packages the final submission.

### Package contents

- final `.tex` source
- bibliography
- required figures
- final tables
- evidence manifest
- reproducibility audit report
- short README describing how to compile and verify the package

### Success criterion

The submission archive is self-contained enough for upload and later review.

### Failure signals

- the archive omits figures or tables
- the archive depends on hidden local files
- the archive mixes formal evidence with exploratory outputs

## Freeze Decision Rule

Freeze when all five blocks pass:

1. compile pass
2. reviewer simulation
3. artifact packaging validation
4. reproducibility audit
5. submission zip generation

If any block fails, the fix should be minimal and targeted. Do not expand the system unless the failure is structural and directly blocks submission.

## Recommended Workflow

1. Run the compile check.
2. Run the reviewer simulation check.
3. Validate the artifact package.
4. Run the reproducibility audit.
5. Generate the submission zip.
6. Freeze the codebase unless a blocking error remains.

## Relation To The First Paper

The freeze checklist is part of the first paper's quality bar. It does not change the claim. It only ensures the claim is packaged in a way that a reviewer can compile, inspect, and reproduce.
