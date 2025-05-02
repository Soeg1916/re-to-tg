"""
Shared configuration between bot and web interface
"""
import os
import json

# Check for custom configuration file
CONFIG_FILE = 'bot_config.json'
HAS_CUSTOM_CONFIG = os.path.exists(CONFIG_FILE)

# Default configuration
DEFAULT_CONFIG = {
    "subreddits": [
        'MikuNakano',
        '5ToubunNoHanayome',
        'churchofmiku'  # This one returns 404 but we still try
    ],
    "intervals": {
        "fact": 600,  # 10 minutes
        "image": 1200,  # 20 minutes
        "reddit": 180   # 3 minutes
    },
    "target_channel": os.getenv('TARGET_CHANNEL', '')
}

# Load custom configuration if available
if HAS_CUSTOM_CONFIG:
    try:
        with open(CONFIG_FILE, 'r') as f:
            CUSTOM_CONFIG = json.load(f)
    except Exception as e:
        print(f"Error loading custom config: {e}")
        CUSTOM_CONFIG = DEFAULT_CONFIG
else:
    CUSTOM_CONFIG = DEFAULT_CONFIG

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEFAULT_CHANNEL = os.getenv('TARGET_CHANNEL')
TARGET_CHANNEL = CUSTOM_CONFIG.get('target_channel', DEFAULT_CHANNEL)

# Intervals (in seconds)
MAIN_POST_INTERVAL = CUSTOM_CONFIG.get('intervals', {}).get('fact', 600)
IMAGE_POST_INTERVAL = CUSTOM_CONFIG.get('intervals', {}).get('image', 1200)
REDDIT_POST_INTERVAL = CUSTOM_CONFIG.get('intervals', {}).get('reddit', 180)

# Reddit configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = 'Miku Bot v1.0'

# Status file paths
BOT_RUNNING_FILE = '/tmp/bot_running.txt'
WEB_RUNNING_FILE = '/tmp/web_interface_running.txt'

# Subreddits to track
SUBREDDITS = CUSTOM_CONFIG.get('subreddits', DEFAULT_CONFIG['subreddits'])

# Alias for backward compatibility
MIKU_SUBREDDITS = SUBREDDITS

# API endpoints
WAIFU_PICS_API = "https://api.waifu.pics/sfw/waifu"
WAIFU_IM_API = "https://api.waifu.im/search/?included_tags=maid&included_tags=raiden-shogun&included_tags=oppai&is_nsfw=false"
SAFEBOORU_API = "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit=100&tags=nakano_miku"
ANIME_PICS_API = "https://api.waifu.pics/sfw/megumin"

# History tracking
HISTORY_FILE = "post_history.json"