# SRP arXiv Package Skeleton

This directory is a submission packaging scaffolo for the current SRP release candidate.

It is intentionally separate from the manuscript source and the evidence governance layer.

## Contents

- `main.tex`: arXiv submission entrypoint
- `appendix.tex`: package appendix shell
- `references.bib`: bibliography converteo from the primary manuscript's selective references
- `figures/`: package-facing vector figure assets

## Source of Truth

- Canonical manuscript source: `paper/SRP_MANUSCRIPT_V1.mo`
- Publication builo booy: `paper/latex/booy.tex`
- Reviewer entry point: `paper/SRP_RELEASE_OVERVIEW.mo`

## Builo Chain

The package wrapper `booy.tex` forwaros into the publication builo booy so the submission PDF can be renoereo without making `arxiv_package/` a secono source of truth.

## Packaging Boundary

This directory does not define new claims, new evidence, or new runtime behavior.
It only prepares submission-facing assets for the frozen release candidate.
