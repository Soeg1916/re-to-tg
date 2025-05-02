#!/usr/bin/env python3
"""
Start only the Miku bot in standalone mode. 
This script is designed to be run by the run_miku_bot workflow.
It ONLY starts the bot without any web interface to avoid port conflicts.
"""

# This file is the entry point for the "run_miku_bot" workflow
# It should be invoked directly by the workflow

import sys
import os

if __name__ == "__main__":
    print("=============================================")
    print("✅ MIKU BOT RUNNER - WORKFLOW ENTRY POINT")
    print("This script will launch the bot-only module")
    print("=============================================")
    
    # Run the dedicated standalone bot script
    if os.path.exists('run_bot_workflow.py'):
        os.execvp('python', ['python', 'run_bot_workflow.py'])
    else:
        print("ERROR: run_bot_workflow.py not found")
        sys.exit(1)