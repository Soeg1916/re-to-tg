#!/usr/bin/env python3
"""
IMPORTANT: This is a special script designed ONLY for the run_miku_bot workflow.
It does NOT import Flask or any web components to avoid port conflicts.
"""
import os
import sys
import logging
import socket

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Get the current workflow from environment
workflow = os.environ.get('REPL_WORKFLOW', '')
print(f"WORKFLOW: {workflow}")

# Function to check if a port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Check if port 5000 is in use (the web interface is running)
if is_port_in_use(5000):
    print("Port 5000 is already in use. Running in bot-only mode.")

# Create a file marker to indicate this bot is running 
with open('/tmp/bot_running.txt', 'w') as f:
    f.write('1')

try:
    # Import necessary components - IMPORTANT: NO FLASK IMPORTS HERE
    from api_clients import initialize_reddit_client
    from reddit_tracker import initialize_last_post_ids
    from bot import setup_bot
    
    # Initialize Reddit
    print("Initializing Reddit client...")
    reddit = initialize_reddit_client()
    
    # Initialize Reddit post tracking
    print("Initializing Reddit post tracking...")
    initialize_last_post_ids() 
    
    # Set up and start the bot
    print("Setting up Telegram bot...")
    updater = setup_bot()
    
    if updater:
        print("✅ Bot started successfully!")
        # Start the bot and keep it running
        updater.idle()
    else:
        print("❌ Failed to start bot. Check your TELEGRAM_BOT_TOKEN.")
        
except Exception as e:
    logger.error(f"Error starting bot: {e}")
    import traceback
    traceback.print_exc()
    
    # Keep the process alive even if there's an error
    import time
    while True:
        logger.error("Bot crashed. Waiting 60 seconds before exiting...")
        time.sleep(60)
        
finally:
    # Cleanup the marker file
    if os.path.exists('/tmp/bot_running.txt'):
        os.remove('/tmp/bot_running.txt')