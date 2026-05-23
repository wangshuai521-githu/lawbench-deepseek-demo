# LegalBench x DeepSeek Demo Project

This project turns the open-source LegalBench dataset into a small benchmark system that can be shown in interviews.

## What is implemented

- a generic DeepSeek runner for LegalBench prompt templates
- support for `train.tsv` and `test.tsv`
- saved JSON run artifacts
- a static dashboard for benchmark visualization

## Core scripts

- `run-legalbench-deepseek.ps1`
- `run-demo-benchmark.ps1`
- `build-dashboard.ps1`

## Example tasks to run

- `hearsay`
- `opp115_data_security`
- `opp115_policy_change`
- `maud_definition_includes_asset_deals`

## Run one task

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
$env:DEEPSEEK_API_KEY="your_api_key_here"
.\run-legalbench-deepseek.ps1 -TaskName hearsay -Split train -MaxSamples 5 -SavePredictions
```

## Run a task with a real test split

```powershell
.\run-legalbench-deepseek.ps1 -TaskName opp115_data_security -Split test -MaxSamples 20 -SavePredictions
```

## Build dashboard

```powershell
.\build-dashboard.ps1
```

Then open:

- `C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench\dashboard\index.html`

## Run the full demo batch

```powershell
.\run-demo-benchmark.ps1
```

This runs a small interview-friendly benchmark set and rebuilds the dashboard automatically.

## Why this is useful for job hunting

This is stronger than a one-off API demo because it shows:

- reading and adapting an open-source benchmark
- integrating a third-party model API
- building reusable evaluation tooling
- saving artifacts for reproducibility
- presenting results through a small product-style dashboard

## Interview framing

You can describe this project like this:

I adapted the open-source LegalBench benchmark into a reusable evaluation workflow for DeepSeek models. I built a generic prompt runner that loads task templates and TSV datasets, calls the DeepSeek API, normalizes predictions, stores run artifacts, and renders a local dashboard for result inspection.

The value of the project is not just API integration. It shows benchmark-oriented engineering: task abstraction, repeatable runs, error handling for messy dataset text, and a lightweight results product that makes model behavior easier to inspect.

## Current demo story

The first benchmark batch already produced:

- `hearsay` on `train`: accuracy `1.00`
- `opp115_data_security` on `test`: accuracy `0.85`
- `opp115_policy_change` on `test`: accuracy `0.85`
- `maud_definition_includes_asset_deals` on `test`: accuracy `1.00`

One MAUD task exposed two realistic engineering issues during integration: request-serialization failures caused by noisy source text, and evaluation undercount caused by verbose multiple-choice answers such as `The correct answer is B`. The runner was then hardened with text sanitization, UTF-8 request handling, and better answer normalization. That is a strong interview story because it shows debugging and hardening, not just happy-path demos.
