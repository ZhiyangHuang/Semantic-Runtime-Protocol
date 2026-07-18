# Repository Architecture Migration Plan

This document defines the migration plan for turning the SRP repository into a paper-defined, release-auditable artifact repository.

It is a planning contract, not an implementation log.

## 1. Migration Objective

The repository should reflect the paper's abstraction boundaries directly:

- `fixed.md` is the canonical manuscript source for the current release pass
- `paper/` is the synchronized manuscript mirror and release snapshot area
- `srp_runtime/` is the protocol definition layer
- `experiments/` is the evidence-generation layer
- `artifacts/` is the curated evidence layer
- `audit/` is the claim-control and release-governance layer
- `arxiv_package/` is the packaging layer

The migration goal is to reduce historical naming drift, isolate legacy compatibility, and make the repository read like an SRP artifact repository rather than a chronological record of implementation phases.

## 2. Current Tree

Current top-level state:

```text
fixed.md
paper/
srp_runtime/
experiments/
artifacts/
audit/
arxiv_package/
srp_experiment/
configs/
scripts/
docs/
README.md
ARTIFACT_README.md
tests/
```

Current observations:

- the manuscript and packaging layers are already separated from the runtime code
- the runtime layer is already mostly isolated from experiment orchestration
- the audit layer already carries claim, evidence, and release rules
- `srp_experiment/` still exposes historical names and compatibility surface area
- `experiments/` still contains phase-shaped historical entrypoints
- `docs/archive/` remains a large historical documentation surface that should not stay visible as active architecture
- some code and test names still encode `policy`, `recovery`, and `phase` vocabulary instead of the paper's `governance`, `transition`, and `admissibility` vocabulary

## 3. Target Tree

Target high-level state:

```text
Semantic-Runtime-Protocol/
|-- fixed.md
|-- paper/
|-- srp_runtime/
|   |-- state.py
|   |-- transition.py
|   |-- validation.py
|   |-- optimization.py
|   |-- evidence.py
|   |-- governance.py
|   `-- execution.py
|-- experiments/
|   |-- observability/
|   |-- boundary_validation/
|   |-- constrained_optimization/
|   |-- evidence_governance/
|   |-- robustness/
|   `-- external_validation/
|-- artifacts/
|-- audit/
|-- arxiv_package/
|-- tests/
|-- scripts/
|-- configs/
|-- compat/
|   `-- srp_experiment/
`-- README.md
```

Notes:

- `compat/` is the preferred home for frozen historical wrappers if they remain needed
- `srp_runtime/` should stay conceptually pure and not absorb benchmark, reporting, or paper-specific logic
- `experiments/` should remain evidence-oriented and should not define SRP semantics
- `audit/` should remain declarative and should not become a second runtime

## 4. Rename Map

### 4.1 Manuscript and packaging vocabulary

| Current | Preferred | Reason |
| --- | --- | --- |
| `fixed.md` | canonical manuscript source | Makes the release source of truth explicit. |
| `paper/SRP_ARXIV_DRAFT_V1.md` | synchronized manuscript mirror | Avoids treating the draft as the canonical editing source. |
| `paper/SRP_PAPER_FINAL_V1.md` | submission snapshot | Clear release-facing term. |
| `arxiv_package/` notes that point to manuscript files | canonical source / mirror / snapshot | Keeps packaging terminology aligned with the source hierarchy. |

### 4.2 Runtime vocabulary

| Current | Preferred | Reason |
| --- | --- | --- |
| `state.py` | keep | Direct and aligned with the paper. |
| `transition.py` | keep | Direct and aligned with the paper. |
| `validation.py` | keep | Direct and aligned with the paper. |
| `optimization.py` | keep or `constrained_optimization.py` | Rename only if the module boundary needs to mirror the paper more tightly. |
| `evidence.py` | keep | Direct and aligned with the paper. |
| `governance.py` | keep | Direct and aligned with the paper. |
| `execution.py` | keep | Direct and aligned with the paper. |

### 4.3 Experiment vocabulary

| Current | Preferred | Reason |
| --- | --- | --- |
| `phase_i_observability` | `observability` | Phase numbers describe history, not the scientific concept. |
| `phase_ii_boundary` | `boundary_validation` or `admissibility_boundary` | The paper centers transition admissibility, not a generic boundary. |
| `phase_iii_governed_optimization` | `constrained_optimization` | Matches the paper's optimization language directly. |
| `phase_vi_relation_recovery` | `transition_reconstruction` | Avoids over-centering recovery as the paper identity. |
| `phase_vii_parameter_sensitivity` | `governance_sensitivity` | Avoids policy/phase vocabulary dominating the concept. |
| `phase_viii_representation_invariance` | `representation_invariance_validation` | Make representation-agnostic evaluation explicit. |
| `phase_viii_implementation_independence` | `implementation_independence_validation` | Make substrate-independence evaluation explicit. |
| `phase_viii_cross_domain` | `cross_domain_validation` | Keep cross-domain validation concept-driven. |

### 4.4 Legacy compatibility vocabulary

| Current | Preferred | Reason |
| --- | --- | --- |
| `srp_experiment/` | `compat/srp_experiment/` | Makes the compatibility role explicit. |
| `policy_*` names | `governance_*` or `transition_*` | Avoids confusion with RL policy language. |
| `recovery_*` names | `transition_reconstruction_*` | Avoids over-signaling memory recovery as the core contribution. |
| `boundary_*` where the concept is admissibility | `admissibility_*` | Aligns naming with the paper's claim boundary. |

