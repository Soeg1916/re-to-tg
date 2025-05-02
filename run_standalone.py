"""
Special script to run ONLY the Miku bot without Flask.
This script is specifically designed for the run_miku_bot workflow.
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    print("=============================================")
    print("✅ MIKU BOT STANDALONE MODE ACTIVATED!")
    print("This will run WITHOUT Flask to avoid port conflicts")
    print("=============================================")
    
    # Mark that we're running the bot
    with open('/tmp/bot_running.txt', 'w') as f:
        f.write('1')
    
    try:
        # Import the necessary bot components 
        from api_clients import initialize_reddit_client
        from reddit_tracker import initialize_last_post_ids
        from bot import setup_bot
        
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
        
        # Keep the process alive even after an error
        import time
        while True:
            logger.error("Error running bot. Waiting 60 seconds before retry...")
            time.sleep(60)
    finally:
        # Clean up our marker file when the bot exits
        if os.path.exists('/tmp/bot_running.txt'):
            os.remove('/tmp/bot_running.txt')