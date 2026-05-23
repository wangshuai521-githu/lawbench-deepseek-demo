# LegalBench x DeepSeek Interactive Demo

This project adapts the open-source LegalBench benchmark into an interactive evaluation app for DeepSeek models.

## What this project does

- loads LegalBench task folders and prompt templates
- previews dataset samples from `train.tsv` and `test.tsv`
- runs single-sample inference through the DeepSeek API
- runs small batch evaluations and computes accuracy
- stores benchmark artifacts locally
- provides a browser UI for task exploration and interaction

## Dataset design and system thinking

This project is built around the structure of LegalBench rather than a one-off prompt script.

Core design idea:

1. one benchmark task maps to one task directory
2. each task directory contains:
   - task description in `README.md`
   - prompt template in `base_prompt.txt`
   - dataset rows in `train.tsv` and/or `test.tsv`
3. each dataset row is rendered into the prompt template
4. the backend sends the rendered prompt to DeepSeek
5. the system normalizes the model output and compares it with the gold answer

Why this matters:

- it shows understanding of benchmark dataset organization
- it turns dataset structure into reusable backend and frontend abstractions
- it supports both interactive inference and repeatable small-batch evaluation

Related design note:

- `docs/frontend-backend-design.md`

## Project structure

- `backend/server.py`: Python backend and API
- `webapp/`: frontend UI
- `legalbench-main/`: LegalBench source data
- `docs/frontend-backend-design.md`: dataset and system design notes
- `DEPLOY-RENDER.md`: public deployment guide
- `GIT-HOSTING.md`: remote hosting guide

## Quick entry points

If you want to understand or present the project quickly, start here:

- `HR-PITCH.md`: short HR-facing project introduction
- `TECH-PITCH.md`: technical interviewer-facing project introduction
- `INTERVIEW-SCRIPT.md`: one-minute interview explanation
- `RESUME-ENTRY.md`: resume-ready project bullets
- `RECORDING-SCRIPT.md`: 1-2 minute demo recording script
- `SELF-INTRO-PROJECT.md`: how to mention the project in self-introduction
- `LOCAL-DEMO-STEPS.md`: shortest local demo steps
- `HR-OVERVIEW.md`: offline share note for HR or interviewers

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

## Recommended sharing strategy

At the current stage, the best presentation combination is:

1. source code on Gitee
2. local interactive demo for live interviews
3. offline dashboard for fast result viewing
4. HR-facing and interviewer-facing written summaries
