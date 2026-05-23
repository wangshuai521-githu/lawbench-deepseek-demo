# Remote hosting steps

Your project is ready for remote hosting, but the machine does not have direct access to GitHub right now. Use Gitee first.

## Step 1: create an empty Gitee repository

Create a new empty repo on Gitee, for example:

- `legalbench-deepseek-demo`

Do not initialize it with README, `.gitignore`, or license.

## Step 2: initialize locally

Run these inside the project directory:

```powershell
Set-Location "C:\Users\wang'shuai\Documents\Codex\2026-05-22\lawbench-github-api-deepseek-github-lawbench"
git init
git branch -M main
git add .
git commit -m "Build LegalBench x DeepSeek interactive demo"
```

## Step 3: connect to Gitee

Replace the URL below with your Gitee repo URL:

```powershell
git remote add origin https://gitee.com/<your-name>/legalbench-deepseek-demo.git
git push -u origin main
```

## Step 4: later mirror to GitHub

When network conditions allow, you can mirror the same repo to GitHub for better portfolio visibility.

## What will not be uploaded

The top-level `.gitignore` excludes:

- `legalbench-main/outputs/`
- `dashboard/data.json`
- `legalbench.zip`

This keeps the repository cleaner and avoids uploading local artifacts.
