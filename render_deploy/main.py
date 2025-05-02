"""
Main entry point for Miku Bot web dashboard.
This file is used by Gunicorn to serve the web interface on Render.
"""

import os
import logging
import time
from flask import Flask, render_template, jsonify

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the app
app = Flask(__name__)

@app.route('/')
def index():
    """Main page to show bot status"""
    return render_template('index.html', title="Miku Bot Dashboard")

@app.route('/api/status')
def status():
    """API endpoint to check bot status"""
    # In Render deployment, bot is running in worker service
    # We'll use a different method to check status
    try:
        # Check for existence of the marker file that the bot worker creates
        bot_running = os.path.exists("/tmp/bot_running.txt")
        
        # Additionally check the timestamp if the file exists
        last_seen = None
        if bot_running and os.path.exists("/tmp/bot_last_seen.txt"):
            try:
                with open("/tmp/bot_last_seen.txt", "r") as f:
                    last_seen = int(f.read().strip())
            except:
                last_seen = int(time.time())
        
        return jsonify({
            "is_running": bot_running,
            "version": "1.0.2",
            "mode": "Render Deployment (Bot running in worker service)",
            "last_seen": last_seen
        })
    except Exception as e:
        logger.exception(f"Error checking bot status: {e}")
        return jsonify({
            "is_running": False,
            "version": "1.0.2",
            "mode": "Render Deployment (Status check error)",
            "error": str(e)
        }), 500

@app.route('/api/test_post/<post_type>')
def test_post(post_type):
    """API endpoint to manually trigger different types of posts"""
    return jsonify({
        "success": False,
        "message": "Manual posting disabled in Render deployment."
    })

# Run the app directly when not using Gunicorn
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)