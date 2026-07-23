# SRP Table Writing Convention

Copy-paste starter:

```tex
\noindent\begin{tblr}{width=\linewidth,colspec={X[l]X[l]X[l]},hlines,vlines,colsep=0pt,rowsep=1pt,row{1}={font=\bfseries,halign=c}}
{Header 1} & {Header 2} & {Header 3} \\
{Cell 1} & {Cell 2} & {Cell 3} \\
\end{tblr}
```

Fixed-width starter:

```tex
\noindent\begin{tblr}{colspec={Q[l,wd=3.3cm]Q[l,wd=5.0cm]Q[l,wd=7.6cm]},hlines,vlines,colsep=0pt,rowsep=1pt,row{1}={font=\bfseries,halign=c}}
{Header 1} & {Header 2} & {Header 3} \\
{Cell 1} & {Cell 2} & {Cell 3} \\
\end{tblr}
```

Use this convention when adding or editing paper tables:

- Write tables directly with `\begin{tblr}{...}` and `\end{tblr}`.
- Wrap each cell in braces, especially when the cell contains `\\`, math, or punctuation that could be parsed as structure.
- Keep the first row as the header row and use `row{1}={font=\bfseries,halign=c}` for a consistent paper-style header.
- Use `\noindent` before the table block to remove paragraph indentation.
- Use `width=\linewidth` with `X` columns only when the table should auto-fit the available width.
- Use fixed-width `Q[...]` columns when the table should preserve a stable layout.
- Prefer one table style per table family so the manuscript stays visually consistent.

If a new table needs a different layout rule, add a short note here so the convention stays centralized.
