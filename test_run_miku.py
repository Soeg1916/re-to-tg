#!/usr/bin/env python
"""
Test script to simulate running in the run_miku_bot workflow
"""
import os
import sys

# Set the environment variable to simulate the workflow
os.environ['REPL_WORKFLOW'] = 'run_miku_bot'

# Import and run our workflow handler
import workflow_handler