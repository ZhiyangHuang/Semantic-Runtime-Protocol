<#
One-command comparison workflow for multi-method comparison tables.

Default flow:
1. optional local backend health check
2. generate a comparison config from mode + cycles
3. run the batch
4. collect summaries into a dedicated comparison output folder
5. format dedicated comparison tables

Examples:
  powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1
  powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1 -Mode core_four -Cycles 5 7
  powershell -ExecutionPolicy Bypass -File srp_experiment/comparison-run.ps1 -Mode hybrid_family -SkipHealthCheck
#>

param(
    [ValidateSet("all_modes", "core_four", "hybrid_family", "hybrid_lineage", "srp_vs_hybrids")]
    [string]$Mode = "all_modes",
    [int[]]$Cycles = @(3, 5, 7),
    [string]$Model = "Qwen/Qwen3-4B-AWQ",
    [switch]$SkipHealthCheck,
    [switch]$FailFast
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
Set-Location $repoRoot

function Invoke-Step {
    param(
        [string]$Label,
        [string[]]$Command
    )

    Write-Host ""
    Write-Host "[Step] $Label"
    Write-Host "[Cmd ] $($Command -join ' ')"
    & $Command[0] $Command[1..($Command.Length - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

function Get-MethodSets {
    param(
        [string]$SelectedMode
    )

    switch ($SelectedMode) {
        "all_modes" {
            return @(@("raw_prompt", "summarization", "rag", "srp", "rag_srp", "rag_srp_anchor", "rag_srp_v2"))
        }
        "core_four" {
            return @(@("raw_prompt", "summarization", "rag", "srp"))
        }
        "hybrid_family" {
            return @(@("rag", "rag_srp", "rag_srp_anchor", "rag_srp_v2"))
        }
        "hybrid_lineage" {
            return @(@("rag_srp", "rag_srp_anchor", "rag_srp_v2"))
        }
        "srp_vs_hybrids" {
            return @(@("rag", "srp", "rag_srp_anchor", "rag_srp_v2"))
        }
        default {
            throw "Unsupported mode: $SelectedMode"
        }
    }
}

if (-not $SkipHealthCheck) {
    Invoke-Step -Label "Local backend health check" -Command @(
        "python",
        "srp_experiment/check_local_backend.py"
    )
}
else {
    Write-Host "[Skip] Local backend health check"
}

$cycleSlug = ($Cycles | ForEach-Object { "c$_" }) -join "-"
$runSlug = "comparison_{0}__{1}__{2}" -f $Mode, ($Model -replace "[^A-Za-z0-9]+", "_").ToLower(), $cycleSlug
$runsRoot = Join-Path $repoRoot ("srp_experiment/results/batch_runs/{0}" -f $runSlug)
$tablesRoot = Join-Path $repoRoot ("srp_experiment/results/comparison_tables/{0}" -f $runSlug)
$generatedConfigDir = Join-Path $repoRoot "srp_experiment/results/generated_configs"
$null = New-Item -ItemType Directory -Force -Path $generatedConfigDir, $runsRoot, $tablesRoot
$generatedConfigPath = Join-Path $generatedConfigDir ("{0}.json" -f $runSlug)
$manifestPath = Join-Path $tablesRoot "batch_manifest.json"
$summaryJsonPath = Join-Path $tablesRoot "batch_summary_table.json"
$summaryCsvPath = Join-Path $tablesRoot "batch_summary_table.csv"
$summaryMdPath = Join-Path $tablesRoot "batch_summary_table.md"
$paperMdPath = Join-Path $tablesRoot "paper_table.md"
$paperTexPath = Join-Path $tablesRoot "paper_table.tex"
$qualityMdPath = Join-Path $tablesRoot "quality_table.md"
$qualityTexPath = Join-Path $tablesRoot "quality_table.tex"
$efficiencyMdPath = Join-Path $tablesRoot "efficiency_table.md"
$efficiencyTexPath = Join-Path $tablesRoot "efficiency_table.tex"
$cameraMdPath = Join-Path $tablesRoot "camera_ready_table.md"
$cameraTexPath = Join-Path $tablesRoot "camera_ready_table.tex"

$configObject = [ordered]@{
    description = "Generated comparison pack run"
    shared = [ordered]@{
        backend = "local"
        output_root = ("srp_experiment/results/batch_runs/{0}" -f $runSlug)
    }
    runs = @(
        [ordered]@{
            name = ("comparison_{0}" -f $Mode)
            cycles = $Cycles
            models = @($Model)
            methods = (Get-MethodSets -SelectedMode $Mode)
        }
    )
}

$configJson = $configObject | ConvertTo-Json -Depth 10
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText($generatedConfigPath, $configJson, $utf8NoBom)

Invoke-Step -Label "Batch run" -Command @(
    "python",
    "srp_experiment/batch_run.py",
    "--config",
    $generatedConfigPath,
    "--manifest-path",
    $manifestPath
)

if ($FailFast) {
    # placeholder to preserve interface symmetry; batch_run already exits on failure
}

Invoke-Step -Label "Collect comparison summary" -Command @(
    "python",
    "srp_experiment/collect_batch_summary.py",
    "--runs-dir",
    $runsRoot,
    "--output-json",
    $summaryJsonPath,
    "--output-csv",
    $summaryCsvPath,
    "--output-md",
    $summaryMdPath
)

Invoke-Step -Label "Format comparison tables" -Command @(
    "python",
    "srp_experiment/paper_table_formatter.py",
    "--input-json",
    $summaryJsonPath,
    "--output-md",
    $paperMdPath,
    "--output-tex",
    $paperTexPath,
    "--quality-md",
    $qualityMdPath,
    "--quality-tex",
    $qualityTexPath,
    "--efficiency-md",
    $efficiencyMdPath,
    "--efficiency-tex",
    $efficiencyTexPath,
    "--camera-ready-md",
    $cameraMdPath,
    "--camera-ready-tex",
    $cameraTexPath
)

Write-Host ""
Write-Host "[Done] Comparison workflow completed."
Write-Host "[Info] Mode: $Mode"
Write-Host "[Info] Cycles: $($Cycles -join ', ')"
Write-Host "[Info] Generated config: $generatedConfigPath"
Write-Host "[Info] Batch runs dir: $runsRoot"
Write-Host "[Info] Tables dir: $tablesRoot"
Write-Host ""
Write-Host "[Preview] paper_table.md"
Get-Content $paperMdPath | Select-Object -First 8 | ForEach-Object { Write-Host $_ }
