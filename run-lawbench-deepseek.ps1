param(
    [string]$PythonExe = "D:\Program Files\IBM\SPSS\Statistics\27\Python3\python.exe",
    [string]$TaskId = "1-2",
    [ValidateSet("zero_shot", "one_shot")]
    [string]$Shot = "zero_shot",
    [string]$Model = "deepseek-v4-flash",
    [int]$MaxSamples = 20,
    [int]$TimeoutSec = 120
)

$ErrorActionPreference = "Stop"

$scriptRoot = "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
$runner = Join-Path $scriptRoot "lawbench-opencompass\run_deepseek_lawbench.py"

if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

if (-not (Test-Path -LiteralPath $runner)) {
    throw "Runner not found: $runner"
}

if (-not $env:DEEPSEEK_API_KEY) {
    throw "Missing DEEPSEEK_API_KEY environment variable."
}

& $PythonExe $runner `
    --task $TaskId `
    --shot $Shot `
    --model $Model `
    --max-samples $MaxSamples `
    --timeout $TimeoutSec
