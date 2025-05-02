import os, sys; wf = os.environ.get("REPL_WORKFLOW", ""); print(f"WORKFLOW: {wf}"); (wf == "run_miku_bot") and __import__("os").system("python direct_bot_runner.py") and sys.exit(0)
import logging
import os
import sys
import socket

# CRITICAL: Immediate workflow detection before ANY other imports
# Get the current workflow name from environment variable
current_workflow = os.environ.get('REPL_WORKFLOW', '')

# If this is the run_miku_bot workflow, immediately redirect to our direct bot runner
# This completely bypasses Flask and avoids any port conflicts
if current_workflow == 'run_miku_bot':
    print("==================================================")
    print("CRITICAL WORKFLOW DETECTION: run_miku_bot detected!")
    print("IMMEDIATELY redirecting to direct_bot_runner.py")
    print("This completely avoids importing Flask to prevent port conflicts")
    print("==================================================")
    
    try:
        # Execute our direct bot runner and exit
        # Using execfile equivalent for Python 3
        with open('direct_bot_runner.py') as f:
            code = compile(f.read(), 'direct_bot_runner.py', 'exec')
            exec(code, globals(), locals())
        sys.exit(0)
    except Exception as e:
        print(f"Error redirecting to direct_bot_runner.py: {e}")
        # If something goes wrong, fall back to standard execution

# Function to check if a port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Continue with normal imports for combined mode
from bot import setup_bot
from flask import Flask, render_template, jsonify
import threading

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

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
    # Get the current workflow name from environment variable
    current_workflow = os.environ.get('REPL_WORKFLOW', '')
    
    # FORCE STANDALONE MODE when in run_miku_bot workflow to avoid port conflicts
    if current_workflow == 'run_miku_bot':
        print("=========================================")
        print("CRITICAL: Detected run_miku_bot workflow")
        print("FORCING BOT to run in standalone mode...")
        print("This prevents port conflicts with other workflows")
        print("=========================================")
        
        # Directly import and run the standalone bot without any Flask components
        try:
            import standalone_bot
            standalone_bot.run_standalone()
        except Exception as e:
            import traceback
            print(f"ERROR running standalone bot: {e}")
            traceback.print_exc()
            # Sleep to keep the process alive even if there's an error
            import time
            while True:
                print("Attempting to recover from error...")
                time.sleep(60)
        return
    
    # If explicitly asked to run bot_only from command line arg
    elif len(sys.argv) > 1 and sys.argv[1] == 'bot_only':
        print("Starting Miku bot in standalone mode via command line argument...")
        
        # Import and run the completely standalone bot script
        import standalone_bot
        standalone_bot.run_standalone()
        return
    
    else:
        # Normal mode: start both the bot thread and Flask app
        print("Starting in COMBINED mode (web interface + bot)...")
        
        # Start the bot in a separate thread
        bot_thread = threading.Thread(target=start_bot_thread)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000)

# Only start the bot when running directly, not when imported by gunicorn
if __name__ == '__main__':
    main()
