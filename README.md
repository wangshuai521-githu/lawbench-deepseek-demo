# LegalBench x DeepSeek Interactive Demo

This project adapts the open-source LegalBench benchmark into an interactive evaluation app for DeepSeek models.

## What this project does

- loads LegalBench task folders and prompt templates
- previews dataset samples from `train.tsv` and `test.tsv`
- runs single-sample inference through the DeepSeek API
- runs small batch evaluations and computes accuracy
- stores benchmark artifacts locally
- provides a browser UI for task exploration and interaction

## Project structure

- `backend/server.py`: Python backend and API
- `webapp/`: frontend UI
- `legalbench-main/`: LegalBench source data
- `docs/frontend-backend-design.md`: dataset and system design notes
- `DEPLOY-RENDER.md`: public deployment guide
- `GITHUB-UPLOAD.md`: GitHub upload guide

## Local run

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
$env:DEEPSEEK_API_KEY="your_api_key_here"
python .\backend\server.py
```

Open:

- `http://127.0.0.1:8787`

## Demo tasks already tested

- `hearsay`
- `opp115_data_security`
- `opp115_policy_change`
- `maud_definition_includes_asset_deals`

## Deployment and hosting

Use:

- `GIT-HOSTING.md`
- `DEPLOY-RENDER.md`

If GitHub is not accessible from your current network, use Gitee first and mirror later.

## Offline sharing

For offline demos or HR sharing, use:

- `HR-OVERVIEW.md`
- `LOCAL-DEMO-STEPS.md`
- `build-share-package.ps1`
