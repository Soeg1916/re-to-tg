"""
A simple script to run only the Miku Bot without the Flask web interface.
This script is designed to be called by the run_miku_bot workflow.
"""
import os
import logging
import sys

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
    print("============================================")
    print("MIKU BOT STANDALONE RUNNER")
    print("Running bot WITHOUT Flask web interface")
    print("This avoids port conflicts with other services")
    print("============================================")
    
    # Import and run standalone bot implementation
    from standalone_bot import run_standalone
    run_standalone()

if __name__ == "__main__":
    main()