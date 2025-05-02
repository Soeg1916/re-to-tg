"""
A minimal Flask app for the 'Start application' workflow.
"""

import os
import logging
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
    bot_running = os.path.exists("/tmp/bot_running.txt")
    return jsonify({
        "is_running": bot_running,
        "version": "1.0.1",
        "mode": "Web Interface Only (Bot is running in a separate workflow)"
    })

@app.route('/api/test_post/<post_type>')
def test_post(post_type):
    """API endpoint to manually trigger different types of posts"""
    return jsonify({
        "success": False,
        "message": "Test posting is only available directly in the bot workflow."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)