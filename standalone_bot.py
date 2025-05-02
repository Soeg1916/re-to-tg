"""
A completely standalone Miku Bot implementation.
This script runs the bot without any web interface or Flask dependencies.
"""
import os
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def run_standalone():
    """Run the bot in completely standalone mode"""
    
    print("============================================")
    print("MIKU BOT STANDALONE RUNNER")
    print("Running bot without any Flask dependencies")
    print("============================================")
    
    try:
        # Import only what's needed for the bot
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
        logger.error(f"Error starting bot: {e}")
        import traceback
        traceback.print_exc()
        
        # Keep the process alive even on error
        while True:
            logger.error("Error in bot execution. Waiting 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    run_standalone()