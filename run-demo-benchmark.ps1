param(
    [string]$Model = "deepseek-v4-flash",
    [int]$MaxSamples = 20
)

$ErrorActionPreference = "Stop"

$scriptRoot = "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
$runner = Join-Path $scriptRoot "run-legalbench-deepseek.ps1"

$jobs = @(
    @{ TaskName = "hearsay"; Split = "train"; MaxSamples = 5 },
    @{ TaskName = "opp115_data_security"; Split = "test"; MaxSamples = $MaxSamples },
    @{ TaskName = "opp115_policy_change"; Split = "test"; MaxSamples = $MaxSamples },
    @{ TaskName = "maud_definition_includes_asset_deals"; Split = "test"; MaxSamples = $MaxSamples }
)

foreach ($job in $jobs) {
    & $runner `
        -TaskName $job.TaskName `
        -Split $job.Split `
        -Model $Model `
        -MaxSamples $job.MaxSamples `
        -SavePredictions
}

& (Join-Path $scriptRoot "build-dashboard.ps1")
