#!/usr/bin/env python3
"""
Direct execution script for the run_miku_bot workflow.
This script is standalone and does not use Flask or any web components.
"""
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("MIKU_BOT_LAUNCHER")

def main():
    # Check if we're in the right workflow
    workflow = os.environ.get('REPL_WORKFLOW', '')
    print(f"Current workflow: {workflow}")
    
    # This script is designed to run in both direct execution and in the run_miku_bot workflow
    
    # Remove any lock files to ensure clean execution
    for file_path in ['/tmp/bot_running.txt', '/tmp/web_interface_running.txt', '/tmp/bot_failed.txt']:
        if os.path.exists(file_path):
            print(f"Removing lock file: {file_path}")
            os.remove(file_path)
    
    # Print banner
    print("=" * 60)
    print("MIKU BOT DIRECT LAUNCHER")
    print("This script bypasses main.py and all Flask dependencies")
    print("=" * 60)
    
    # Import bot code directly
    try:
        print("Launching standalone bot...")
        
        # Set a environment variable to indicate direct execution
        os.environ['MIKU_BOT_DIRECT_EXECUTION'] = 'true'
        
        # Execute the imported module - we avoid using 'import' to prevent circular imports
        command = [sys.executable, 'main_run_bot.py']
        result = subprocess.run(command)
        
        if result.returncode != 0:
            print(f"Bot process exited with error code: {result.returncode}")
            return 1
        
        return 0
    except Exception as e:
        print(f"Error launching bot: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())