# Repository Consolidation Audit

This document tracks the Phase 6 repository consolidation effort.
Its purpose is to keep the repository aligned with the frozen v1 evidence chain while removing historical dependency arrows.

## 1. Scope

The consolidation target is not "deletion for its own sake".
The target is a repository that retains only the live code needed for the paper, the frozen evidence chain, and ongoing governance.

Frozen boundaries:

- `paper/` is frozen for v1
- `audit/` is the governance ledger
- `artifacts/` stores curated evidence
- `experiments/real_world_validation/` contains the real-validation extension
- `LongMemEval` remains protocol-ready until real data exists

## 1.1 Migration Principles

The consolidation work follows five fixed principles:

1. Do not migrate code merely to make deletion easier; only move code that still serves the paper, runtime, or reproducibility.
2. Keep a single source of truth for protocol logic in `srp_runtime/`.
3. Keep experiment-specific shared helpers in `experiments/common/` or equivalent live utility layers.
4. Treat runtime imports, tooling imports, and test imports as blocking dependencies; treat markdown, audit, and historical mentions as non-blocking provenance.
5. Keep every migration batch small, reversible, and verifiable with `verify_release.py`, `run_reproduction.py --core`, and the dependency audit.

## 2. Live Code Map

These areas are still active because they support the paper, reproducibility, or governance.

| Module / Area | Status | Reason |
| --- | --- | --- |
| `srp_runtime/` | Live | Core runtime implementation |
| `experiments/` | Live | Reproducible experiment and validation entrypoints |
| `experiments/srp_runtime_legacy/` | Live support | Transitional compatibility namespace for legacy harness consolidation |
| `experiments/real_world_validation/` | Live | Current real-validation extension |
| `artifacts/` | Live | Curated evidence and dependency audit outputs |
| `audit/` | Live | Claim, evidence, freeze, and promotion governance |
| `paper/` | Live | Frozen manuscript and release-facing narrative |
| `configs/` | Live | Frozen runtime and experiment configurations |
| `scripts/` | Live | Release and dependency verification tooling |
| `tests/` | Live | Verification and regression coverage |
| `arxiv_package/` | Live | Release packaging support |

## 3. Legacy Modules

These areas are frozen historical layers or archival material.

| Module / Area | Status | Reason |
| --- | --- | --- |
| `srp_experiment/` | Legacy | Frozen legacy experiment and evidence layer |
| `audit/provenance/docs_archive/` | Legacy | Historical research materials preserved for provenance |

## 4. Dependency Elimination Targets

These dependencies must be removed, isolated, or explicitly frozen before `docs/` and `srp_experiment/` can be safely deleted.

Priority order:

- `P0`: runtime imports
- `P1`: tooling imports
- `P2`: test imports
- `P3`: markdown, audit, and historical references, which are informative but non-blocking

Deletion readiness rule:

- `P0` and `P1` must reach zero before deletion is allowed
- `P2` must be classified into live, legacy compatibility, or historical/prototype assets
- any remaining `P2` surface that is intentionally preserved must be frozen and documented as a non-live compatibility asset
- `P3` may remain as provenance after live dependency cleanup

### `docs/`

Blocking dependency:

- `scripts/verify_release.py` now requires `audit/release_manifest.json` and `audit/provenance/README.md`

### `srp_experiment/`

Blocking dependency categories:

- `P2` test imports
- legacy helper references in historical docs

Runtime imports have been cleared in the current scan.
Tooling imports have been cleared in the current scan.

Current dependency audit baseline:

- total reference hits: `360`
- `docs_archive` hits: `45`
- `import` hits: `22`
- `srp_experiment` hits: `287`

Current dependency audit outcome:

- `P0 runtime imports`: `0`
- `P1 tooling imports`: `0`
- `P2 test imports`: `22`
- the remaining `P2` references are frozen compatibility and prototype assets rather than live migration debt
- only non-blocking `P3` references remain in audit, markdown, and historical material

Dependency audit source:

- `artifacts/dependency_audit/import_dependency_report.json`
- `artifacts/dependency_audit/import_dependency_report.md`

## 5. Unused Code Audit Status

No directory is yet confirmed deletable purely from this audit.
The current state is:

- `audit/provenance/docs_archive/` is legacy provenance, not a release gate dependency
- `srp_experiment/` is legacy, but its core runtime/tooling edges are gone
- the remaining `srp_experiment` references are frozen test/prototype assets, not live runtime dependencies
- the repository therefore has a delete candidate plus preserved compatibility assets, not yet confirmed dead code

Confirmed deletable status will only be assigned after:

- the release gate is manifest-driven and the legacy trees are isolated into provenance or archived compatibility assets
- preserved compatibility assets are explicitly marked and excluded from live dependency checks
- the dependency audit is rerun and the remaining references are only approved provenance references

## 6. Claim -> Experiment -> Code Coverage

The repository should keep only code that participates in an explicit claim-to-evidence path.

Current coverage pattern:

- paper claim
- claim matrix
- selection policy
- real dataset slice
- SRP runner
- baseline comparison
- failure analysis
- scientific report
- claim support audit
- freeze point

This means the live code should be traceable from claim to artifact.
Anything that cannot be placed on that path is a removal candidate.

## 7. Repository Consolidation Tasks

1. Freeze the remaining `P2` test assets into explicit legacy / historical categories.
2. Keep the release gate manifest-driven and prohibit hardcoded archive dependencies.
3. Re-run the dependency audit and compare the blocking hit count against the current baseline.
4. Retire or rehome historical archive material.
5. Delete `docs/` only when it becomes a dead tree.
6. Delete the core `srp_experiment/` implementation only when the legacy compatibility surface has been isolated or archived.
7. Preserve any intentionally frozen compatibility assets in their own documented boundary.

## 8. Final Deletion Decisions

The following decisions are currently frozen:

- keep `srp_runtime/`
- keep `experiments/`
- keep `artifacts/`
- keep `audit/`
- keep `paper/`
- keep `configs/`
- keep `scripts/`
- keep `tests/`
- keep `arxiv_package/`
- keep the frozen `srp_experiment` compatibility and prototype assets until the deletion-readiness audit approves retirement or archival
- keep `docs/` for now until archive references are rehomed or archived into provenance-only status

Deletion is deferred, not denied.
The only acceptable trigger for deletion is the disappearance of all live dependency arrows into the legacy trees.

