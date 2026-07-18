# SRP Release Snapshot

Date: 2026-07-18

Commit: `39053895ef73b6adc5b87a7970c2849636de4eab`

This snapshot records the frozen release-candidate state for the SRP repository.

It is a release record, not a new policy document.

## Canonical Source

- `fixed.md`

## Manuscript Mirror

- `paper/SRP_ARXIV_DRAFT_V1.md`

## Submission Snapshot

- `paper/SRP_PAPER_FINAL_V1.md`

## Packaging Layer

- `arxiv_package/`

## Verification

- `python scripts/verify_release.py`: PASS
- `latexmk -pdf -shell-escape -g -interaction=nonstopmode -halt-on-error main.tex` in `arxiv_package/`: PASS

## PDF Artifact

- File: `arxiv_package/main.pdf`
- Size: `376092` bytes
- Pages: `16`
- SHA256: `9805787D27BF3379B091E862B37BE1B68DD14A0A5AD4E234FDA66B68648416DD`

## Render Status

The current PDF is a full manuscript render driven by the publication build layer.

The package now closes the manuscript-to-PDF chain through `paper/latex/body.tex` and `arxiv_package/body.tex`.

## Terminology Contract

- [TERMINOLOGY_CONTRACT.md](TERMINOLOGY_CONTRACT.md)

## Migration Status

- [PHASE_TERMINOLOGY_MIGRATION_STATUS.md](PHASE_TERMINOLOGY_MIGRATION_STATUS.md)

## Evidence Boundary

- [CLAIM_EVIDENCE_MAP.md](CLAIM_EVIDENCE_MAP.md)

## Compatibility

Legacy aliases remain preserved for frozen historical reproducibility.

The active release vocabulary is governed by the terminology contract, while legacy names remain only as compatibility or provenance markers.

## Notes

- The release candidate is now in stabilization mode.
- The full manuscript-body injection into the arXiv package is now present.
- No release-facing evidence IDs or claim IDs were changed during this snapshot pass.
