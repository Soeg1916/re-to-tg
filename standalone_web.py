#!/usr/bin/env python3
"""
Standalone web dashboard for Miku Bot with zero external dependencies.
This script runs a simple Flask application on port 5000 to display the status of the bot.
"""

import os
import sys
import time
import json
from flask import Flask, render_template, jsonify, request

# Create Flask app
app = Flask(__name__)

# Simple configuration - everything in one file
BOT_RUNNING_FILE = '/tmp/bot_running.txt'
WEB_RUNNING_FILE = '/tmp/web_interface_running.txt'
DEFAULT_CHANNEL = os.getenv('TARGET_CHANNEL', '@Miku_nakano111')
MAIN_POST_INTERVAL = 600  # 10 minutes
IMAGE_POST_INTERVAL = 1200  # 20 minutes
REDDIT_POST_INTERVAL = 180  # 3 minutes

# Add start time for uptime tracking
START_TIME = time.time()

# Write a file to indicate the web interface is running
with open(WEB_RUNNING_FILE, 'w') as f:
    f.write(str(int(START_TIME)))

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
    uptime = int(time.time() - START_TIME)
    
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

if __name__ == '__main__':
    print("Starting standalone web dashboard...")
    print(f"Bot running file: {BOT_RUNNING_FILE}")
    print(f"Web running file: {WEB_RUNNING_FILE}")
    print(f"Target channel: {DEFAULT_CHANNEL}")
    print("==================================")
    app.run(host='0.0.0.0', port=5000)