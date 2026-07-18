# Paper Build Pipeline

This document records the build chain that produces the release-facing SRP manuscript PDF.

It separates canonical source, publication representation, and submission execution.

## Build Chain

```text
fixed.md
  -> paper/SRP_ARXIV_DRAFT_V1.md
  -> paper/latex/body.tex
  -> arxiv_package/body.tex
  -> arxiv_package/main.tex
  -> arxiv_package/main.pdf
```

## Layer Responsibilities

| Layer | Path | Responsibility |
| --- | --- | --- |
| Canonical source | `fixed.md` | Primary editable manuscript source of truth |
| Synchronized mirror | `paper/SRP_ARXIV_DRAFT_V1.md` | Release-synchronized manuscript mirror |
| Publication build body | `paper/latex/body.tex` | Generated manuscript body used for PDF build |
| Package wrapper | `arxiv_package/body.tex` | Thin forwarding wrapper into the publication build layer |
| Submission entrypoint | `arxiv_package/main.tex` | PDF compilation entrypoint |
| Submission output | `arxiv_package/main.pdf` | Release-facing PDF artifact |

## Constraints

- `fixed.md` remains canonical and editable.
- `paper/SRP_ARXIV_DRAFT_V1.md` remains the synchronized mirror.
- `paper/latex/body.tex` is a build artifact, not a new source of truth.
- `arxiv_package/` must not become a second manuscript source.

## Verification Notes

- The build layer exists to close the manuscript-to-PDF release chain.
- It is intended to preserve the manuscript hierarchy already frozen in the repository contract.
- The build body should be regenerated from the synchronized manuscript mirror when the manuscript changes.

