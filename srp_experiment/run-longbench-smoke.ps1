param(
    [string]$Config = "srp_experiment/configs/longbench_v2_multimodel_100_1000_smoke.json",
    [string]$TaskId = "",
    [switch]$SkipEnvCheck
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

function Invoke-Step {
    param(
        [string]$Label,
        [string[]]$Command
    )
    Write-Host "[Run] $Label"
    & $Command[0] $Command[1..($Command.Length - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Label"
    }
}

if (-not $SkipEnvCheck) {
    Invoke-Step -Label ".env alignment check" -Command @(
        "python",
        "srp_experiment/check_env_alignment.py"
    )
}

$configJson = Get-Content $Config -Raw | ConvertFrom-Json
$runsDir = $configJson.shared.output_root
$reportOutputDir = Join-Path $runsDir "long_horizon_report"

Invoke-Step -Label "LongBench smoke batch run" -Command @(
    "python",
    "srp_experiment/batch_run.py",
    "--config",
    $Config
)

Invoke-Step -Label "Collect batch summary" -Command @(
    "python",
    "srp_experiment/collect_batch_summary.py",
    "--runs-dir",
    $runsDir
)

$reportCommand = @(
    "python",
    "srp_experiment/long_horizon_report.py",
    "--input-dir",
    $runsDir,
    "--output-dir",
    $reportOutputDir
)

if ($TaskId) {
    $reportCommand += @("--task-id", $TaskId)
}

Invoke-Step -Label "Build long-horizon report" -Command $reportCommand

Write-Host ""
Write-Host "[Done] Smoke pipeline completed."
Write-Host "  Runs dir: $runsDir"
Write-Host "  Long-horizon report: $reportOutputDir"
