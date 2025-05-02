#!/usr/bin/env python3
"""
A completely standalone script for the run_miku_bot workflow.
This script ONLY runs the bot with NO Flask dependencies.
"""
import os
import sys
import time
import socket
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def start_bot():
    """Run the bot in standalone mode"""
    print("=============================================")
    print("✅ COMPLETELY ISOLATED BOT RUNNER")
    print("This script has NO Flask imports/dependencies")
    print("=============================================")
    
    # Clean up existing lock files
    for file_path in ['/tmp/bot_running.txt', '/tmp/web_interface_running.txt', '/tmp/bot_failed.txt']:
        if os.path.exists(file_path):
            print(f"Removing lock file: {file_path}")
            os.remove(file_path)
    
    # Create a marker file to indicate the bot is running
    with open('/tmp/bot_running.txt', 'w') as f:
        f.write('1')
    
    try:
        # Import bot components directly
        from bot import setup_bot
        from api_clients import initialize_reddit_client
        from reddit_tracker import initialize_last_post_ids
        
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
        
        # Create error marker
        with open('/tmp/bot_failed.txt', 'w') as f:
            f.write(str(e))
        
        # Keep the process alive even after an error
        while True:
            logger.error("Error running bot. Waiting 60 seconds before retry...")
            time.sleep(60)
    finally:
        # Clean up our marker file when the bot exits
        if os.path.exists('/tmp/bot_running.txt'):
            os.remove('/tmp/bot_running.txt')

if __name__ == "__main__":
    start_bot()