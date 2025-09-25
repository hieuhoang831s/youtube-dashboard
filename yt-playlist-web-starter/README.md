
# YouTube Playlist & Comments Analyzer (Streamlit)

This is a tiny Streamlit app that reads:
- `youtube_playlist.xlsx` (sheet **Videos**) exported by your `you.py` / `you_plus.py`
- `all_comments.csv` exported when you run with `--all-comments`

## Run locally

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Make sure your files exist at /mnt/data/ or change paths in the sidebar
streamlit run app.py
```

## Refresh data
- Export playlist & details:
  ```bash
  python you.py --api-key YOUR_KEY --playlist PLAYLIST_URL --out-xlsx youtube_playlist.xlsx --all-comments
  ```
- Or the `you_plus.py` variant. Then refresh the Streamlit page.
