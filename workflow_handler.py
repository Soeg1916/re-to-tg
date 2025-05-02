#!/usr/bin/env python
"""
Specialized workflow handler script that routes execution based on the current workflow.
This script should be copied to main.py to be run by the workflows.
"""
import os
import sys
import time
import logging

# Set up logging first
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Get the current workflow name
current_workflow = os.environ.get('REPL_WORKFLOW', '')
print(f"Current workflow: {current_workflow}")

# If we're in the run_miku_bot workflow, run only the bot in standalone mode
if current_workflow == 'run_miku_bot':
    print("============================================")
    print("DETECTED run_miku_bot WORKFLOW - RUNNING BOT ONLY")
    print("============================================")
    
    try:
        # Execute our direct bot runner script
        exec(open('run_bot_override.py').read())
        sys.exit(0)
    except Exception as e:
        print(f"ERROR running bot: {e}")
        # Keep the process alive even on error
        while True:
            print("Waiting for manual intervention...")
            time.sleep(60)
    
# Otherwise, continue with normal execution by importing the main module
else:
    print("Running in standard workflow mode, continuing with main module")
    import main
    
    # Check if we're running directly (not imported)
    if __name__ == "__main__":
        # Call the main function from main module
        main.main()