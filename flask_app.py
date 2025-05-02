"""
Flask-only entry point for Gunicorn.
This file is used by the Start application workflow to run ONLY the web interface.
It completely skips the bot to avoid conflicts with the run_miku_bot workflow.
"""
import os
import time
import logging
import socket
from flask import Flask, render_template, jsonify

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Create Flask app
app = Flask(__name__)

# Add start time for uptime tracking
app.config['START_TIME'] = time.time()

# Mark that the bot is handled by another instance
with open('/tmp/bot_instance_running.txt', 'w') as f:
    f.write('1')

@app.route('/')
def index():
    """Main page to show bot status"""
    return render_template('index.html')

@app.route('/status')
def status():
    """API endpoint to check bot status"""
    import os
    import time
    from config import DEFAULT_CHANNEL, MAIN_POST_INTERVAL, IMAGE_POST_INTERVAL, REDDIT_POST_INTERVAL
    
    channel = DEFAULT_CHANNEL
    if channel and not channel.startswith('@'):
        channel = '@' + channel
        
    # Current uptime in seconds
    uptime = int(time.time() - app.config.get('START_TIME', time.time()))
    
    return jsonify({
        "status": "web_only",
        "bot_name": "Nakano Miku Bot",
        "version": "1.0.0",
        "channel": channel,
        "uptime_seconds": uptime,
        "uptime_human": f"{uptime // 86400}d {(uptime % 86400) // 3600}h {(uptime % 3600) // 60}m {uptime % 60}s",
        "intervals": {
            "main_fact_interval_minutes": MAIN_POST_INTERVAL // 60,
            "image_interval_minutes": IMAGE_POST_INTERVAL // 60,
            "reddit_interval_minutes": REDDIT_POST_INTERVAL // 60
        },
        "reddit_enabled": bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET")),
        "keepalive": True,
        "bot_instance_mode": "Web dashboard only - Bot is running in a separate workflow"
    })
    
@app.route('/api/test/post/<post_type>', methods=['GET'])
def test_post(post_type):
    """API endpoint to manually trigger different types of posts"""
    # In web-only mode, redirect to the status page and explain what's happening
    return jsonify({
        "success": False,
        "message": "This is a web-only instance. The bot is running in the run_miku_bot workflow.",
        "note": "Test posts can only be triggered from the workflow running the bot instance."
    }), 503

# Keeping the original endpoint for backward compatibility
@app.route('/api/test/reddit-post', methods=['GET'])
def test_reddit_post():
    """Redirect to the new endpoint structure for Reddit posts"""
    return test_post('reddit')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)