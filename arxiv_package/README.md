# SRP arXiv Package Skeleton

This directory is a submission packaging scaffold for the current SRP release candidate.

It is intentionally separate from the manuscript source and the evidence governance layer.

## Contents

- `main.tex`: arXiv submission entrypoint
- `appendix.tex`: package appendix shell
- `references.bib`: bibliography converted from the primary manuscript's selective references
- `figures/`: package-facing vector figure assets

## Source of Truth

- Canonical manuscript source: `fixed.md`
- Synchronized manuscript mirror: `paper/SRP_ARXIV_DRAFT_V1.md`
- Publication build body: `paper/latex/body.tex`
- Submission snapshot: `paper/SRP_PAPER_FINAL_V1.md`
- Supporting reconstruction: `paper/SRP_RELATED_WORK_V1.md`

## Build Chain

The package wrapper `body.tex` forwards into the publication build body so the submission PDF can be rendered without making `arxiv_package/` a second source of truth.

## Packaging Boundary

This directory does not define new claims, new evidence, or new runtime behavior.
It only prepares submission-facing assets for the frozen release candidate.
