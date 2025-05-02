"""
A simple script to run only the Miku Bot without the Flask web interface.
This script is designed to be called by the run_miku_bot workflow.
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

def main():
    """
    Main entry point to run only the bot without the web interface
    """
    # Force the environment to indicate we're running in bot-only mode
    os.environ['MIKU_BOT_ONLY'] = 'true'
    
    print("=============================================")
    print("MIKU BOT RUNNER (NO WEB INTERFACE)")
    print("This script completely bypasses Flask and avoids port conflicts")
    print("=============================================")
    
    try:
        # Import and run the bot_only module
        from bot_only import run_standalone_bot
        run_standalone_bot()
    except Exception as e:
        logger.error(f"Error running standalone bot: {e}")
        import traceback
        traceback.print_exc()
        
        # Keep the process alive even after an error
        import time
        while True:
            logger.error("Error in bot execution. Waiting 60 seconds...")
            time.sleep(60)

if __name__ == "__main__":
    main()