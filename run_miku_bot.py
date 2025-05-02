"""
Start only the Miku bot in standalone mode. 
This script is designed to be run by the run_miku_bot workflow.
It ONLY starts the bot without any web interface to avoid port conflicts.
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

print("========================================================")
print("✅ MIKU BOT RUNNER DETECTED - STANDALONE MODE ACTIVATED")
print("This script runs the bot WITHOUT the web interface")
print("to avoid port conflicts with the main application.")
print("========================================================")

try:
    # Import only what's needed for the bot, completely skipping Flask
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
    
    # Keep the process alive even after an error
    while True:
        logger.error("Error in bot execution. Waiting 60 seconds before retry...")
        time.sleep(60)