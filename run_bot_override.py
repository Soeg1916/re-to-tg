#!/usr/bin/env python
"""
Special bot runner that completely ignores Flask and port conflicts.
This script is designed to be run by the run_miku_bot workflow.
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

print("=====================================")
print("MIKU BOT DIRECT RUNNER")
print("This script completely bypasses Flask")
print("=====================================")

# Initialize necessary components without Flask
try:
    # Direct imports to avoid Flask
    from bot import setup_bot
    from api_clients import initialize_reddit_client

    # Set up the bot core components
    reddit = initialize_reddit_client()
    updater = setup_bot()

    if updater:
        print("Bot started successfully!")
        
        # Keep the bot running
        try:
            updater.idle()
        except KeyboardInterrupt:
            print("Bot stopping...")
        except Exception as e:
            logger.error(f"Error in bot operation: {e}")
            
            # Keep the process alive regardless of errors
            while True:
                print("Waiting 60 seconds before retry...")
                time.sleep(60)
                try:
                    # Try reconnecting the bot
                    updater = setup_bot()
                    if updater:
                        print("Bot reconnected!")
                        updater.idle()
                except Exception as e:
                    logger.error(f"Reconnection failed: {e}")
    else:
        print("Bot setup failed. Check that TELEGRAM_BOT_TOKEN is set.")
        # Keep the process alive
        while True:
            print("Waiting for configuration...")
            time.sleep(60)
except Exception as e:
    logger.error(f"Critical bot error: {e}")
    import traceback
    traceback.print_exc()
    
    # Keep the process alive no matter what
    while True:
        print("Critical error occurred. Waiting for manual intervention...")
        time.sleep(60)