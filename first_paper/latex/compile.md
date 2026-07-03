# Compile Guide

This folder holds three interchangeable LaTeX entry points for the first paper draft.

## Files

- `main.tex` - generic submission-oriented skeleton
- `main_acl.tex` - ACL-style skeleton
- `main_neurips.tex` - NeurIPS-style skeleton
- `main_submission.tex` - compressed submission version
- `references.bib` - shared bibliography file

## Recommended Uses

- `main.tex`: use this for local drafting and venue-agnostic edits.
- `main_acl.tex`: use this when targeting ACL-style NLP submissions.
- `main_neurips.tex`: use this when targeting NeurIPS-style ML submissions.
- `main_submission.tex`: use this when targeting the compressed submission core.

## Compile Commands

Run all commands from the `first_paper/latex/` directory.

### Quick Start

```bash
# main
.\build.ps1

# acl
.\build.ps1 -Target acl

# neurips
.\build.ps1 -Target neurips

# submission
.\build.ps1 -Target submission
```

The default target is `main` when you do not pass `-Target`.
Use `-Clean` to remove auxiliary files before compiling, and `-Preview` to run only one quick `pdflatex` pass.
The script prints targets in the same form it uses internally, for example `main -> main.tex`, `acl -> main_acl.tex`, `neurips -> main_neurips.tex`, and `submission -> main_submission.tex`.

### Full Builds

```powershell
.\build.ps1 -Target main
.\build.ps1 -Target acl
.\build.ps1 -Target neurips
.\build.ps1 -Target submission
.\build.ps1 -Target acl -Clean
.\build.ps1 -Target main -Clean
.\build.ps1 -Target neurips -Preview
.\build.ps1 -Target submission -Preview
```

### Manual BibTeX Flow

```bash
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

This manual sequence is useful if you want to inspect each pass individually. `main.tex` uses `latexmk` for full builds when available, while `main_acl.tex`, `main_neurips.tex`, and `main_submission.tex` use the stable manual chain.

## Notes

- `main.tex` prefers `latexmk` for full builds; `main_acl.tex`, `main_neurips.tex`, and `main_submission.tex` use the manual chain in `build.ps1`.
- The bibliography file is shared across all templates, so keep citation keys consistent.
- The figure path in `main.tex` points to `../figures/`.

## Quick Checklist

Use this checklist before re-running a compile:

1. Make sure you are in `first_paper/latex/`.
2. Confirm the target `.tex` file matches the venue you want.
3. Confirm `references.bib` exists in the same folder.
4. Confirm all citation keys used in the paper exist in `references.bib`.
5. Confirm figure paths are valid relative to `first_paper/latex/`.
6. Run the matching compile sequence or `latexmk`.
7. Read the `.log` file if the PDF does not appear or citations are unresolved.

## Common Errors

### 1. `LaTeX Warning: Citation ... undefined`

Cause:
- citation key in the text does not exist in `references.bib`
- BibTeX was not run

How to fix:
- search the key in `references.bib`
- make sure the key spelling matches exactly
- rerun the full sequence: `pdflatex -> bibtex -> pdflatex -> pdflatex`

### 2. `LaTeX Error: File ... not found`

Cause:
- broken image path
- missing package in the TeX distribution
- wrong filename or capitalization

How to fix:
- check the exact path in the `.tex` file
- verify the file exists in the expected directory
- if needed, use the `.log` file to see the exact missing file name

### 3. `Package ... Error`

Cause:
- incompatible package version
- missing package installation
- template package not available locally

How to fix:
- check whether the error is from `acl`, `neurips_2024`, or another package
- if a venue template package is missing, install the official template or use the generic `main.tex`

### 4. Bibliography compiles, but references still show `?`

Cause:
- BibTeX did not run in the correct order
- `.aux` / `.bbl` files are stale

How to fix:
- rerun the full sequence from scratch
- if needed, delete generated auxiliary files in the LaTeX folder and compile again

### 5. Figure appears blank or stretched

Cause:
- placeholder figure is still in use
- image path is correct but asset is low-resolution or too small

How to fix:
- replace the placeholder with the final figure
- keep the source image in `first_paper/figures/`
- adjust `width=...` only after the image is in the right place

## Where to Look First

If something breaks, check in this order:

1. The `.log` file for the exact error line.
2. The citation key in `references.bib`.
3. The figure path in the `.tex` file.
4. The template package name in the preamble.
5. The compile order and whether BibTeX ran.

This order usually resolves the issue faster than guessing from the PDF output alone.

## Error-to-Command Quick Index

| Symptom | Most Likely Fix | Command to Run |
| --- | --- | --- |
| Citation shows `?` or `undefined` | BibTeX did not run or the key is missing | Rerun without `-Preview`: `.\build.ps1` |
| PDF missing after compile | LaTeX stopped on an earlier error | Open the `.log` file, fix the first error, then rerun the full compile sequence |
| Figure not found | Bad relative path or missing file | Verify the file exists, then rerun `pdflatex` |
| Template package error | Missing ACL/NeurIPS package or incompatible TeX install | Switch to `main.tex` for testing, or install the official venue template |
| References still appear as `?` after BibTeX | Stale auxiliary files | Delete generated `.aux`, `.bbl`, `.blg`, `.log` files and rerun the full sequence |
| Figure looks blank or tiny | Placeholder asset or wrong width | Replace the placeholder image and rerun `pdflatex` |

Use the command in the last column that matches your selected template file. For a quick reminder:

- `main` -> `.\build.ps1`
- `acl` -> `.\build.ps1 -Target acl`
- `neurips` -> `.\build.ps1 -Target neurips`

For example, if you are compiling `main_acl.tex`, the BibTeX command should be `bibtex main_acl`.
