param(
    [string]$SourceRoot = "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench",
    [string]$OutputRoot = "C:\Users\wang'shuai\Documents\Codex\share-package\legalbench-deepseek-demo"
)

$ErrorActionPreference = "Stop"

if (Test-Path -LiteralPath $OutputRoot) {
    Remove-Item -LiteralPath $OutputRoot -Recurse -Force
}

New-Item -ItemType Directory -Path $OutputRoot | Out-Null

$includePaths = @(
    "backend",
    "dashboard",
    "docs",
    "legalbench-main",
    "webapp",
    ".gitignore",
    "README.md",
    "README-APP.md",
    "README-PROJECT.md",
    "DEPLOY-RENDER.md",
    "GIT-HOSTING.md",
    "HOWTO-DEEPSEEK-LAWBENCH.md",
    "render.yaml",
    "requirements.txt",
    "run-demo-benchmark.ps1",
    "run-legalbench-deepseek.ps1",
    "build-dashboard.ps1",
    "HR-OVERVIEW.md",
    "LOCAL-DEMO-STEPS.md"
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

$outputsSrc = Join-Path $SourceRoot "legalbench-main\outputs"
$outputsDst = Join-Path $OutputRoot "legalbench-main\outputs"
if (Test-Path -LiteralPath $outputsSrc) {
    Copy-Item -LiteralPath $outputsSrc -Destination $outputsDst -Recurse -Force
}

Write-Host "Share package created at: $OutputRoot"
