import os
import re
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Tuple

import pandas as pd
import praw
import streamlit as st
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go


# ────────────────────────────── env & reddit init ─────────────────────────────
if os.path.exists(".env"):  # load only in local/dev
    load_dotenv()

def init_reddit() -> praw.Reddit:
    """Create a PRAW `Reddit` instance from env / Streamlit secrets.
    Shows a helpful message and stops if credentials are missing.
    """
    client_id     = os.getenv("REDDIT_CLIENT_ID")     or st.secrets.get("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET") or st.secrets.get("REDDIT_CLIENT_SECRET")
    user_agent    = os.getenv("REDDIT_USER_AGENT")    or st.secrets.get("REDDIT_USER_AGENT")

    missing: list[str] = []
    if not client_id:
        missing.append("REDDIT_CLIENT_ID")
    if not client_secret:
        missing.append("REDDIT_CLIENT_SECRET")
    if not user_agent:
        missing.append("REDDIT_USER_AGENT")

    if missing:
        st.error(
            "Missing Reddit API credentials: " + ", ".join(missing) +
            "\n\nPlease add them in Settings → Secrets (or set environment variables)."
        )
        st.markdown("Add these entries in your Streamlit secrets:")
        st.code(
            """REDDIT_CLIENT_ID = "your_actual_client_id"
REDDIT_CLIENT_SECRET = "your_actual_client_secret"
REDDIT_USER_AGENT = "RedditScraper/1.0 by /u/yourusername""",
            language="toml",
        )
        st.stop()

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


# ──────────────────────────── Intelligent Categorization ────────────────────────────
def get_category_keywords() -> Dict[str, List[str]]:
    """Define keywords and patterns for each category like GummySearch."""
    return {
        "Pain Points": [
            "problem", "issue", "struggling", "frustrated", "annoying", "broken", "doesn't work",
            "hate", "terrible", "awful", "worst", "failing", "difficult", "hard", "impossible",
            "bug", "error", "crash", "slow", "expensive", "overpriced", "waste", "scam",
            "disappointed", "regret", "mistake", "wrong", "bad", "horrible", "sucks",
            "fix", "solve", "help", "support", "trouble", "stuck", "confused", "lost"
        ],
        "Solution Requests": [
            "how to", "how do", "how can", "what's the best", "recommend", "suggestion",
            "advice", "help me", "looking for", "need", "want", "seeking", "search",
            "alternative", "replacement", "substitute", "instead of", "better than",
            "tutorial", "guide", "instructions", "step by step", "walkthrough",
            "best way", "most effective", "proven method", "tips", "tricks", "hacks"
        ],
        "Money Talk": [
            "price", "cost", "expensive", "cheap", "budget", "affordable", "money", "pay",
            "subscription", "monthly", "yearly", "fee", "charge", "billing", "invoice",
            "worth it", "value", "roi", "return on investment", "save money", "deal",
            "discount", "coupon", "promo", "sale", "free", "pricing", "quote", "estimate",
            "$", "usd", "euro", "pound", "currency", "salary", "income", "revenue", "profit"
        ],
        "Hot Discussions": [
            "trending", "viral", "popular", "everyone", "talking about", "buzz", "hype",
            "news", "announcement", "update", "release", "launch", "breaking", "controversy",
            "debate", "argument", "discussion", "thoughts", "opinions", "what do you think",
            "hot take", "unpopular opinion", "controversial", "drama", "gossip"
        ],
        "Seeking Alternatives": [
            "alternative", "replacement", "substitute", "instead of", "better than", "similar to",
            "like", "competitor", "switch from", "migrate", "move away", "leave", "quit",
            "fed up", "done with", "tired of", "sick of", "switching", "changing",
            "compare", "vs", "versus", "difference", "which is better", "pros and cons"
        ],
        "Work/Study Related": [            
            "agenda", "assignment", "balance", "boss", "burnout", "campus", "career",            
            "class", "collaboration", "colleague", "college", "commute", "conference",
            "coursework", "coworker", "coworking", "cubicle", "deadline", "desk",
            "digital nomad", "dissertation", "distraction", "exam", "flexible work",
            "focus", "gpa", "grade", "group project", "home office", "homework",
            "hybrid", "internship", "lab", "lecture", "library", "manager", "meeting",
            "mentor", "networking", "notebook", "notes", "office", "open space",
            "overtime", "presentation", "productivity", "professor", "project",
            "promotion", "remote work", "revision", "routine", "schedule", "school",
            "seminar", "study", "studying", "syllabus", "task", "teacher", "teamwork",
            "telecommute", "thesis", "time blocking", "time management", "tutorial",
            "university", "workflow", "work-life", "work from home", "workspace",
        ],
    }

