"""
Specialized workflow handler script that routes execution based on the current workflow.
This script should be copied to main.py to be run by the workflows.
"""
import os
import sys
import socket
import time
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# For simple port conflict detection
def is_port_in_use(port):
    """Check if a port is in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# CRITICAL: Detect which workflow we're running in
workflow = os.environ.get('REPL_WORKFLOW', '')
print(f"WORKFLOW HANDLER: Detected workflow '{workflow}'")

# If this is the run_miku_bot workflow, run the dedicated bot script
if workflow == 'run_miku_bot':
    print("==========================================")
    print("DETECTED: run_miku_bot workflow")
    print("Running bot in standalone mode without Flask")
    print("==========================================")
    
    try:
        # If bot_runner.py exists, run it
        import bot_runner
        sys.exit(0)
    except ImportError:
        # Otherwise fall back to run_bot.py
        try:
            import run_bot
            sys.exit(0)
        except ImportError:
            print("ERROR: Could not find bot runner modules")
            # Keep the process alive
            while True:
                print("Waiting 60 seconds...")
                time.sleep(60)
                
# If this is any other workflow, or no workflow is specified, 
# continue with the combined mode (web + bot)
else:
    print("==========================================")
    print("DETECTED: Combined mode workflow")
    print("Running web interface with bot in thread")
    print("==========================================")
    
    try:
        # If Flask is installed, import from the main_web module
        from flask import Flask
        print("Flask is available. Running web interface.")
        
        from main_web import app
        
        # Only set up the app if this is being run directly
        if __name__ == '__main__':
            print("Running main_web directly")
            from main_web import main
            main()
    except ImportError:
        print("ERROR: Flask is not installed")
        print("Falling back to standalone bot mode")
        
        try:
            # Try to run the bot in standalone mode
            import bot_runner
            sys.exit(0)
        except ImportError:
            print("ERROR: Could not find bot runner modules")
            # Keep the process alive
            while True:
                print("Waiting 60 seconds...")
                time.sleep(60)