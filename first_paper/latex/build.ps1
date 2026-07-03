<# 
Build workflow:
- The default target is `main` when you do not pass `-Target`.
- `main` uses `latexmk` for full builds when available.
- `acl`, `neurips`, and `submission` use the stable manual chain: pdflatex -> bibtex -> pdflatex -> pdflatex.
- `-Preview` always runs a single pdflatex pass and skips BibTeX.
- `-Clean` removes auxiliary files for the selected target before compiling.
#>

param(
    [ValidateSet("main", "acl", "neurips", "submission")]
    [string]$Target = "main",
    [switch]$Clean,
    [switch]$Preview
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$config = switch ($Target) {
    "main" {
        @{ Tex = "main.tex"; Job = "main" }
    }
    "acl" {
        @{ Tex = "main_acl.tex"; Job = "main_acl" }
    }
    "neurips" {
        @{ Tex = "main_neurips.tex"; Job = "main_neurips" }
    }
    "submission" {
        @{ Tex = "main_submission.tex"; Job = "main_submission" }
    }
}

if (-not (Test-Path "references.bib")) {
    throw "Missing references.bib in $scriptDir"
}

$texFile = $config.Tex
$jobName = $config.Job

if (-not (Test-Path $texFile)) {
    throw "Missing $texFile in $scriptDir"
}

Write-Host "[Target] $Target -> $texFile"

function Invoke-PdfLaTeX {
    param(
        [string]$File
    )
    pdflatex -interaction=nonstopmode -halt-on-error $File
    if ($LASTEXITCODE -ne 0) { throw "pdflatex failed for $File" }
}

function Invoke-LatexMk {
    param(
        [string]$File,
        [string]$JobName
    )
    & latexmk @(
        "-pdf",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-jobname=$JobName",
        $File
    )
    if ($LASTEXITCODE -ne 0) { throw "latexmk failed for $File" }
}

if ($Clean) {
    Write-Host "[Clean] Removing auxiliary files for $jobName..."
    $patterns = @(
        "$jobName.aux",
        "$jobName.bbl",
        "$jobName.blg",
        "$jobName.log",
        "$jobName.out",
        "$jobName.toc",
        "$jobName.bcf",
        "$jobName.run.xml"
    )
    foreach ($pattern in $patterns) {
        if (Test-Path $pattern) {
            Remove-Item -Force $pattern
        }
    }
}

Write-Host "[Build] Starting $texFile"

if ($Preview) {
    Invoke-PdfLaTeX -File $texFile
    Write-Host "[Preview] BibTeX skipped by request."
    Write-Host "[Preview] Extra pdflatex passes skipped."
    Write-Host "[Done] Preview build completed. PDF should be in $scriptDir"
    exit 0
}

if ($Target -eq "main" -and (Get-Command latexmk -ErrorAction SilentlyContinue)) {
    Write-Host "[Build] Using latexmk for full build."
    Invoke-LatexMk -File $texFile -JobName $jobName
}
else {
    if ($Target -eq "main") {
        Write-Host "[Build] latexmk not found; falling back to manual pdflatex + bibtex."
    }
    else {
        Write-Host "[Build] Using manual pdflatex + bibtex for $Target."
    }
    Invoke-PdfLaTeX -File $texFile
    bibtex $jobName
    if ($LASTEXITCODE -ne 0) { throw "bibtex failed for $jobName" }
    Invoke-PdfLaTeX -File $texFile
    Invoke-PdfLaTeX -File $texFile
}

Write-Host "[Done] Full build completed. PDF should be in $scriptDir"
