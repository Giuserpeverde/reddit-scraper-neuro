import os
from datetime import datetime, date, timedelta, timezone

import pandas as pd
import praw
import streamlit as st
from dotenv import load_dotenv


# ────────────────────────────── env & reddit init ──────────────────────────────
if os.path.exists(".env"):  # load only in local/dev
    load_dotenv()

def init_reddit() -> praw.Reddit:
    """Create a PRAW `Reddit` instance from env / Streamlit secrets."""
    client_id     = os.getenv("REDDIT_CLIENT_ID")     or st.secrets["REDDIT_CLIENT_ID"]
    client_secret = os.getenv("REDDIT_CLIENT_SECRET") or st.secrets["REDDIT_CLIENT_SECRET"]
    user_agent    = os.getenv("REDDIT_USER_AGENT")    or st.secrets["REDDIT_USER_AGENT"]
    return praw.Reddit(client_id=client_id,
                       client_secret=client_secret,
                       user_agent=user_agent)


# ─────────────────────── helpers: fetch posts & single thread ──────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def get_subreddit_posts(
    _reddit: praw.Reddit,
    name: str,
    filter_type: str = "All",
    start: date | None = None,
    end:   date | None = None,
) -> pd.DataFrame:
    """
    Scrape **ALL** posts that fall inside the requested window.
    • “All”, “Last Week”, “Last Month”, “Last Year” use rolling windows  
    • “Date Range” honours the explicit `start` → `end` span  
    Note: Reddit’s API caps results at ~1 000 posts per listing; for huge
    subs you’ll hit that limit unless you integrate Pushshift.
    """
    try:
        sub   = _reddit.subreddit(name)
        now   = datetime.now(timezone.utc)
        start_ts, end_ts = 0, now.timestamp()

        if filter_type == "Last Week":
            start_ts = (now - timedelta(days=7)).timestamp()
        elif filter_type == "Last Month":
            start_ts = (now - timedelta(days=30)).timestamp()
        elif filter_type == "Last Year":
            start_ts = (now - timedelta(days=365)).timestamp()
        elif filter_type == "Date Range" and start and end:
            start_ts = datetime.combine(start, datetime.min.time(), tzinfo=timezone.utc).timestamp()
            end_ts   = datetime.combine(end,   datetime.max.time(), tzinfo=timezone.utc).timestamp()

        rows: list[dict] = []
        for post in sub.new(limit=None):            # newest → oldest
            if post.created_utc > end_ts:
                continue
            if post.created_utc < start_ts:         # we’re past window → stop
                break

            rows.append({
                "ID":                  post.id,
                "Title":               post.title,
                "Post Text":           post.selftext,
                "Subreddit":           post.subreddit.display_name,
                "Author":              str(post.author),
                "Created UTC":         datetime.fromtimestamp(post.created_utc, tz=timezone.utc),
                "Score":               post.score,
                "Up-vote Ratio":       post.upvote_ratio,
                "Total Comments":      post.num_comments,
                "Total Awards":        post.total_awards_received,
                "Flair":               post.link_flair_text,
                "Is Original Content": post.is_original_content,
                "Over 18":             post.over_18,
                "Spoiler":             post.spoiler,
                "Num Cross-posts":     post.num_crossposts,
                "Permalink":           f"https://www.reddit.com{post.permalink}",
                "Post URL":            post.url,
            })
        return pd.DataFrame(rows)

    except Exception as exc:
        st.error(f"Error fetching subreddit posts: {exc}")
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def get_post_by_url(_reddit: praw.Reddit, url: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return a DataFrame for the submission + its **entire** comment tree."""
    try:
        s = _reddit.submission(url=url)
        post_df = pd.DataFrame([{
            "ID":            s.id,
            "Title":         s.title,
            "Post Text":     s.selftext,
            "Subreddit":     s.subreddit.display_name,
            "Author":        str(s.author),
            "Created UTC":   datetime.fromtimestamp(s.created_utc, tz=timezone.utc),
            "Score":         s.score,
            "Up-vote Ratio": s.upvote_ratio,
            "Total Comments": s.num_comments,
            "Total Awards":   s.total_awards_received,
            "Flair":          s.link_flair_text,
            "Is Original Content": s.is_original_content,
            "Over 18":            s.over_18,
            "Spoiler":            s.spoiler,
            "Num Cross-posts":    s.num_crossposts,
            "Permalink":          f"https://www.reddit.com{s.permalink}",
            "Post URL":           s.url,
        }])

        s.comments.replace_more(limit=None)
        comments = [{
            "Comment ID":   c.id,
            "Parent ID":    c.parent_id,
            "Comment Text": c.body,
            "Author":       str(c.author),
            "Score":        c.score,
            "Created UTC":  datetime.fromtimestamp(c.created_utc, tz=timezone.utc),
            "Permalink":    f"https://www.reddit.com{c.permalink}",
            "Is Submitter": c.is_submitter,
        } for c in s.comments.list()]

        return post_df, pd.DataFrame(comments)

    except Exception as exc:
        st.error(f"Error fetching post: {exc}")
        return pd.DataFrame(), pd.DataFrame()


# ──────────────────────────────── Streamlit UI ────────────────────────────────
def main() -> None:
    st.set_page_config("Reddit Scraper", layout="wide")
    st.title("📥 Reddit Data Scraper")

    reddit = init_reddit()

    st.sidebar.header("Settings")
    mode = st.sidebar.radio("Choose scraping option:", ("Subreddit Posts", "Specific Post by URL"))

    # ── Subreddit mode ─────────────────────────────────────────────────────────
    if mode == "Subreddit Posts":
        st.header("Subreddit Posts Scraper")

        sub_name   = st.text_input("Enter subreddit name:", "selfhosted")
        filter_opt = st.selectbox(
            "Select date filter:",
            ("All", "Last Week", "Last Month", "Last Year", "Date Range")
        )

        start_d = end_d = None
        if filter_opt == "Date Range":
            col1, col2 = st.columns(2)
            with col1:
                start_d = st.date_input("Start date", value=date.today() - timedelta(days=7))
            with col2:
                end_d   = st.date_input("End date",   value=date.today())
            if start_d > end_d:
                st.warning("⚠️ Start date must be before end date.")

        if st.button("Scrape Subreddit"):
            with st.spinner("Collecting posts …"):
                df = get_subreddit_posts(
                    reddit, sub_name,
                    filter_type=filter_opt,
                    start=start_d, end=end_d,
                )

            st.success(f"Fetched {len(df)} posts")
            st.dataframe(df, use_container_width=True)

            if not df.empty:
                st.download_button(
                    "Download CSV",
                    df.to_csv(index=False).encode(),
                    f"{sub_name}_posts.csv",
                    "text/csv"
                )

    # ── Single-thread mode ─────────────────────────────────────────────────────
    else:
        st.header("Post URL Scraper")

        url = st.text_input("Enter Reddit post URL:")
        if st.button("Scrape Post"):
            with st.spinner("Fetching submission & comments …"):
                post_df, cmt_df = get_post_by_url(reddit, url)

            if not post_df.empty:
                st.subheader("Post Details")
                st.dataframe(post_df, use_container_width=True)

                st.subheader(f"Comments ({len(cmt_df)})")
                st.dataframe(cmt_df, use_container_width=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download Post CSV",
                        post_df.to_csv(index=False).encode(),
                        "post_details.csv",
                        "text/csv"
                    )
                with col2:
                    st.download_button(
                        "Download Comments CSV",
                        cmt_df.to_csv(index=False).encode(),
                        "comments.csv",
                        "text/csv"
                    )

if __name__ == "__main__":
    main()
