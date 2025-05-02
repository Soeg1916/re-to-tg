"""
CRITICAL: This script is designed ONLY for direct execution in the run_miku_bot workflow.
It bypasses all Flask imports completely to avoid any port conflicts.
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

print("=====================================")
print("MIKU BOT DIRECT RUNNER")
print("This script completely bypasses Flask")
print("=====================================")

try:
    # Import only the essentials for the bot
    from api_clients import initialize_reddit_client
    from bot import setup_bot
    
    # Initialize Reddit
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
    logger.error(f"Critical error in bot startup: {e}")
    import traceback
    traceback.print_exc()
    
    # Keep the process alive even on error
    while True:
        logger.error("Error occurred. Waiting 60 seconds before retry...")
        time.sleep(60)