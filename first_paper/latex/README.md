# First Paper LaTeX

This folder holds the LaTeX entry points for the first paper draft.

## Start Here

- `.\build.ps1` - build `main.tex`
- `.\build.ps1 -Target acl` - build `main_acl.tex`
- `.\build.ps1 -Target neurips` - build `main_neurips.tex`
- `.\build.ps1 -Target submission` - build `main_submission.tex`

The default target is `main` when you do not pass `-Target`.
`main` prefers `latexmk`; `acl`, `neurips`, and `submission` use the stable manual chain in `build.ps1`.

## Files

- `main.tex` - current first-paper main draft
- `main_acl.tex` - ACL-style draft
- `main_neurips.tex` - NeurIPS-style draft
- `main_submission.tex` - compressed submission-version draft
- `references.bib` - shared bibliography source
- `compile.md` - build and switching guide
- `build.ps1` - PowerShell build script
