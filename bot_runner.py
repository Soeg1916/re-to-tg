"""
Special script specifically designed for the run_miku_bot workflow.
This ensures the bot runs in standalone mode without Flask to avoid port conflicts.
"""
import os
import sys
import logging
import time

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def main():
    """
    Entry point for the run_miku_bot workflow.
    Force standalone mode to avoid port conflicts.
    """
    print("=================================================")
    print("DEDICATED WORKFLOW RUNNER FOR MIKU BOT")
    print("Completely bypassing Flask to avoid port conflicts")
    print("=================================================")
    
    try:
        # Directly import and use only the essential components for the bot
        from bot import setup_bot
        from api_clients import initialize_reddit_client
        
        # Initialize Reddit client
        reddit = initialize_reddit_client()
        print("Reddit client initialized" if reddit else "Reddit client initialization failed")
        
        # Set up and start the bot
        updater = setup_bot()
        
        if updater:
            print("Bot started successfully! Running in standalone mode.")
            # Keep the bot running
            updater.idle()
        else:
            print("Failed to start bot. Check your TELEGRAM_BOT_TOKEN.")
            # Keep the process alive
            while True:
                print("Waiting for configuration...")
                time.sleep(60)
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        import traceback
        traceback.print_exc()
        
        # Keep the process alive even after an error
        while True:
            logger.error("Error in bot execution. Waiting 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()