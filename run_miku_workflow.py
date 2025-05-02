#!/usr/bin/env python
"""
Special standalone script to run ONLY the Miku bot.
This script completely bypasses the Flask app to avoid port conflicts.
It is designed specifically to be called by the run_miku_bot workflow.
"""
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Force the environment variable to indicate we're running in bot-only mode
os.environ['MIKU_BOT_ONLY'] = 'true'

print("=============================================")
print("MIKU BOT STANDALONE RUNNER")
print("Running ONLY the bot without any web interface")
print("This script completely bypasses Flask to avoid any port conflicts")
print("=============================================")

# Import and directly run the standalone bot implementation
try:
    from standalone_bot import run_standalone
    run_standalone()
except Exception as e:
    logger.error(f"Error running standalone bot: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    # This script is meant to be run directly
    pass