param(
    [string]$PythonExe = "D:\Program Files\IBM\SPSS\Statistics\27\Python3\python.exe",
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8787
)

$ErrorActionPreference = "Stop"

$scriptRoot = "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"

if (-not (Test-Path -LiteralPath $PythonExe)) {
    throw "Python executable not found: $PythonExe"
}

if (-not $env:DEEPSEEK_API_KEY) {
    throw "Missing DEEPSEEK_API_KEY environment variable."
}

Set-Location $scriptRoot
$env:APP_ROOT = $scriptRoot
$env:HOST = $BindHost
$env:PORT = [string]$Port

Write-Host ""
Write-Host "Starting LawBench demo server..."
Write-Host "URL: http://$BindHost`:$Port"
Write-Host ""

& $PythonExe ".\backend\server.py"