def classify_post_content(title: str, text: str) -> Tuple[str, float]:
    """
    Classify a post into one of the GummySearch categories.
    Returns (category, confidence_score).
    """
    keywords = get_category_keywords()
    content = f"{title.lower()} {text.lower()}"
    
    # Remove common noise words for better classification
    noise_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
    for word in noise_words:
        content = re.sub(rf'\b{word}\b', '', content)
    
    category_scores = {}
    
    for category, category_keywords in keywords.items():
        score = 0
        for keyword in category_keywords:
            # Use regex for better matching
            pattern = rf'\b{re.escape(keyword.lower())}\b'
            matches = len(re.findall(pattern, content))
            score += matches
            
            # Boost score for title matches (more important)
            title_matches = len(re.findall(pattern, title.lower()))
            score += title_matches * 2
        
        category_scores[category] = score
    
    # Get the category with highest score
    if max(category_scores.values()) == 0:
        return "General Discussion", 0.0
    
    best_category = max(category_scores, key=category_scores.get)
    max_score = category_scores[best_category]
    
    # Calculate confidence (normalize by content length and keyword count)
    total_words = len(content.split())
    confidence = min(max_score / max(total_words * 0.1, 1), 1.0)
    
    return best_category, confidence

def get_category_color(category: str) -> str:
    """Get color for category badges like GummySearch."""
    colors = {
        "Pain Points": "#FF4B4B",      # Red
        "Solution Requests": "#00D4FF", # Blue  
        "Money Talk": "#00FF88",       # Green
        "Hot Discussions": "#FF8C00",  # Orange
        "Seeking Alternatives": "#9966FF", # Purple
        "General Discussion": "#666666"  # Gray
    }
    return colors.get(category, "#666666")

def get_category_icon(category: str) -> str:
    """Get emoji icon for each category."""
    icons = {
        "Pain Points": "😣",
        "Solution Requests": "❓", 
        "Money Talk": "💰",
        "Hot Discussions": "🔥",
        "Seeking Alternatives": "🔄",
        "General Discussion": "💬"
    }
    return icons.get(category, "💬")


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

            # Classify the post content
            category, confidence = classify_post_content(post.title, post.selftext or "")
            
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
                "Category":            category,
                "Category Confidence": confidence,
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
        
        # Classify the post content
        category, confidence = classify_post_content(s.title, s.selftext or "")
        
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
            "Category":           category,
            "Category Confidence": confidence,
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


# ──────────────────────────────── Streamlit UI ─────────────────────────────
def apply_custom_css():
    """Apply custom CSS for modern dark theme and better styling."""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main theme colors */
    :root {
        --primary-color: #FF4B4B;
        --secondary-color: #FF6B6B;
        --background-dark: #0E1117;
        --surface-dark: #1A1D23;
        --surface-light: #262730;
        --text-primary: #FAFAFA;
        --text-secondary: #A6A6A6;
        --accent-blue: #00D4FF;
        --accent-green: #00FF88;
        --border-color: #333644;
    }
    
    /* Main container styling */
    .stApp {
        background: linear-gradient(135deg, var(--background-dark) 0%, #1a1d29 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--surface-dark) 0%, var(--surface-light) 100%);
        border-right: 1px solid var(--border-color);
    }
    
    /* Headers and titles */
    .main-header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        display: inline-block;
        vertical-align: middle;
    }
    
    .section-header {
        color: var(--text-primary);
        font-size: 1.8rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        border-bottom: 2px solid var(--accent-blue);
        padding-bottom: 0.5rem;
    }
    
    /* Cards and containers */
    .filter-card {
        background: var(--surface-dark);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    
    .stats-card {
        background: linear-gradient(135deg, var(--surface-dark), var(--surface-light));
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border: 1px solid var(--border-color);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 75, 75, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 75, 75, 0.4);
    }
    
    /* Metrics */
    .metric-container {
        background: var(--surface-dark);
        border-radius: 8px;
        padding: 1rem;
        border-left: 4px solid var(--accent-blue);
    }
    
    /* Selectbox and inputs */
    .stSelectbox > div > div {
        background: var(--surface-light);
        border: 1px solid var(--border-color);
        border-radius: 6px;
    }
    
    .stTextInput > div > div > input {
        background: var(--surface-light);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        color: var(--text-primary);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(90deg, var(--accent-green), #00cc77);
        border-radius: 8px;
    }
    
    .stError {
        background: linear-gradient(90deg, #ff4757, #ff3742);
        border-radius: 8px;
    }
    
    /* DataFrame styling */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Advanced filter section */
    .advanced-filters {
        background: var(--surface-dark);
        border: 1px solid var(--border-color);
        border-radius: 12px;
        padding: 1.5rem;
        margin-top: 1rem;
    }
    
    .filter-section {
        margin-bottom: 1rem;
        padding: 1rem;
        background: var(--surface-light);
        border-radius: 8px;
        border-left: 3px solid var(--accent-blue);
    }
    </style>
    """, unsafe_allow_html=True)

# ... rest of the code unchanged ...
# (The rest of your file was already correctly indented.)
