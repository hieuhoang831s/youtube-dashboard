
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime

# Try to import the user's analysis helpers if available
ANALYZER = None
try:
    import comment_report as cr
    ANALYZER = cr
except Exception:
    ANALYZER = None

st.set_page_config(page_title="YouTube Playlist Analyzer", page_icon="📊", layout="wide")

st.title("📊 YouTube Playlist & Comments Analyzer")
st.caption("Quick dashboard built from your exported files (playlist .xlsx + all_comments.csv).")

DATA_DIR = "/mnt/data"

xlsx_path = os.path.join(DATA_DIR, "youtube_playlist.xlsx")
csv_path  = os.path.join(DATA_DIR, "all_comments.csv")

# Sidebar inputs
st.sidebar.header("Inputs")
xlsx_path_in = st.sidebar.text_input("Path to playlist Excel (.xlsx)", value=xlsx_path)
csv_path_in  = st.sidebar.text_input("Path to all comments CSV", value=csv_path)
creator_handle = st.sidebar.text_input("Creator handle (optional, e.g. @cuoidihihihi)", value="")

st.sidebar.markdown("---")
st.sidebar.subheader("Filters")
min_date = st.sidebar.date_input("Min published date (comments)", value=None)
max_date = st.sidebar.date_input("Max published date (comments)", value=None)

# Load playlist
df_videos = None
if os.path.exists(xlsx_path_in):
    try:
        # Sheet "Videos" from you.py / you_plus.py
        df_videos = pd.read_excel(xlsx_path_in, sheet_name="Videos", engine="openpyxl")
        st.success(f"Loaded playlist: {os.path.abspath(xlsx_path_in)} ({len(df_videos)} videos)")
    except Exception as e:
        st.error(f"Failed to load playlist Excel: {e}")
else:
    st.info("Playlist Excel not found. Export with you.py/you_plus.py.")

# Load comments
df_comments = None
if os.path.exists(csv_path_in):
    try:
        df_comments = pd.read_csv(csv_path_in, encoding="utf-8-sig")
        st.success(f"Loaded comments CSV: {os.path.abspath(csv_path_in)} ({len(df_comments)} rows)")
    except Exception as e:
        st.error(f"Failed to load comments CSV: {e}")
else:
    st.info("Comments CSV not found. Enable --all-comments in you.py/you_plus.py to export.")

# Process comments
results = None
if df_comments is not None:
    if min_date or max_date:
        # Safe parse
        dts = pd.to_datetime(df_comments.get("PublishedAt"), errors="coerce")
        if min_date:
            df_comments = df_comments[dts >= pd.Timestamp(min_date)]
        if max_date:
            # include the whole day
            df_comments = df_comments[dts < pd.Timestamp(max_date) + pd.Timedelta(days=1)]

    if ANALYZER is not None and hasattr(ANALYZER, "analyze_comments"):
        try:
            results = ANALYZER.analyze_comments(df_comments, creator_handle=creator_handle or None)
        except Exception as e:
            st.warning(f"Falling back to built-in analysis due to error: {e}")

    if results is None:
        # Minimal fallback overview
        df = df_comments.copy()
        df["PublishedAt"] = pd.to_datetime(df["PublishedAt"], errors="coerce")
        total = len(df)
        n_top = int((df["Kind"] == "top").sum())
        n_reply = int((df["Kind"] == "reply").sum())
        pct_reply = round(100 * n_reply / total, 2) if total else 0.0
        unique_authors = df["Author"].nunique(dropna=True)
        avg_likes = round(pd.to_numeric(df["LikeCount"], errors="coerce").fillna(0).mean(), 2) if total else 0.0

        overview = pd.DataFrame([
            ["Total comments", total],
            ["Top-level", n_top],
            ["Replies", n_reply],
            ["Replies %", f"{pct_reply}%"],
            ["Unique commenters", unique_authors],
            ["Avg likes/comment", avg_likes],
        ], columns=["Metric","Value"])

        by_day = df.dropna(subset=["PublishedAt"]).copy()
        by_day["Date"] = by_day["PublishedAt"].dt.date
        activity_by_day = by_day.groupby("Date").size().reset_index(name="Comments").sort_values("Date")

        results = {
            "df": df,
            "overview": overview,
            "activity_by_day": activity_by_day,
            "top_commenters": df.groupby("Author").size().reset_index(name="TotalComments").sort_values("TotalComments", ascending=False),
            "top_liked": df.sort_values(pd.to_numeric(df["LikeCount"], errors="coerce").fillna(0), ascending=False)[["VideoID","Author","Text","LikeCount","PublishedAt"]].head(200)
        }

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    if df_videos is not None:
        st.subheader("Playlist overview")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Videos", len(df_videos))
        total_duration = int(df_videos.get("DurationSeconds", pd.Series(dtype=int)).fillna(0).sum())
        k2.metric("Total length", f"{total_duration//3600}h {(total_duration%3600)//60}m")
        k3.metric("Public/Unlisted/Private",
                  f'{(df_videos["PrivacyStatus"]=="public").sum()}/'
                  f'{(df_videos["PrivacyStatus"]=="unlisted").sum()}/'
                  f'{(df_videos["PrivacyStatus"]=="private").sum()}')
        k4.metric("Total views (sum)", int(pd.to_numeric(df_videos.get("Views"), errors="coerce").fillna(0).sum()))

        st.dataframe(df_videos[["PlaylistOrder","Title","Duration","Views","Likes","CommentsCount","PublishedAt","VideoURL"]])

with col2:
    if results is not None:
        st.subheader("Comments – Overview")
        st.dataframe(results["overview"])

if results is not None:
    st.subheader("Activity by day")
    ab = results["activity_by_day"]
    if len(ab) > 0:
        fig = plt.figure()
        plt.plot(ab["Date"], ab["Comments"], marker="o")
        plt.xticks(rotation=30)
        plt.title("Comments per day")
        plt.tight_layout()
        st.pyplot(fig)
    else:
        st.info("No dated comments to plot.")

    st.subheader("Top commenters")
    st.dataframe(results["top_commenters"].head(50))

    st.subheader("Top liked comments (preview)")
    st.dataframe(results["top_liked"].head(50))
else:
    st.warning("Load playlist Excel and comments CSV to see analysis.")

st.markdown("---")
st.caption("Tip: Regenerate data with your scripts (you.py / you_plus.py) and re-run this app to refresh.")
