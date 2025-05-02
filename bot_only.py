"""
A dedicated standalone script to run only the Telegram bot without the web interface.
This script is specifically designed to be called by the 'run_miku_bot' workflow.
"""
import os
import sys
import logging
import socket

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Check if a port is in use
def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Determine if we should run in standalone mode
def should_run_standalone():
    """Determine if we should run in standalone mode based on environment and port availability"""
    # Always run standalone if the port is in use
    if is_port_in_use(5000):
        print("Port 5000 is already in use. Forcing standalone mode.")
        return True
        
    # Always run standalone if explicitly requested in environment
    if os.environ.get('MIKU_BOT_ONLY') == 'true':
        print("MIKU_BOT_ONLY environment variable is set. Forcing standalone mode.")
        return True
        
    # Always run standalone if we're in the run_miku_bot workflow
    workflow = os.environ.get('REPL_WORKFLOW', '')
    if workflow == 'run_miku_bot':
        print(f"Detected workflow: {workflow}. Forcing standalone mode.")
        return True
        
    # Otherwise, use combined mode
    return False

def run_standalone_bot():
    """Run the bot in standalone mode without the Flask web interface"""
    print("=============================================")
    print("RUNNING MIKU BOT IN STANDALONE MODE")
    print("No web interface will be started to avoid port conflicts")
    print("=============================================")
    
    try:
        # Import and set up the bot
        from bot import setup_bot
        from api_clients import initialize_reddit_client
        
        # Initialize the Reddit client
        reddit = initialize_reddit_client()
        print("Reddit client initialized successfully" if reddit else "Reddit client initialization failed")
        
        # Set up and start the bot
        updater = setup_bot()
        
        if updater:
            print("Bot started successfully. Listening for updates...")
            # Keep the bot running
            updater.idle()
        else:
            print("Failed to start bot. Check your TELEGRAM_BOT_TOKEN environment variable.")
            
    except Exception as e:
        logger.error(f"Error in standalone bot: {e}")
        import traceback
        traceback.print_exc()
        
        # Keep the process alive even after error
        import time
        while True:
            logger.error("Error in bot execution. Waiting 60 seconds before retry...")
            time.sleep(60)

if __name__ == "__main__":
    # Run the bot in standalone mode if we detect it's needed
    if should_run_standalone():
        run_standalone_bot()
    else:
        print("Not running in standalone mode. Use 'python main.py' for combined mode.")
        sys.exit(1)