#!/usr/bin/env python
"""
Production-ready script to run the Miku bot in standalone mode.
This script is designed to be run by itself in production environments like Koyeb.
"""
import os
import logging
import socket
import sys
import time
import traceback
import requests
from bot import setup_bot

# Constants
BOT_RUNNING_MARKER = "/tmp/bot_running.txt"
BOT_LAST_SEEN_MARKER = "/tmp/bot_last_seen.txt"

def update_status_markers():
    """Create or update status marker files for the web dashboard"""
    try:
        # Create or update the running marker
        with open(BOT_RUNNING_MARKER, "w") as f:
            f.write("running")
            
        # Update the last seen timestamp
        with open(BOT_LAST_SEEN_MARKER, "w") as f:
            f.write(str(int(time.time())))
            
        logger.debug("Updated status markers")
    except Exception as e:
        logger.error(f"Error updating status markers: {e}")

# Set up logging with more verbose output for production
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Check if the bot is already running by detecting conflicts
def is_bot_already_running():
    """
    Check if another instance of this bot is already running.
    Attempts to make a getUpdates request to Telegram to see if there's a conflict.
    
    Returns:
        bool: True if bot is already running, False otherwise
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return False
        
    try:
        # Try to make a getUpdates request
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url, timeout=5)
        
        # If we got a conflict error, another instance is running
        if response.status_code == 409:
            logger.info("Conflict detected: Bot is already running in another instance.")
            return True
            
        # If successful, no other instance is running
        if response.ok:
            logger.info("No conflict detected: Bot is not running elsewhere.")
            return False
            
        # If some other error, log it and assume no conflict
        logger.warning(f"Unexpected response checking bot status: {response.status_code}")
        return False
    except Exception as e:
        logger.exception(f"Error checking if bot is running: {e}")
        return False

# Force standalone mode for workflow, but only if another instance isn't running
def force_standalone_bot():
    print("============================================")
    print("MIKU BOT FORCED STANDALONE MODE (RENDER)")
    print("This script is optimized for Render deployment")
    print("============================================")
    
    # Check if another instance is already running
    if is_bot_already_running():
        print("Another instance of the bot is already running!")
        print("This instance will act as a monitor only.")
        
        # Create status markers for the web dashboard
        update_status_markers()
        
        # Just keep this process alive without starting another bot
        try:
            while True:
                time.sleep(60)
                update_status_markers()  # Update markers periodically
                print("Monitoring... Bot is running in another instance.")
        except KeyboardInterrupt:
            print("Monitor stopped.")
        return
    
    try:
        # Initialize Reddit client
        from api_clients import initialize_reddit_client
        reddit_client = initialize_reddit_client()
        
        # Create initial status markers
        update_status_markers()
        
        # Start the bot directly without Flask
        updater = setup_bot()
        
        # Set up a background thread to update status markers
        import threading
        def status_updater():
            while True:
                try:
                    time.sleep(30)
                    update_status_markers()
                except Exception as e:
                    logger.error(f"Error in status updater: {e}")
        
        # Start the status updater thread
        status_thread = threading.Thread(target=status_updater, daemon=True)
        status_thread.start()
        
        # Keep the script running with proper signal handling
        if updater:
            print("Bot setup successful. Starting to poll for updates...")
            print("Status tracking enabled for web dashboard")
            updater.idle()
        else:
            print("Bot setup failed. Check logs for details.")
            # Keep updating status even if bot setup failed
            while True:
                time.sleep(30)
                update_status_markers()
    except Exception as e:
        logger.error(f"Error running standalone bot: {e}")
        traceback.print_exc()
        
if __name__ == "__main__":
    # Always run in standalone mode when executed directly
    force_standalone_bot()