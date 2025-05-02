#!/usr/bin/env python
"""
Main entry point for all workflows.
This script detects which workflow is running and routes execution appropriately.
"""
import os
import sys
import logging
import socket

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# CRITICAL: Check if we're in the run_miku_bot workflow BEFORE importing Flask
import sys, subprocess

# Get the workflow name from environment
workflow = os.environ.get('REPL_WORKFLOW', '')
print(f"WORKFLOW: {workflow}")

# Force environment check in case REPL_WORKFLOW isn't set correctly
workflow_forced = False

# Check if we're called by the run_miku_bot workflow
if os.path.exists('/tmp/workflow_name.txt'):
    with open('/tmp/workflow_name.txt', 'r') as f:
        stored_workflow = f.read().strip()
        if stored_workflow == 'run_miku_bot':
            workflow = 'run_miku_bot'
            workflow_forced = True
            print("FORCED WORKFLOW DETECTION: run_miku_bot (from file)")
else:
    # Create a file with our workflow name for future runs
    with open('/tmp/workflow_name.txt', 'w') as f:
        f.write(workflow)

# Manual override check - detect if port 5000 is already in use
import socket
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# If port 5000 is in use and we're not already forcing the workflow,
# assume we're in the secondary workflow
if is_port_in_use(5000) and not workflow_forced:
    workflow = 'run_miku_bot'
    print("FORCED WORKFLOW DETECTION: run_miku_bot (port 5000 in use)")

# Detect if we're in the bot-only workflow
if workflow == 'run_miku_bot':
    print("=============================================")
    print("✅ MIKU BOT STANDALONE MODE ACTIVATED!")
    print("This will run WITHOUT Flask to avoid port conflicts")
    print("=============================================")
    
    try:
        # Only import what we need for the bot, skip Flask entirely
        from api_clients import initialize_reddit_client
        from bot import setup_bot
        
        # Initialize Reddit client
        reddit = initialize_reddit_client()
        
        # Set up and start the bot
        updater = setup_bot()
        
        if updater:
            print("Bot started successfully!")
            # Keep the bot running
            updater.idle()
        else:
            print("Failed to start bot. Check your TELEGRAM_BOT_TOKEN.")
            
    except Exception as e:
        print(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        
        # Keep the process alive even on error
        import time
        while True:
            print("Error running bot. Waiting 60 seconds...")
            time.sleep(60)
            
    # Exit early to avoid importing Flask
    sys.exit(0)

# Continue with normal imports for combined mode
from flask import Flask, render_template, jsonify
import threading
from bot import setup_bot

# Function to check if a port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Create Flask app
app = Flask(__name__)

# Add start time for uptime tracking
import time
app.config['START_TIME'] = time.time()

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
        "status": "running",
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
        "keepalive": True
    })
    
@app.route('/api/test/post/<post_type>', methods=['GET'])
def test_post(post_type):
    """API endpoint to manually trigger different types of posts"""
    from api_clients import fetch_reddit_post, get_random_miku_image, reddit_client
    from facts import get_random_miku_fact, get_random_miku_caption
    from handlers import send_post
    from bot import get_bot
    
    # Validate post type
    valid_types = ['fact', 'image', 'reddit']
    if post_type not in valid_types:
        return jsonify({
            "success": False,
            "message": f"Invalid post type. Must be one of: {', '.join(valid_types)}"
        }), 400
    
    # Get the bot instance
    bot = get_bot()
    if not bot:
        return jsonify({
            "success": False,
            "message": "Bot not initialized yet. Try again in a few seconds."
        }), 400
    
    # Create a minimal context with the bot
    class MockContext:
        def __init__(self, bot_instance):
            self.bot = bot_instance
    
    context = MockContext(bot)
    
    # Prepare content based on post type
    content = None
    
    if post_type == 'fact':
        # Post a fact with image
        image_data = get_random_miku_image()
        if not image_data:
            return jsonify({
                "success": False,
                "message": "Could not fetch a Miku image. Check logs for details."
            }), 500
            
        content = {
            "image_url": image_data["image_url"],
            "caption": get_random_miku_fact(),
            "source": image_data.get("source", "")
        }
        
    elif post_type == 'image':
        # Post just an image with short caption
        image_data = get_random_miku_image()
        if not image_data:
            return jsonify({
                "success": False,
                "message": "Could not fetch a Miku image. Check logs for details."
            }), 500
            
        content = {
            "image_url": image_data["image_url"],
            "caption": get_random_miku_caption(),
            "source": image_data.get("source", "")
        }
        
    elif post_type == 'reddit':
        # Post from Reddit
        if not reddit_client:
            return jsonify({
                "success": False,
                "message": "Reddit client not initialized. Please add REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET environment variables."
            }), 400
            
        reddit_post = fetch_reddit_post()
        if not reddit_post:
            return jsonify({
                "success": False,
                "message": "Could not fetch a Reddit post. Check logs for details."
            }), 500
            
        content = reddit_post
        
    # Try to send the post
    try:
        # Ensure content is not None before sending
        if content:
            send_post(context, content)
            return jsonify({
                "success": True,
                "message": f"{post_type.capitalize()} post sent successfully!",
                "post": {
                    "type": post_type,
                    "image_url": content.get("image_url", ""),
                    "source": content.get("source", ""),
                    "caption_preview": content.get("caption", "")[:30] + "..." if len(content.get("caption", "")) > 30 else content.get("caption", "")
                }
            })
        else:
            return jsonify({
                "success": False,
                "message": "Failed to prepare content for posting"
            }), 500
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Error sending post: {str(e)}"
        }), 500

# Keeping the original endpoint for backward compatibility
@app.route('/api/test/reddit-post', methods=['GET'])
def test_reddit_post():
    """Redirect to the new endpoint structure for Reddit posts"""
    return test_post('reddit')

def start_bot_thread():
    """Run the Telegram bot in a separate thread"""
    setup_bot()

# Handle the startup differently based on workflow
def main():
    # Normal mode: start both the bot thread and Flask app
    print("Starting in COMBINED mode (web interface + bot)...")
    
    # Start the bot in a separate thread
    bot_thread = threading.Thread(target=start_bot_thread)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)

# Only start the bot when running directly, not when imported by gunicorn
# Also, don't start the bot if the env variable NO_BOT is set
if __name__ == '__main__':
    # Check if we've already detected another bot instance
    if os.path.exists('/tmp/bot_instance_running.txt'):
        print("Another bot instance is already running. This instance will only run the web interface.")
        # Run Flask without the bot thread
        app.run(host='0.0.0.0', port=5000)
    else:
        # Mark that we're running a bot instance
        with open('/tmp/bot_instance_running.txt', 'w') as f:
            f.write('1')
        # Run the full app with bot
        main()