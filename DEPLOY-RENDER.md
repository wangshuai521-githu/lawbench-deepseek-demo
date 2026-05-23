# Render deployment guide

This app can be deployed as a single Python web service because:

- the frontend is static files served by `backend/server.py`
- the backend exposes both the UI and the API
- DeepSeek access is controlled by the `DEEPSEEK_API_KEY` environment variable

## What is already prepared

- deployable backend host/port handling in `backend/server.py`
- `requirements.txt`
- `render.yaml`

## Before deployment

You should push this project to GitHub first.

Recommended repository contents:

- `backend/`
- `webapp/`
- `legalbench-main/`
- `render.yaml`
- `requirements.txt`

## Deploy on Render

1. Create a new GitHub repository and push the project.
2. Log in to Render.
3. Choose **New +** -> **Blueprint** or create a **Web Service** from the GitHub repo.
4. If using the repo directly, Render should detect:
   - build command: `pip install -r requirements.txt`
   - start command: `python backend/server.py`
5. Add environment variable:
   - `DEEPSEEK_API_KEY=your_key`
6. Deploy.

## Important runtime settings

Render requires web services to bind on `0.0.0.0`, which is already handled.
The service also reads `PORT` from the environment, which Render provides automatically.

## Shareable result

After deployment, you will get a public URL such as:

`https://your-app-name.onrender.com`

That link can be sent directly to HR or interviewers.

## Good demo workflow

For interviews, prepare both:

1. The public Render link for quick viewing
2. The local version as backup in case the network is unstable
