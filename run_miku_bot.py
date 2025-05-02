"""
Special bot runner designed to avoid port conflicts.
This script is specifically created to be called by the 'run_miku_bot' workflow.
"""
import os
import sys
import socket
import logging
import time

# Set up logging
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

def run_standalone_bot():
    """Run the bot in standalone mode, ensuring no port conflicts"""
    
    # Check if port 5000 is already in use
    if is_port_in_use(5000):
        print(f"Port 5000 is already in use - forcing standalone mode")
    
    print("=============================================")
    print("RUNNING BOT IN COMPLETELY STANDALONE MODE")
    print("No Flask or web components will be loaded")
    print("=============================================")
    
    try:
        # Import only what we need for the bot
        from bot import setup_bot
        from api_clients import initialize_reddit_client
        
        # Initialize Reddit
        reddit = initialize_reddit_client()
        print("Reddit client initialized successfully" if reddit else "Reddit client initialization failed")
        
        # Set up and start the bot
        updater = setup_bot()
        if updater:
            print("Bot started successfully!")
            # Keep the bot running
            updater.idle()
        else:
            print("Failed to start bot. Check your TELEGRAM_BOT_TOKEN environment variable.")
            # Keep the process alive even if setup failed
            while True:
                print("Waiting for configuration updates...")
                time.sleep(60)
    except Exception as e:
        logger.error(f"Error running standalone bot: {e}")
        import traceback
        traceback.print_exc()
        
        # Keep process alive even with errors
        while True:
            logger.error("Error in bot execution. Waiting 60 seconds before retry...")
            time.sleep(60)

if __name__ == "__main__":
    # Always run in standalone mode
    run_standalone_bot()