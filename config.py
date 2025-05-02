import os

# Telegram bot configuration
DEFAULT_CHANNEL = os.getenv("TELEGRAM_CHANNEL_USERNAME", "")

# Reddit API configuration
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MikuBot/1.0")

# Reddit subreddits to fetch Miku content from
MIKU_SUBREDDITS = [
    "5ToubunNoHanayome",
    "churchofmiku",
    "MikuNakano",
    "Nakano_Miku"
]

# API endpoints for anime images
WAIFU_PICS_API = "https://api.waifu.pics/sfw/waifu"
ANIME_PICS_API = "https://api.waifu.im/search"
# Use specifically nakano_miku tag to only get Miku from Quintessential Quintuplets
SAFEBOORU_API = "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&tags=nakano_miku+rating%3asafe"

# Scheduling intervals (in seconds)
# These can be customized via environment variables
MAIN_POST_INTERVAL = int(os.getenv("MAIN_POST_INTERVAL", 10)) * 60  # Every 10 minutes for photo+text posts
IMAGE_POST_INTERVAL = int(os.getenv("IMAGE_POST_INTERVAL", 10)) * 60  # Every 10 minutes for regular image posts
REDDIT_POST_INTERVAL = int(os.getenv("REDDIT_POST_INTERVAL", 2)) * 60  # Every 2 minutes for Reddit posts

# Paths for data storage
HISTORY_FILE = "post_history.json"
