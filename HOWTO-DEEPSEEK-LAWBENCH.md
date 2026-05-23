# LawBench + DeepSeek Quick Start

This setup runs the `hearsay` task first. It is a simple `Yes/No` classification task, so it is the easiest way to verify the API path end to end.

## Files

- Repo: `C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench\legalbench-main`
- Runner: `C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench\run-hearsay-deepseek.ps1`

## Step 1: set your API key

Run this in PowerShell:

```powershell
$env:DEEPSEEK_API_KEY="your_api_key_here"
```

This only applies to the current PowerShell window.

## Step 2: run the task

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
.\run-hearsay-deepseek.ps1
```

To save predictions:

```powershell
.\run-hearsay-deepseek.ps1 -SavePredictions
```

## Step 3: read the output

The script prints:

- task name
- model name
- sample count
- accuracy
- one row per example with gold and prediction

If `-SavePredictions` is enabled, JSON output is written under:

```text
legalbench-main\outputs\
```

## What the script does

1. Reads `tasks\hearsay\base_prompt.txt`
2. Reads `tasks\hearsay\train.tsv`
3. Inserts each `text` value into the prompt
4. Calls `https://api.deepseek.com/chat/completions`
5. Extracts `Yes` or `No` from the model output
6. Computes simple accuracy against the dataset labels

## Next step

If you want, the next change is to make this runner generic so it can run other LawBench classification tasks too.
