#!/usr/bin/env python3
"""
Main entry point for all workflows.
This script detects which workflow is running and routes execution appropriately.
"""
import os
import sys

# Check if we're in a Replit workflow
workflow = os.environ.get('REPL_WORKFLOW', '')

print(f"WORKFLOW: {workflow}")

# CRITICAL PATH: If we're running in Gunicorn, use the web-only interface
if len(sys.argv) > 0 and 'gunicorn' in sys.argv[0] or 'gunicorn' in ' '.join(sys.argv):
    print("✅ GUNICORN DETECTED - IMPORTING WEB-ONLY MODULE")
    # Only the app object should be exported for gunicorn
    from web_only import app
    print("✅ LOADING WEB-ONLY VERSION - NO BOT FUNCTIONALITY")
    sys.exit(0)  # Doesn't actually exit; just stops rest of the code

# CRITICAL PATH: If we're in the run_miku_bot workflow, use a dedicated bot runner
if workflow == 'run_miku_bot':
    print("=" * 60)
    print("✅ MIKU BOT WORKFLOW DETECTED")
    print("✅ EXECUTING STANDALONE BOT SCRIPT")
    print("=" * 60)
    
    # Execute the standalone bot script that has no Flask dependencies
    import main_run_bot
    # This should never return
    sys.exit(0)

print("GUNICORN NOT DETECTED AND NOT IN run_miku_bot WORKFLOW")
print("No action taken in main.py")

# Function to check if a port is in use
def is_port_in_use(port):
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# If we get here, we're not in a special workflow, so run normally
# This means we're either in the Start application workflow or running directly

# Just run the web interface since the bot should be in the other workflow
try:
    from flask import Flask, render_template, jsonify
    
    # Create Flask app
    app = Flask(__name__)
    
    # Add start time for uptime tracking
    import time
    app.config['START_TIME'] = time.time()
    
    # Write a file to indicate the web interface is running
    with open('/tmp/web_interface_running.txt', 'w') as f:
        f.write('1')
    
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
    
    # If running directly, start the Flask app
    if __name__ == '__main__':
        print("==================================")
        print("DIRECT EXECUTION: Web-only Mode")
        print("Starting Flask app without bot")
        print("==================================")
        app.run(host='0.0.0.0', port=5000)
            
except ImportError:
    # If Flask is not available, just show an error
    print("Flask not available. Cannot run web interface.")
    print("Use 'run_miku_bot' workflow to run the bot only.")