"""
Minimal Flask app for the 'Start application' workflow.
This is a completely stripped-down version to ensure it works with gunicorn.
"""

import os
import time
from flask import Flask, render_template, jsonify

# Create Flask app
app = Flask(__name__)

# Bot configuration
DEFAULT_CHANNEL = os.getenv('TARGET_CHANNEL')
MAIN_POST_INTERVAL = 600  # 10 minutes
IMAGE_POST_INTERVAL = 1200  # 20 minutes
REDDIT_POST_INTERVAL = 180  # 3 minutes
BOT_RUNNING_FILE = '/tmp/bot_running.txt'

# Add start time for uptime tracking
app.config['START_TIME'] = time.time()

@app.route('/')
def index():
    """Main page to show bot status"""
    return render_template('index.html')

@app.route('/status')
def status():
    """API endpoint to check bot status"""
    channel = DEFAULT_CHANNEL
    if channel and not channel.startswith('@'):
        channel = '@' + channel
        
    # Current uptime in seconds
    uptime = int(time.time() - app.config.get('START_TIME', time.time()))
    
    # Check if the bot is running in the run_miku_bot workflow
    bot_running = os.path.exists(BOT_RUNNING_FILE)
    
    # Get bot uptime if available
    bot_uptime = 0
    if bot_running and os.path.exists(BOT_RUNNING_FILE):
        try:
            with open(BOT_RUNNING_FILE, 'r') as f:
                start_time = int(f.read().strip() or '0')
                if start_time > 0:
                    bot_uptime = int(time.time() - start_time)
        except:
            bot_uptime = 0
    
    return jsonify({
        "status": "web_only",
        "bot_name": "Nakano Miku Bot",
        "version": "1.0.1",
        "channel": channel,
        "uptime_seconds": uptime,
        "uptime_human": f"{uptime // 86400}d {(uptime % 86400) // 3600}h {(uptime % 3600) // 60}m {uptime % 60}s",
        "bot_uptime_seconds": bot_uptime,
        "bot_uptime_human": f"{bot_uptime // 86400}d {(bot_uptime % 86400) // 3600}h {(bot_uptime % 3600) // 60}m {bot_uptime % 60}s",
        "intervals": {
            "main_fact_interval_minutes": MAIN_POST_INTERVAL // 60,
            "image_interval_minutes": IMAGE_POST_INTERVAL // 60,
            "reddit_interval_minutes": REDDIT_POST_INTERVAL // 60
        },
        "reddit_enabled": bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")),
        "bot_running": bot_running,
        "mode": "Web Interface Only (Bot running in separate workflow)",
        "keepalive": True
    })
    
@app.route('/api/test/post/<post_type>', methods=['GET'])
def test_post(post_type):
    """API endpoint to manually trigger different types of posts"""
    return jsonify({
        "success": False,
        "message": "This is a web-only instance. The bot is running in a separate workflow.",
        "instructions": "To test post functionality, go to the run_miku_bot workflow"
    }), 503

@app.route('/api/test/reddit-post', methods=['GET'])
def test_reddit_post():
    """Redirect to the new endpoint structure for Reddit posts"""
    return test_post('reddit')