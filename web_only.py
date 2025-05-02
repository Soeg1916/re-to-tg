"""
Web-only module for use with the Start application workflow.
This file is specifically designed to be used by Gunicorn.
It completely bypasses bot initialization to avoid conflicts.
"""
import os
import time
from flask import Flask, render_template, jsonify

# Create Flask app
app = Flask(__name__)

# Add start time for uptime tracking
app.config['START_TIME'] = time.time()

# Write a file to indicate the web interface is running
with open('/tmp/web_interface_running.txt', 'w') as f:
    f.write('1')

print("✅ LOADING WEB-ONLY VERSION - NO BOT FUNCTIONALITY")

@app.route('/')
def index():
    """Main page to show bot status"""
    return render_template('index.html')

@app.route('/status')
def status():
    """API endpoint to check bot status"""
    from config import DEFAULT_CHANNEL, MAIN_POST_INTERVAL, IMAGE_POST_INTERVAL, REDDIT_POST_INTERVAL
    
    channel = DEFAULT_CHANNEL
    if channel and not channel.startswith('@'):
        channel = '@' + channel
        
    # Current uptime in seconds
    uptime = int(time.time() - app.config.get('START_TIME', time.time()))
    
    # Check if the bot is running 
    bot_running = os.path.exists('/tmp/bot_running.txt')
    
    return jsonify({
        "status": "web_only",
        "bot_name": "Nakano Miku Bot",
        "version": "1.0.1",
        "channel": channel,
        "uptime_seconds": uptime,
        "uptime_human": f"{uptime // 86400}d {(uptime % 86400) // 3600}h {(uptime % 3600) // 60}m {uptime % 60}s",
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