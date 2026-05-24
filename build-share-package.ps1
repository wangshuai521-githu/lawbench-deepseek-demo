param(
    [string]$SourceRoot = "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench",
    [string]$OutputRoot = "C:\Users\wang'shuai\Documents\Codex\share-package\lawbench-deepseek-demo"
)

$ErrorActionPreference = "Stop"

if (Test-Path -LiteralPath $OutputRoot) {
    Remove-Item -LiteralPath $OutputRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $OutputRoot | Out-Null

$includePaths = @(
    "backend",
    "docs",
    "lawbench-opencompass",
    "webapp",
    ".gitignore",
    "README.md",
    "render.yaml",
    "requirements.txt",
    "run-lawbench-deepseek.ps1"
)

foreach ($item in $includePaths) {
    $src = Join-Path $SourceRoot $item
    $dst = Join-Path $OutputRoot $item
    if (Test-Path -LiteralPath $src) {
        if ((Get-Item -LiteralPath $src).PSIsContainer) {
            Copy-Item -LiteralPath $src -Destination $dst -Recurse -Force
        } else {
            $parent = Split-Path -Parent $dst
            if (-not (Test-Path -LiteralPath $parent)) {
                New-Item -ItemType Directory -Path $parent | Out-Null
            }
            Copy-Item -LiteralPath $src -Destination $dst -Force
        }
    }
}

$outputsSrc = Join-Path $SourceRoot "outputs"
$outputsDst = Join-Path $OutputRoot "outputs"
if (Test-Path -LiteralPath $outputsSrc) {
    Copy-Item -LiteralPath $outputsSrc -Destination $outputsDst -Recurse -Force
}

Write-Host "Share package created at: $OutputRoot"
