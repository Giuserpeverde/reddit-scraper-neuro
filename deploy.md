# 🚀 Streamlit Cloud Deployment Guide

## Quick Deployment Steps

### 1. Prerequisites
- GitHub account
- Reddit API credentials
- Streamlit account (free at [share.streamlit.io](https://share.streamlit.io/))

### 2. Get Reddit API Credentials
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in the form:
   - **Name**: Your app name (e.g., "Reddit Data Scraper")
   - **App type**: Select "script"
   - **Description**: Brief description
   - **About URL**: Leave blank or add GitHub repo URL
   - **Redirect URI**: Enter `http://localhost:8080` (required but not used)
4. Click "Create app"
5. Note your credentials:
   - **Client ID**: The string under your app name
   - **Client Secret**: Click to reveal

### 3. Deploy to Streamlit Cloud
1. **Fork/Upload this repository** to your GitHub account
2. **Go to Streamlit Cloud**:
   - Visit [share.streamlit.io](https://share.streamlit.io/)
   - Sign in with your GitHub account
3. **Create new app**:
   - Click "New app"
   - Choose your forked repository
   - Set **Main file path**: `main.py`
   - Set **Python version**: 3.11 (recommended)
4. **Configure secrets**:
   - Before deploying, click "Advanced settings"
   - Go to "Secrets" tab
   - Add your Reddit API credentials:
   ```toml
   REDDIT_CLIENT_ID = "your_client_id_here"
   REDDIT_CLIENT_SECRET = "your_client_secret_here"
   REDDIT_USER_AGENT = "RedditScraper/1.0 by /u/yourusername"
   ```
5. **Deploy**: Click "Deploy!"

### 4. Post-Deployment
- Your app will be available at: `https://your-app-name.streamlit.app/`
- Share the URL with others to use your Reddit scraper
- Monitor usage and performance in the Streamlit Cloud dashboard

### 5. Local Testing (Optional)
Before deploying, you can test locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Create local secrets file
cp .streamlit/secrets.toml .streamlit/secrets_local.toml
# Edit the file with your credentials

# Run locally
streamlit run main.py
```

## 🔧 Configuration Options

### Environment Variables (Streamlit Secrets)
| Variable | Description | Example |
|----------|-------------|---------|
| `REDDIT_CLIENT_ID` | Reddit API client ID | `abcd1234efgh5678` |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | `your_secret_key_here` |
| `REDDIT_USER_AGENT` | User agent string | `RedditScraper/1.0 by /u/username` |

### Streamlit Configuration
The app includes optimized configuration in `.streamlit/config.toml`:
- Custom dark theme with Reddit colors
- Performance optimizations
- Security settings

## 🐛 Troubleshooting

### Common Issues:
1. **"Invalid credentials"**: Check your Reddit API keys
2. **App won't start**: Verify requirements.txt and Python version
3. **Rate limiting**: Reddit API has built-in rate limits (handled automatically)

### Performance Tips:
- Use date ranges instead of "All" for large subreddits
- Apply filters to reduce data volume
- The app uses caching for better performance

## 📞 Support
If you encounter issues:
1. Check the Streamlit Cloud logs
2. Verify your Reddit API credentials
3. Test locally first
4. Check Reddit API status

Happy scraping! 🎉
