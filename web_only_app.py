"""
A simplified web-only version of the Flask app for the Miku bot dashboard.
This version is specifically designed to be used with gunicorn.
"""

import os
import json
import time
from flask import Flask, render_template, jsonify, redirect, url_for
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("miku_web")

# Create the app
app = Flask(__name__)

# Status file path
STATUS_FILE = "/tmp/bot_running.txt"

@app.route('/')
def index():
    """Main page to show bot status"""
    return render_template('index.html', title="Miku Bot Dashboard")

@app.route('/api/status')
def status():
    """API endpoint to check bot status"""
    is_running = False
    last_seen = None
    
    try:
        if os.path.exists(STATUS_FILE):
            with open(STATUS_FILE, 'r') as f:
                timestamp = int(f.read().strip())
                last_seen = timestamp
                # Bot is considered running if the status file was updated in the last 30 seconds
                is_running = (time.time() - timestamp) < 30
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
    
    post_history = []
    try:
        # Try to load the post history from the JSON file
        if os.path.exists("post_history.json"):
            with open("post_history.json", 'r') as f:
                post_history = json.load(f)
    except Exception as e:
        logger.error(f"Error loading post history: {e}")
    
    return jsonify({
        "is_running": is_running,
        "last_seen": last_seen,
        "post_history": post_history[:10]  # Limit to last 10 posts
    })

@app.route('/api/test_post/<post_type>')
def test_post(post_type):
    """API endpoint to manually trigger different types of posts (web-only version)"""
    return jsonify({
        "success": False,
        "message": "Test posting is only available when the bot is running in the same process. Use the run_miku_bot workflow to access the bot directly."
    })

@app.route('/api/test_reddit_post')
def test_reddit_post():
    """Redirect to the new endpoint structure for Reddit posts"""
    return redirect(url_for('test_post', post_type='reddit'))

# This is a special application instance for Gunicorn
app.logger.setLevel(logging.INFO)
logger.info("Web-only version of the Miku Bot dashboard loaded")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)