"""
A dedicated standalone script to run only the Telegram bot without the web interface.
This script is specifically designed to be called by the 'run_miku_bot' workflow.
"""
import os
import sys
import time
import logging
import socket

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Function to check if port is in use (to avoid conflicts)
def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def should_run_standalone():
    """Determine if we should run in standalone mode based on environment and port availability"""
    # Always run in standalone mode if the web interface is running
    if os.path.exists('/tmp/web_interface_running.txt'):
        logger.info("Web interface detected, running in standalone mode")
        return True
        
    # Check if port 5000 is already in use
    if is_port_in_use(5000):
        logger.info("Port 5000 is in use, running in standalone mode")
        return True
        
    # Get current workflow from environment
    workflow = os.environ.get('REPL_WORKFLOW', '')
    if workflow == 'run_miku_bot':
        logger.info("Detected run_miku_bot workflow, running in standalone mode")
        return True
        
    # Default to combined mode if none of the above conditions are met
    return False

def run_standalone_bot():
    """Run the bot in standalone mode without the Flask web interface"""
    print("========================================================")
    print("MIKU BOT - STANDALONE MODE")
    print("Running bot without web interface to avoid port conflicts")
    print("========================================================")
    
    # Check if there's already a bot running
    if os.path.exists('/tmp/bot_running.txt'):
        logger.warning("Bot is already running in another process!")
        logger.warning("Exiting to avoid conflicts...")
        sys.exit(1)
    
    # Create a file to indicate the bot is running
    with open('/tmp/bot_running.txt', 'w') as f:
        f.write('1')
        
    try:
        # Import the necessary bot components 
        from api_clients import initialize_reddit_client
        from reddit_tracker import initialize_last_post_ids
        from bot import setup_bot
        
        # Initialize the Reddit client
        reddit = initialize_reddit_client()
        
        # Initialize Reddit tracking
        initialize_last_post_ids()
        
        # Set up and start the bot
        updater = setup_bot()
        
        if updater:
            print("Bot started successfully!")
            # Keep the bot running
            updater.idle()
        else:
            print("Failed to start bot. Check your TELEGRAM_BOT_TOKEN.")
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        
        # Keep the process alive even after an error
        while True:
            logger.error("Error running bot. Waiting 60 seconds before retry...")
            time.sleep(60)
    finally:
        # Clean up our marker file when the bot exits
        if os.path.exists('/tmp/bot_running.txt'):
            os.remove('/tmp/bot_running.txt')

if __name__ == "__main__":
    # Only run the standalone bot if we determine it's appropriate
    if should_run_standalone():
        run_standalone_bot()
    else:
        print("Not running in standalone mode. Use main.py for combined mode.")
        sys.exit(0)