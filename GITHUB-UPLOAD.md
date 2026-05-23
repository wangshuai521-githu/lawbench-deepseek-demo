# GitHub upload steps

Your project is ready for upload, but this machine still does not have `git` in `PATH`.

## Step 1: install Git for Windows

Download and install Git for Windows:

- https://git-scm.com/download/win

After installation, open a new PowerShell window and verify:

```powershell
git --version
```

## Step 2: create a GitHub repository

Create a new empty repository on GitHub, for example:

- `legalbench-deepseek-demo`

Do not initialize it with README, `.gitignore`, or license on GitHub.

## Step 3: initialize locally

Run these commands inside the project directory:

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
git init
git branch -M main
git add .
git commit -m "Build LegalBench x DeepSeek interactive demo"
```

## Step 4: connect to GitHub

Replace the URL below with your repository URL:

```powershell
git remote add origin https://github.com/<your-name>/legalbench-deepseek-demo.git
git push -u origin main
```

## Step 5: deploy to Render

After the repo is on GitHub, follow:

- `DEPLOY-RENDER.md`

## What will not be uploaded

The top-level `.gitignore` excludes:

- `legalbench-main/outputs/`
- `dashboard/data.json`
- `legalbench.zip`

This keeps the repository cleaner and avoids uploading local artifacts.