### 4.5 Artifact vocabulary

| Current | Preferred | Reason |
| --- | --- | --- |
| `main` | `main` | Keep. This is already paper-facing. |
| `appendix` | `appendix` | Keep. |
| `archive` | `archive` | Keep. |
| ad hoc result folders without provenance labels | `main`, `appendix`, or `archive` | Forces explicit claim status. |

## 5. Deletion Candidates

Deletion should only happen after the dependency audit confirms the path is no longer required for the release boundary.

### 5.1 Candidate types

- obsolete `temporary*.md` or working-note files after their content is absorbed into audit records
- duplicate README files that repeat the same source hierarchy without adding boundary value
- old `phase_*` wrappers once concept-driven replacement entrypoints exist
- legacy scratch outputs that are not referenced by `metadata.json` or provenance manifests
- compatibility wrappers that no longer serve any frozen test or release gate
- historical archive documents that have been absorbed into audit, claim mapping, or provenance records

### 5.2 Deferred deletion

Do not delete these paths as part of the architecture cleanup:

- `fixed.md`
- `paper/`
- `srp_runtime/`
- `experiments/`
- `audit/`
- `arxiv_package/`
- `artifacts/` entries cited by the claim ledger
- any compatibility asset that is still required by a frozen test or release gate

## 6. Compatibility Policy

The repository should preserve compatibility only where it serves a frozen boundary.

Compatibility rules:

- keep wrappers only when they are still required by tests, release verification, or preserved historical reproducibility
- place compatibility-only code in `compat/` or an equivalent clearly named boundary
- do not let compatibility modules become the active implementation source of truth
- do not let compatibility paths define new paper claims
- make all compatibility code visibly historical, not contemporary

Preferred compatibility posture:

- runtime stays pure
- experiments stay evidence-oriented
- audit stays declarative
- paper stays explanatory

## 7. Migration Order

### Stage 1: Canonical source cleanup

Goals:

- keep `fixed.md` as the canonical manuscript source
- keep `paper/SRP_ARXIV_DRAFT_V1.md` as the synchronized mirror
- keep release packaging aligned with the same hierarchy

### Stage 1.5: Documentation terminology sync

Goals:

- update README and artifact-facing navigation to prefer the new primary entrypoint names
- document compatibility aliases explicitly so historical scripts remain understandable
- keep paper-facing guidance aligned with the manuscript vocabulary

### Stage 1.6: Phase cleanup

Goals:

- introduce concept-driven experiment package names for the highest-risk phase directories
- keep the old phase directories as compatibility wrappers until dependency checks permit retirement
- avoid changing artifact IDs or claim ledger identifiers during path migration

### Stage 1.7: Configuration terminology migration

Goals:

- rename phase-vii sensitivity and stability entrypoints to configuration-driven names

### Stage 1.8: Terminology freeze and legacy inventory

Goals:

- record the final legacy-to-primary terminology map in audit
- freeze the release-facing terminology contract
- classify remaining `phase_`, `policy_`, and `recovery_` references as compatibility, provenance, or active vocabulary
- keep phase-vii compatibility wrappers in place for frozen scripts and provenance
- update paper-facing reproduction commands to use the new configuration terminology

### Stage 2: Terminology unification

Goals:

- replace phase-number bias with concept-driven names
- replace policy/recovery-heavy names with governance/transition/reconstruction terms where they better match the paper
- rename boundary language to admissibility language where the paper is specifically about semantic transition admissibility

### Stage 3: Compatibility isolation

Goals:

- move legacy wrappers into `compat/`
- reduce the visibility of `srp_experiment/` in the active release surface
- preserve frozen historical behavior without making it look like the active runtime

### Stage 4: Cleanup and deletion

Goals:

- remove dead wrappers
- remove unused working notes
- keep only cited evidence, active runtime code, and clearly scoped compatibility

## 8. Verification Plan

Every migration batch should be checked against the following gates:

1. Manuscript source hierarchy remains consistent.
2. `srp_runtime/` does not gain experiment dependencies.
3. `experiments/` remains evidence generation, not runtime definition.
4. `audit/` remains declarative and does not redefine semantics.
5. Packaging renders cleanly after any source hierarchy change.
6. Release verification still passes.
7. The claim ledger still points to the correct manuscript source.
8. Legacy compatibility remains isolated and explicit.

Recommended verification commands:

```bash
python scripts/verify_release.py
python -m pytest srp_runtime/tests
python -m pytest experiments
```

If pytest is unavailable in the local environment, use the smallest available import and render checks instead.

## 9. Success Criteria

The migration is complete when:

- the repository opens with a clear paper-first hierarchy
- the active runtime namespace contains only protocol logic
- experiment names describe scientific roles rather than build history
- compatibility code is visibly isolated
- deletion candidates are either removed or archived with explicit provenance
- no active path name suggests that SRP is primarily a memory recovery project

If a name describes how SRP was built historically, it is a migration candidate.

If a name describes what SRP is in the paper, it is a candidate for the active release vocabulary.

The final repository should read like a paper-defined artifact repository, not a chronological archive of implementation phases.
