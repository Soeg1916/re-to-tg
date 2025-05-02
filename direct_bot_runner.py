#!/usr/bin/env python
"""
CRITICAL: This script is designed ONLY for direct execution in the run_miku_bot workflow.
It bypasses all Flask imports completely to avoid any port conflicts.
"""
import os
import sys
import logging
import time

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# IMPORTANT: DO NOT import Flask or any modules that import Flask here!
print("=========================================================")
print("DIRECT BOT RUNNER - NO FLASK")
print("Completely bypassing web components, using bot standalone mode only")
print("=========================================================")

# The trick is to only import what we need
try:
    # Import the minimal components needed for the bot
    from bot import setup_bot
    from api_clients import initialize_reddit_client
    
    # Initialize Reddit if available
    reddit = initialize_reddit_client()
    
    # Set up and start the bot
    print("Setting up Telegram bot...")
    updater = setup_bot()
    
    if updater:
        print("Bot started successfully!")
        print("Press Ctrl+C to stop the bot (though this won't work in a workflow)")
        
        # Keep the bot running
        try:
            updater.idle()
        except KeyboardInterrupt:
            print("Bot stopping...")
            updater.stop()
    else:
        print("Failed to start bot. Check that TELEGRAM_BOT_TOKEN is set correctly.")
        # Keep the process running even if bot setup failed
        while True:
            print("Waiting for configuration changes...")
            time.sleep(60)
except Exception as e:
    logger.error(f"Error running bot: {e}")
    import traceback
    traceback.print_exc()
    
    # Keep the process alive even after error
    while True:
        print("Error occurred. Waiting for manual intervention...")
        time.sleep(60)

if __name__ == "__main__":
    # This script is meant to be run directly
    pass