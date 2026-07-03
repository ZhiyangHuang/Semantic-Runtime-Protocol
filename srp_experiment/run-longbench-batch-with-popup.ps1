param(
    [string]$Config = "srp_experiment/configs/longbench_v2_multimodel_100_1000_smoke.json",
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
$progressFile = Join-Path $runsDir "batch_manifest_progress.json"
$manifestPath = Join-Path $runsDir "batch_manifest.json"

$null = New-Item -ItemType Directory -Force -Path $runsDir

Start-Process -FilePath "python" -ArgumentList @(
    "srp_experiment/progress_popup.py",
    "--progress-file",
    $progressFile,
    "--title",
    "SRP LongBench Progress"
) -WindowStyle Hidden

Invoke-Step -Label "LongBench batch run with popup" -Command @(
    "python",
    "srp_experiment/batch_run.py",
    "--config",
    $Config,
    "--manifest-path",
    $manifestPath
)

Write-Host ""
Write-Host "[Done] Batch run finished."
Write-Host "  Runs dir: $runsDir"
Write-Host "  Progress file: $progressFile"
