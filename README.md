# Reddit Data Scraper 🚀

A modern, interactive Reddit data scraper built with Streamlit. Extract posts, comments, and analytics from any subreddit or specific Reddit post with a beautiful, responsive interface.

![Reddit Scraper](reddit-logo.png)

## ✨ Features

- **🔍 Subreddit Scraping**: Extract posts from any subreddit with advanced filtering options
- **🔗 Single Post Analysis**: Deep dive into specific posts and their entire comment threads
- **📊 Real-time Analytics**: Interactive charts and visualizations using Plotly
- **🎯 Advanced Filtering**: Filter by date range, score, comments, awards, NSFW content, and more
- **📥 Multiple Export Formats**: Download data as CSV or JSON
- **🌙 Modern Dark Theme**: Beautiful, responsive UI with custom CSS styling
- **⚡ Fast & Efficient**: Optimized data fetching with caching for better performance

## 🚀 Quick Start (Streamlit Cloud)

### 1. Deploy to Streamlit Cloud

[![Deploy to Streamlit Cloud](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

1. **Fork this repository** to your GitHub account
2. **Get Reddit API credentials**:
   - Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
   - Click "Create App" or "Create Another App"
   - Choose "script" as the app type
   - Note down your `client_id` and `client_secret`
3. **Deploy to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io/)
   - Click "New app" and connect your GitHub repository
   - Set the main file path to `main.py`
   - Configure secrets (see step 4)
4. **Configure App Secrets**:
   - In your Streamlit Cloud app dashboard, go to Settings > Secrets
   - Add your Reddit API credentials:
   ```toml
   REDDIT_CLIENT_ID = "your_client_id_here"
   REDDIT_CLIENT_SECRET = "your_client_secret_here"  
   REDDIT_USER_AGENT = "YourAppName/1.0 by /u/yourusername"
   ```
5. **Deploy your app!** 🚀

Your Reddit scraper will be live and accessible to everyone!

## 🛠️ Local Development

### Prerequisites

- Python 3.8 or higher
- Reddit API credentials (see above)

### Installation

1. **Clone the repository**:
```bash
   git clone https://github.com/pakagronglb/reddit-scraper.git
cd reddit-scraper
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
   - Copy `.streamlit/secrets.toml` to create your local secrets file
   - Or create a `.env` file with:
```env
   REDDIT_CLIENT_ID=your_client_id_here
   REDDIT_CLIENT_SECRET=your_client_secret_here
   REDDIT_USER_AGENT=YourAppName/1.0 by /u/yourusername
   ```

5. **Run the application**:
```bash
streamlit run main.py
```

The app will be available at `http://localhost:8501`

## 📋 Usage Guide

### Subreddit Scraping

1. **Enter Subreddit Name**: Type the subreddit name (without r/)
2. **Set Time Filter**: Choose from "All", "Last Week", "Last Month", "Last Year", or custom date range
3. **Configure Filters**: Set minimum score, comments, awards, and content preferences
4. **Start Scraping**: Click the "Start Scraping" button
5. **View Results**: Explore the data with interactive charts and tables
6. **Download Data**: Export your results as CSV or JSON

### Single Post Analysis

1. **Enter Post URL**: Paste the full Reddit post URL
2. **Configure Options**: Set comment filtering and sorting preferences
3. **Scrape Post**: Click "Scrape Post & Comments"
4. **Analyze Results**: Review post metrics and comment analytics
5. **Export Data**: Download post and comment data separately

## 🔧 Configuration

### Streamlit Configuration

The app includes optimized Streamlit configuration in `.streamlit/config.toml`:

- **Theme**: Custom dark theme with Reddit-inspired colors
- **Performance**: Optimized caching and data handling
- **Security**: XSRF protection and secure headers

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `REDDIT_CLIENT_ID` | Reddit API client ID | `abcd1234efgh5678` |
| `REDDIT_CLIENT_SECRET` | Reddit API client secret | `your_secret_key_here` |
| `REDDIT_USER_AGENT` | User agent string | `RedditScraper/1.0 by /u/username` |

## 📊 Data Export

The scraper provides comprehensive data export options:

### Post Data Fields
- ID, Title, Post Text, Subreddit
- Author, Created UTC, Score, Up-vote Ratio
- Total Comments, Total Awards, Flair
- Content flags (NSFW, Spoiler, OC)
- URLs and Permalinks

### Comment Data Fields
- Comment ID, Parent ID, Comment Text
- Author, Score, Created UTC
- Permalink, Submitter Status

## 🔒 Privacy & Rate Limiting

- **Rate Limiting**: The app respects Reddit's API rate limits
- **Data Privacy**: No data is stored permanently; everything is processed in real-time
- **Caching**: Uses Streamlit's caching for better performance (1-hour TTL)
- **Security**: API credentials are handled securely through Streamlit secrets

## 🐛 Troubleshooting

### Common Issues

1. **"Invalid credentials" error**:
   - Verify your Reddit API credentials
   - Ensure the user agent string is descriptive
   - Check that your Reddit app type is set to "script"

2. **"No posts found" error**:
   - Verify the subreddit name is correct
   - Check if the subreddit is private or banned
   - Try adjusting your date filters

3. **Rate limiting**:
   - The app automatically handles rate limits
   - If you hit limits, wait a few minutes before retrying

4. **App won't start**:
   - Check that all dependencies are installed
   - Verify Python version compatibility (3.8+)
   - Ensure environment variables are set correctly

### Performance Tips

- Use specific date ranges instead of "All" for large subreddits
- Apply filters to reduce data volume
- Clear browser cache if the app becomes slow

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit your changes: `git commit -m 'Add feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) for the web interface
- Uses [PRAW](https://praw.readthedocs.io/) for Reddit API access
- Visualizations powered by [Plotly](https://plotly.com/)
- Data processing with [Pandas](https://pandas.pydata.org/)

## 📞 Support

If you encounter any issues or have questions:

1. Check the [troubleshooting section](#-troubleshooting)
2. Search existing [issues](https://github.com/pakagronglb/reddit-scraper/issues)
3. Create a new issue with detailed information about the problem

---

**Happy Scraping! 🎉**

Made with ❤️ for the Reddit community
