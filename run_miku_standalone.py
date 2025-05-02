"""
Special script to run ONLY the Miku bot without Flask.
This script is specifically designed for the run_miku_bot workflow.
"""
import os
import sys
import time
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

print("============================================")
print("MIKU BOT STANDALONE RUNNER")
print("This script completely bypasses Flask")
print("============================================")

try:
    # The simplest approach - directly import and run our bot override module
    # which completely bypasses Flask
    import run_bot_override
    
except Exception as e:
    logger.error(f"Critical error in bot startup: {e}")
    import traceback
    traceback.print_exc()
    
    # Keep alive on error
    while True:
        logger.error("Error occurred. Waiting 60 seconds before retry...")
        time.sleep(60)
        try:
            # Try direct access to bot module
            print("Attempting direct bot setup...")
            from bot import setup_bot
            bot = setup_bot()
            if bot:
                print("Bot recovered!")
                bot.idle()
        except Exception as e:
            logger.error(f"Recovery attempt failed: {e}")
            
if __name__ == "__main__":
    # This script is intended to be run directly
    pass