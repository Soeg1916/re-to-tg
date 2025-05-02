#!/usr/bin/env python3
"""
Special script to keep the bot alive in the background.
This script runs the bot and monitors it, restarting it if needed.
"""
import os
import sys
import time
import signal
import subprocess
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('/tmp/bot_keeper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("bot_keeper")

# Path to the bot script
BOT_SCRIPT = "direct_miku_bot.py"

# Create the lock file or exit if it exists
def create_lock_file():
    if os.path.exists('/tmp/bot_keeper.lock'):
        logger.info("Keeper already running (lock file exists). Exiting.")
        sys.exit(0)
    else:
        with open('/tmp/bot_keeper.lock', 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f"Created lock file with PID {os.getpid()}")

# Clean up any lock files on exit
def cleanup_lock_files():
    for file_path in ['/tmp/bot_keeper.lock', '/tmp/bot_running.txt', '/tmp/bot_failed.txt']:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Removed lock file: {file_path}")
            except Exception as e:
                logger.error(f"Error removing lock file {file_path}: {e}")

# Handle signals gracefully
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, shutting down keeper")
    cleanup_lock_files()
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Main function to start and monitor the bot
def main():
    try:
        # Create lock file
        create_lock_file()
        
        # Remove any existing bot lock files
        for file_path in ['/tmp/bot_running.txt', '/tmp/bot_failed.txt']:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Log the start
        logger.info("=== Bot Keeper Starting ===")
        logger.info(f"Will start and monitor {BOT_SCRIPT}")
        
        # Set the REPL_WORKFLOW environment variable
        os.environ['REPL_WORKFLOW'] = 'run_miku_bot'
        
        # Start the bot process
        while True:
            logger.info("Starting bot process...")
            process = subprocess.Popen(
                [sys.executable, BOT_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Log the PID
            logger.info(f"Bot started with PID {process.pid}")
            
            # Monitor the process
            last_check = time.time()
            while process.poll() is None:
                # Process is still running
                time.sleep(5)
                
                # Every minute, check if the bot is still operational
                if time.time() - last_check > 60:
                    if not os.path.exists('/tmp/bot_running.txt'):
                        logger.warning("Bot running file not found, bot may be stuck")
                    last_check = time.time()
            
            # Process exited, check the exit code
            exit_code = process.returncode
            logger.info(f"Bot process exited with code {exit_code}")
            
            # Check if we should restart
            if os.path.exists('/tmp/bot_failed.txt'):
                with open('/tmp/bot_failed.txt', 'r') as f:
                    error = f.read()
                logger.error(f"Bot failed: {error}")
            
            # Wait before restarting
            logger.info("Waiting 5 seconds before restarting...")
            time.sleep(5)
    
    except Exception as e:
        logger.error(f"Keeper error: {e}")
    finally:
        cleanup_lock_files()

if __name__ == "__main__":
    main()