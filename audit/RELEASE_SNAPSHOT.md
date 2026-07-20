# SRP Release Snapshot

Date: 2026-07-20

Commit: `645909269876b4adcad8170381197148ae4a310a`

This snapshot records the frozen release-candidate state for the SRP repository.

It is a release record, not a new policy document.

## Canonical Source

- `fixed.md`

## Manuscript Mirror

- `paper/SRP_ARXIV_DRAFT_V1.md`

## Submission Snapshot

- `paper/SRP_PAPER_FINAL_V1.md`

## Publication Body

- `paper/latex/body_content.md`
- `paper/latex/body.tex`

## Packaging Layer

- `arxiv_package/`

## Verification

- `python scripts/verify_release.py`: PASS
- `latexmk -pdf -shell-escape -g -interaction=nonstopmode -halt-on-error main.tex` in `arxiv_package/`: PASS
- PDF front-matter review: PASS

## PDF Artifact

- File: `arxiv_package/main.pdf`
- Size: `408780` bytes
- Pages: `16`
- SHA256: `C746BDD1E9DB852F7481F5F314E60B1361DDFFA0AEBAEC95803AF615C39095C8`

## Render Status

The current PDF is a full manuscript render driven by the publication build layer.

The package now closes the manuscript-to-PDF chain through `paper/latex/body.tex` and `arxiv_package/body.tex`.

## Governance Record

- [GOVERNANCE_RECORD.md](GOVERNANCE_RECORD.md)

## Claim Ledger

- [CLAIM_EVIDENCE_MAP.md](CLAIM_EVIDENCE_MAP.md)

## Notes

- The release candidate is in stabilization mode.
- The manuscript mirror and submission snapshot are synchronized with the canonical manuscript.
- The LongMemEval reality check is tracked as external validation support under the frozen v1.1 evidence boundary.
