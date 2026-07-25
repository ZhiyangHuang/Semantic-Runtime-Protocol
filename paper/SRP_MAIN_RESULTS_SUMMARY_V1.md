# SRP Main Results Summary V1

Two-track guide for the current SRP release.

## STFB Standard Track

Use this track for the frozen benchmark contract and its core evidence.

- `RQ1`: controlled semantic transition failures under the STFB contract
- `RQ2`: external validation under the same frozen contract
- Core sources: `STFB/README.md`, `paper/docs/plans/STFB_SPEC.md`, `paper/docs/plans/STFB_ROADMAP.md`

## Supplementary Protocol Track

Use this track for supporting governance and runtime evidence.

- `RQ1b`: evidence-authority separation
- `RQ3`: divergence behavior
- `RQ4`: capability trade-offs and runtime integration
- Core sources: `experiments/validation/evidence_authority_separation/README.md`, `paper/SRP_MANUSCRIPT_V1.md`, `paper/docs/release/EVIDENCE_SURFACE.md`

## Quick Rule

- If you want the benchmark standard, start with the STFB track.
- If you want supporting evidence, use the supplementary protocol track.
- Do not blend the two when citing results.

## Main Evidence Snapshot

| Benchmark | Status | Focus |
| --- | --- | --- |
| LongMemEval | closed | long-context memory evaluation with dual evaluation surfaces |
| MMLU | closed | general knowledge reasoning |
| ARC | closed | science reasoning |
| HumanEval | closed | code-generation execution under sandbox isolation |

- main evidence count: `4`
- release evidence remains benchmark-by-benchmark, not blended into one score

## Where To Look

- `paper/SRP_MANUSCRIPT_V1.md` for the manuscript
- `paper/docs/release/EVIDENCE_SURFACE.md` for the consolidated evidence surface
- `paper/docs/release/README.md` for the active release summary

Use this page for a quick release scan; use the detailed reports for provenance.
