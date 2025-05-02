#!/usr/bin/env python3
"""
Simple direct runner for the Miku bot with minimal dependencies.
This script is designed to be run directly by the run_miku_bot workflow.
"""

import os
import sys
import time
import logging
import signal
import subprocess

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("miku_direct_runner")

def signal_handler(sig, frame):
    logger.info("Received shutdown signal, cleaning up...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def run_bot_process():
    """Run the bot in a subprocess"""
    try:
        # Create a file to indicate the bot is running
        with open("/tmp/bot_running.txt", "w") as f:
            f.write(str(int(time.time())))
        
        logger.info("=== Starting Miku Bot in Direct Mode ===")
        
        # Execute direct_miku_bot.py directly
        direct_bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "direct_miku_bot.py")
        
        # Make it executable
        try:
            subprocess.run(['chmod', '+x', direct_bot_path], check=True)
        except Exception as e:
            logger.warning(f"Could not make direct bot script executable: {e}")
        
        # Start the bot in a subprocess
        bot_process = subprocess.Popen([sys.executable, direct_bot_path])
        
        # Wait for the process to complete
        logger.info(f"Bot process started with PID {bot_process.pid}")
        logger.info("Use Ctrl+C to stop")
        
        # Keep the main process running
        while True:
            if bot_process.poll() is not None:
                # Bot process has terminated, restart it
                logger.warning("Bot process terminated, restarting...")
                bot_process = subprocess.Popen([sys.executable, direct_bot_path])
                logger.info(f"Bot process restarted with PID {bot_process.pid}")
            
            # Check for the bot_running.txt file
            if not os.path.exists("/tmp/bot_running.txt"):
                # File was deleted, recreate it
                with open("/tmp/bot_running.txt", "w") as f:
                    f.write(str(int(time.time())))
            
            # Sleep to avoid high CPU usage
            time.sleep(5)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Error running bot: {e}")
    finally:
        # Clean up the bot_running.txt file
        if os.path.exists("/tmp/bot_running.txt"):
            try:
                os.remove("/tmp/bot_running.txt")
            except:
                pass

if __name__ == "__main__":
    run_bot_process()