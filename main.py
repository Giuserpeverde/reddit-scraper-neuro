import praw
import pandas as pd
import os
from dotenv import load_dotenv
import streamlit as st

# Load environment variables only in development
if os.path.exists('.env'):
    load_dotenv()

# Initialize Reddit API
def init_reddit():
    # Try getting from environment first (for production)
    client_id = os.environ.get("REDDIT_CLIENT_ID") or st.secrets["REDDIT_CLIENT_ID"]
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET") or st.secrets["REDDIT_CLIENT_SECRET"]
    user_agent = os.environ.get("REDDIT_USER_AGENT") or st.secrets["REDDIT_USER_AGENT"]
    
    return praw.Reddit(
        client_id=client_id,         
        client_secret=client_secret,      
        user_agent=user_agent
    )

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def get_subreddit_posts(_reddit, subreddit_name, time_filter="month"):
    try:
        subreddit = _reddit.subreddit(subreddit_name)
        posts_dict = {
            "Title": [], 
            "Post Text": [],
            "ID": [], 
            "Score": [],
            "Total Comments": [], 
            "Post URL": []
        }
        
        for post in subreddit.top(limit=None, time_filter=time_filter):
            posts_dict["Title"].append(post.title)
            posts_dict["Post Text"].append(post.selftext)
            posts_dict["ID"].append(post.id)
            posts_dict["Score"].append(post.score)
            posts_dict["Total Comments"].append(post.num_comments)
            posts_dict["Post URL"].append(post.url)
        
        return pd.DataFrame(posts_dict)
    except Exception as e:
        st.error(f"Error fetching subreddit posts: {str(e)}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def get_post_by_url(_reddit, url):
    try:
        submission = _reddit.submission(url=url)
        
        post_data = {
            "Title": submission.title,
            "Post Text": submission.selftext,
            "ID": submission.id,
            "Score": submission.score,
            "Total Comments": submission.num_comments,
            "Post URL": submission.url
        }
        
        post_comments = []
        submission.comments.replace_more(limit=None)
        
        for comment in submission.comments.list():
            comment_data = {
                "Comment Text": comment.body,
                "Score": comment.score,
                "Author": str(comment.author),
                "Created UTC": comment.created_utc
            }
            post_comments.append(comment_data)
        
        return pd.DataFrame([post_data]), pd.DataFrame(post_comments)
    except Exception as e:
        st.error(f"Error fetching post: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()

def main():
    st.title("Reddit Data Scraper")
    
    # Initialize Reddit instance
    reddit = init_reddit()
    
    # Sidebar for input parameters
    st.sidebar.header("Settings")
    scrape_option = st.sidebar.radio(
        "Choose scraping option:",
        ["Subreddit Posts", "Specific Post by URL"]
    )
    
    if scrape_option == "Subreddit Posts":
        st.header("Subreddit Posts Scraper")
        
        # Input fields
        subreddit_name = st.text_input("Enter subreddit name:", "selfhosted")
        time_filter = st.selectbox(
            "Time filter:",
            ["day", "week", "month", "year", "all"]
        )
        
        if st.button("Scrape Subreddit"):
            with st.spinner("Scraping posts..."):
                try:
                    df = get_subreddit_posts(reddit, subreddit_name, time_filter=time_filter)
                    st.success(f"Successfully scraped {len(df)} posts!")
                    
                    # Display the data
                    st.dataframe(df)
                    
                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        "Download CSV",
                        csv,
                        f"{subreddit_name}_posts.csv",
                        "text/csv",
                        key='download-csv'
                    )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    
    else:
        st.header("Post URL Scraper")
        
        post_url = st.text_input("Enter Reddit post URL:")
        
        if st.button("Scrape Post"):
            with st.spinner("Scraping post and comments..."):
                try:
                    post_df, comments_df = get_post_by_url(reddit, post_url)
                    
                    st.subheader("Post Details")
                    st.dataframe(post_df)
                    
                    st.subheader(f"Comments ({len(comments_df)} total)")
                    st.dataframe(comments_df)
                    
                    # Download buttons
                    post_csv = post_df.to_csv(index=False).encode('utf-8')
                    comments_csv = comments_df.to_csv(index=False).encode('utf-8')
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.download_button(
                            "Download Post CSV",
                            post_csv,
                            "post_details.csv",
                            "text/csv",
                            key='download-post'
                        )
                    with col2:
                        st.download_button(
                            "Download Comments CSV",
                            comments_csv,
                            "comments.csv",
                            "text/csv",
                            key='download-comments'
                        )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

