"""
Shared configuration between bot and web interface
"""
import os

# Bot configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DEFAULT_CHANNEL = os.getenv('TARGET_CHANNEL')

# Intervals (in seconds)
MAIN_POST_INTERVAL = 600  # 10 minutes
IMAGE_POST_INTERVAL = 1200  # 20 minutes
REDDIT_POST_INTERVAL = 180  # 3 minutes

# Reddit configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = 'Miku Bot v1.0'

# Status file paths
BOT_RUNNING_FILE = '/tmp/bot_running.txt'
WEB_RUNNING_FILE = '/tmp/web_interface_running.txt'

# Subreddits to track
SUBREDDITS = [
    'MikuNakano',
    '5ToubunNoHanayome',
    'churchofmiku'  # This one returns 404 but we still try
]

# Alias for backward compatibility
MIKU_SUBREDDITS = SUBREDDITS

# API endpoints
WAIFU_PICS_API = "https://api.waifu.pics/sfw/waifu"
WAIFU_IM_API = "https://api.waifu.im/search/?included_tags=maid&included_tags=raiden-shogun&included_tags=oppai&is_nsfw=false"
SAFEBOORU_API = "https://safebooru.org/index.php?page=dapi&s=post&q=index&json=1&limit=100&tags=nakano_miku"