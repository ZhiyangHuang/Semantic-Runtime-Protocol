<#
One-command first-paper experiment workflow.

Default flow:
1. health check local backend
2. run batch experiments from the first-paper priority config
3. collect batch summaries
4. format paper-ready tables

Examples:
  powershell -ExecutionPolicy Bypass -File srp_experiment/first-paper-run.ps1
  powershell -ExecutionPolicy Bypass -File srp_experiment/first-paper-run.ps1 -SkipHealthCheck
  powershell -ExecutionPolicy Bypass -File srp_experiment/first-paper-run.ps1 -Config srp_experiment/configs/local_batch.json
#>

param(
    [string]$Config = "srp_experiment/configs/first_paper_priority_local.json",
    [switch]$SkipHealthCheck,
    [switch]$FailFast
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
Set-Location $repoRoot

$configPath = if ([System.IO.Path]::IsPathRooted($Config)) {
    $Config
} else {
    Join-Path $repoRoot $Config
}

if (-not (Test-Path $configPath)) {
    throw "Config file not found: $configPath"
}

$configJson = Get-Content $configPath -Raw | ConvertFrom-Json
$outputRoot = $configJson.shared.output_root
if (-not $outputRoot) {
    throw "Missing shared.output_root in config: $configPath"
}

$env:SRP_BATCH_RUNS_DIR = $outputRoot
$resultsRoot = Join-Path $repoRoot "srp_experiment\results"
$keyOutputs = @(
    (Join-Path $resultsRoot "batch_summary_table.json"),
    (Join-Path $resultsRoot "batch_summary_table.csv"),
    (Join-Path $resultsRoot "batch_summary_table.md"),
    (Join-Path $resultsRoot "paper_table.md"),
    (Join-Path $resultsRoot "paper_table.tex"),
    (Join-Path $resultsRoot "quality_table.md"),
    (Join-Path $resultsRoot "quality_table.tex"),
    (Join-Path $resultsRoot "efficiency_table.md"),
    (Join-Path $resultsRoot "efficiency_table.tex"),
    (Join-Path $resultsRoot "camera_ready_table.md"),
    (Join-Path $resultsRoot "camera_ready_table.tex")
)
$previewFiles = @(
    (Join-Path $resultsRoot "paper_table.md"),
    (Join-Path $resultsRoot "camera_ready_table.md")
)
$batchSummaryJson = Join-Path $resultsRoot "batch_summary_table.json"
$cameraReadyTable = Join-Path $resultsRoot "camera_ready_table.md"
$batchManifestJson = Join-Path $resultsRoot "batch_manifest.json"

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

function Get-ExpectedMethods {
    param(
        $ConfigObject
    )

    $methods = New-Object System.Collections.Generic.List[string]
    foreach ($run in $ConfigObject.runs) {
        foreach ($bundle in $run.methods) {
            foreach ($method in $bundle) {
                if ($method -and -not $methods.Contains($method)) {
                    $methods.Add($method)
                }
            }
        }
    }
    return $methods
}

function Get-DataMarkdownRowCount {
    param(
        [string]$Path
    )

    if (-not (Test-Path $Path)) {
        return 0
    }

    $pipeLines = Get-Content $Path | Where-Object { $_.Trim().StartsWith("|") }
    if ($pipeLines.Count -le 2) {
        return 0
    }

    return $pipeLines.Count - 2
}

function Get-RunDirectorySuggestions {
    param(
        [string[]]$Methods,
        [string]$RunsRoot,
        [int]$MaxSuggestions = 3
    )

    if (-not (Test-Path $RunsRoot)) {
        return @()
    }

    $matches = New-Object System.Collections.Generic.List[string]
    $runDirs = Get-ChildItem -Path $RunsRoot -Directory -ErrorAction SilentlyContinue
    foreach ($dir in $runDirs) {
        foreach ($method in $Methods) {
            if ($dir.Name -like "*$method*") {
                if (-not $matches.Contains($dir.FullName)) {
                    $matches.Add($dir.FullName)
                }
                break
            }
        }
        if ($matches.Count -ge $MaxSuggestions) {
            break
        }
    }

    return $matches
}

function Get-IncompleteFormatterGroups {
    param(
        [object[]]$Rows,
        [string[]]$ExpectedMethods
    )

    if (-not $Rows -or $Rows.Count -eq 0) {
        return @()
    }

    $grouped = $Rows | Group-Object backend, model, cycles
    $incomplete = New-Object System.Collections.Generic.List[object]

    foreach ($group in $grouped) {
        $groupRows = @($group.Group)
        $groupMethods = @($groupRows | ForEach-Object { $_.method } | Where-Object { $_ } | Sort-Object -Unique)
        $missing = @($ExpectedMethods | Where-Object { $_ -notin $groupMethods })
        if ($missing.Count -gt 0) {
            $first = $groupRows[0]
            $incomplete.Add([PSCustomObject]@{
                backend = $first.backend
                model = $first.model
                cycles = $first.cycles
                present_methods = ($groupMethods -join ", ")
                missing_methods = ($missing -join ", ")
                run_dir = $first.run_dir
                method_bundle = $first.method_bundle
            })
        }
    }

    return $incomplete
}

function Get-RunMethodDiagnostics {
    param(
        [string]$RunDir,
        [string[]]$ExpectedMethods,
        [string[]]$BundleMethods
    )

    $summaryPath = Join-Path $RunDir "summary.json"
    $resultsPath = Join-Path $RunDir "results.json"
    $summaryMethods = @()
    $resultMethods = @()

    if (Test-Path $summaryPath) {
        $summaryJson = Get-Content $summaryPath -Raw | ConvertFrom-Json
        if ($summaryJson) {
            $summaryMethods = @($summaryJson.PSObject.Properties.Name | Sort-Object -Unique)
        }
    }

    if (Test-Path $resultsPath) {
        $resultsJson = Get-Content $resultsPath -Raw | ConvertFrom-Json
        if ($resultsJson) {
            if ($resultsJson.PSObject.Properties.Name -contains "methods") {
                $resultMethods = @($resultsJson.methods.PSObject.Properties.Name | Sort-Object -Unique)
            } elseif ($resultsJson -is [System.Array]) {
                $resultMethods = @($resultsJson | ForEach-Object { $_.method } | Where-Object { $_ } | Sort-Object -Unique)
            } else {
                $candidateMethods = @($resultsJson.PSObject.Properties.Name | Where-Object { $_ -in $ExpectedMethods } | Sort-Object -Unique)
                if ($candidateMethods.Count -gt 0) {
                    $resultMethods = $candidateMethods
                }
            }
        }
    }

    $missingFromSummary = @($ExpectedMethods | Where-Object { $_ -notin $summaryMethods })
    $missingFromResults = @($ExpectedMethods | Where-Object { $_ -notin $resultMethods })
    $missingFromBundleSummary = @($BundleMethods | Where-Object { $_ -notin $summaryMethods })
    $missingFromBundleResults = @($BundleMethods | Where-Object { $_ -notin $resultMethods })

    return [PSCustomObject]@{
        summary_path = $summaryPath
        results_path = $resultsPath
        summary_exists = (Test-Path $summaryPath)
        results_exists = (Test-Path $resultsPath)
        summary_methods = $summaryMethods
        result_methods = $resultMethods
        missing_from_summary = $missingFromSummary
        missing_from_results = $missingFromResults
        missing_from_bundle_summary = $missingFromBundleSummary
        missing_from_bundle_results = $missingFromBundleResults
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

$batchCommand = @(
    "python",
    "srp_experiment/batch_run.py",
    "--config",
    $Config
)

if ($FailFast) {
    $batchCommand += "--fail-fast"
}

Invoke-Step -Label "Batch run" -Command $batchCommand

Invoke-Step -Label "Collect batch summary" -Command @(
    "python",
    "srp_experiment/collect_batch_summary.py"
)

Invoke-Step -Label "Format paper tables" -Command @(
    "python",
    "srp_experiment/paper_table_formatter.py"
)

Write-Host ""
Write-Host "[Done] First-paper experiment workflow completed."
Write-Host "[Info] Main config: $Config"
Write-Host "[Info] Batch runs dir: $env:SRP_BATCH_RUNS_DIR"
Write-Host "[Info] Results root: srp_experiment/results"
Write-Host "[Info] Key outputs:"
foreach ($path in $keyOutputs) {
    $label = Split-Path $path -Leaf
    if (Test-Path $path) {
        Write-Host "  - $label -> $path"
    } else {
        Write-Host "  - $label -> missing"
    }
}

foreach ($path in $previewFiles) {
    $label = Split-Path $path -Leaf
    Write-Host ""
    Write-Host "[Preview] $label"
    if (Test-Path $path) {
        Get-Content $path | Select-Object -First 8 | ForEach-Object { Write-Host $_ }
    } else {
        Write-Host "missing"
    }
}

Write-Host ""
Write-Host "[Sanity]"

$expectedMethods = @(Get-ExpectedMethods -ConfigObject $configJson)
$summaryRows = @()
if (Test-Path $batchSummaryJson) {
    $summaryData = Get-Content $batchSummaryJson -Raw | ConvertFrom-Json
    if ($null -ne $summaryData) {
        $summaryRows = @($summaryData)
    }
}

$rowCount = $summaryRows.Count
if ($rowCount -eq 0) {
    Write-Host "  - Warning: batch_summary_table.json has 0 rows."
    Write-Host "    Action: check $batchManifestJson first, then inspect run outputs under $env:SRP_BATCH_RUNS_DIR."
    Write-Host "    Action: if manifest exists but summary is empty, open $batchSummaryJson and rerun collect_batch_summary.py."
} else {
    Write-Host "  - OK: batch_summary_table.json rows = $rowCount."
}

$presentMethods = @()
if ($rowCount -gt 0) {
    $presentMethods = @($summaryRows | ForEach-Object { $_.method } | Where-Object { $_ } | Sort-Object -Unique)
}

if ($presentMethods.Count -gt 0) {
    Write-Host "  - Methods present: $($presentMethods -join ', ')"
} else {
    Write-Host "  - Warning: no methods detected in batch_summary_table.json."
    Write-Host "    Action: inspect $batchSummaryJson to confirm collected rows have a 'method' field."
}

$missingMethods = @($expectedMethods | Where-Object { $_ -notin $presentMethods })
if ($missingMethods.Count -gt 0) {
    Write-Host "  - Warning: missing expected methods: $($missingMethods -join ', ')"
    Write-Host "    Action: compare $batchManifestJson against $batchSummaryJson to see which runs were planned but not collected."
    $suggestedRuns = @(Get-RunDirectorySuggestions -Methods $missingMethods -RunsRoot (Join-Path $repoRoot $env:SRP_BATCH_RUNS_DIR))
    if ($suggestedRuns.Count -gt 0) {
        Write-Host "    Action: inspect candidate run dirs:"
        foreach ($runPath in $suggestedRuns) {
            Write-Host "      * $runPath"
        }
    } else {
        Write-Host "    Action: inspect run directories under $env:SRP_BATCH_RUNS_DIR for missing summaries."
    }
} else {
    Write-Host "  - OK: all expected methods are present."
}

$srpRowCount = @($summaryRows | Where-Object { $_.method -eq "srp" }).Count
if ($srpRowCount -eq 0) {
    Write-Host "  - Warning: no SRP rows found in batch_summary_table.json."
    Write-Host "    Action: inspect SRP run directories under $env:SRP_BATCH_RUNS_DIR and check each summary.json / results.json."
    Write-Host "    Action: if SRP runs completed, open $batchSummaryJson to verify collect did not drop 'srp' rows."
} else {
    Write-Host "  - OK: SRP rows in batch summary = $srpRowCount."
}

$cameraReadyRowCount = Get-DataMarkdownRowCount -Path $cameraReadyTable
if ($cameraReadyRowCount -eq 0) {
    Write-Host "  - Warning: camera_ready_table.md has 0 data rows."
    Write-Host "    Action: inspect $cameraReadyTable and $batchSummaryJson to confirm formatter received grouped rows."
    Write-Host "    Action: if batch summary looks healthy, rerun paper_table_formatter.py and inspect paper_table.md too."
} else {
    Write-Host "  - OK: camera_ready_table.md data rows = $cameraReadyRowCount."
}

$incompleteGroups = @(Get-IncompleteFormatterGroups -Rows $summaryRows -ExpectedMethods $expectedMethods)
if ($incompleteGroups.Count -gt 0) {
    $hardWarningCount = 0
    $bundleCompletePartialCount = 0
    foreach ($group in $incompleteGroups) {
        $bundleMethods = @()
        if ($group.method_bundle) {
            $bundleMethods = @($group.method_bundle -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
        }
        if ($group.run_dir) {
            $diagnostics = Get-RunMethodDiagnostics -RunDir $group.run_dir -ExpectedMethods $expectedMethods -BundleMethods $bundleMethods
            $bundleComplete = (
                $bundleMethods.Count -gt 0 -and
                $diagnostics.missing_from_bundle_summary.Count -eq 0 -and
                $diagnostics.missing_from_bundle_results.Count -eq 0
            )
            if ($bundleComplete) {
                $bundleCompletePartialCount += 1
            } else {
                $hardWarningCount += 1
            }
        } else {
            $hardWarningCount += 1
        }
    }

    if ($hardWarningCount -gt 0) {
        Write-Host "  - Warning: formatter input includes groups with real bundle-level incompleteness."
    } else {
        Write-Host "  - Note: formatter input includes partial global comparisons, but each run appears complete for its own bundle."
    }

    foreach ($group in $incompleteGroups) {
        Write-Host "      * backend=$($group.backend) | model=$($group.model) | cycles=$($group.cycles) | missing=[$($group.missing_methods)] | present=[$($group.present_methods)]"
        if ($group.run_dir) {
            $bundleMethods = @()
            if ($group.method_bundle) {
                $bundleMethods = @($group.method_bundle -split "," | ForEach-Object { $_.Trim() } | Where-Object { $_ })
            }
            Write-Host "        run_dir: $($group.run_dir)"
            if ($bundleMethods.Count -gt 0) {
                Write-Host "        run bundle methods: [$($bundleMethods -join ', ')]"
            }
            $diagnostics = Get-RunMethodDiagnostics -RunDir $group.run_dir -ExpectedMethods $expectedMethods -BundleMethods $bundleMethods
            if ($diagnostics.summary_exists) {
                $summaryMethodsText = if ($diagnostics.summary_methods.Count -gt 0) { $diagnostics.summary_methods -join ", " } else { "none" }
                Write-Host "        summary.json methods: [$summaryMethodsText]"
            }
            if ($diagnostics.results_exists -and $diagnostics.result_methods.Count -gt 0) {
                Write-Host "        results.json methods: [$($diagnostics.result_methods -join ', ')]"
            }

            if ($bundleMethods.Count -gt 0 -and $diagnostics.missing_from_bundle_summary.Count -eq 0 -and $diagnostics.missing_from_bundle_results.Count -eq 0) {
                Write-Host "        Verdict: this run directory is internally complete for its own method bundle."
                Write-Host "        Action: this group is only incomplete relative to the global formatter method set; compare the bundle in $batchSummaryJson before treating it as a failed run."
            } elseif ($diagnostics.summary_exists -and $diagnostics.missing_from_summary.Count -gt 0) {
                Write-Host "        Verdict: summary.json really is missing expected methods [$($diagnostics.missing_from_summary -join ', ')]."
                Write-Host "        Action: open $($diagnostics.summary_path) first, then compare with $batchManifestJson."
            } elseif (-not $diagnostics.summary_exists -and $diagnostics.results_exists) {
                Write-Host "        Verdict: summary.json is missing, but results.json exists."
                Write-Host "        Action: open $($diagnostics.results_path) first to confirm the run produced raw method outputs."
            } elseif ($diagnostics.results_exists -and $diagnostics.missing_from_results.Count -gt 0) {
                Write-Host "        Verdict: results.json also lacks expected methods [$($diagnostics.missing_from_results -join ', ')]."
                Write-Host "        Action: inspect $($diagnostics.results_path) and rerun this batch entry if those methods should exist."
            } else {
                Write-Host "        Verdict: both summary.json and results.json look structurally complete for this run."
                Write-Host "        Action: this is likely an intentionally partial method bundle; compare with the config before treating it as an error."
            }
        }
    }
    if ($hardWarningCount -gt 0) {
        Write-Host "    Action: inspect batch_summary_table.json for the groups above, then compare with batch_manifest.json and the matching run directories."
    } else {
        Write-Host "    Action: treat these as coverage notes for the global formatter view unless you expected full four-method coverage at every cycle."
    }
    Write-Host "    Summary: bundle-complete partial groups: $bundleCompletePartialCount | real incomplete groups: $hardWarningCount"
} else {
    Write-Host "  - OK: all backend/model/cycle groups have the full expected method set."
}
