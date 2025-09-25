
# Deploy options

## 1) Streamlit Community Cloud (recommended, free)
1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io, sign in, click "New app", choose your repo/branch, and set **Main file** to `app.py`.
3. Add secrets if needed (e.g., `YT_API_KEY`) in **Settings → Secrets**.
4. Deploy. Your app URL will look like `https://<user>-<repo>-<branch>.streamlit.app`.

## 2) Hugging Face Spaces
1. Create a Space, choose **Streamlit** as SDK.
2. Upload `app.py` + `requirements.txt` (and any other files) to the Space.
3. The app builds and runs automatically.

## 3) Render.com (or Railway/Fly.io/Heroku-like)
- Use `Procfile` provided.
- On Render: create a **Web Service**, connect your repo, set **Start Command** auto-detected from `Procfile`.
- On Railway/Fly.io: use the provided `Dockerfile` to build & run.

## 4) Data refresh with GitHub Actions (optional)
- Add your YouTube API key in repo **Settings → Secrets and variables → Actions** as `YT_API_KEY`.
- Update the playlist URL in `.github/workflows/data-refresh.yml`.
- The workflow will run nightly to refresh `data/` and commit results.
