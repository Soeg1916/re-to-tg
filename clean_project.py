#!/usr/bin/env python3
"""
Script to clean up redundant files from the project.
This script identifies essential files and creates a directory with only those files.
"""
import os
import shutil
import sys

# Essential files for the project
ESSENTIAL_FILES = [
    # Core functionality
    'api_clients.py',
    'bot.py',
    'config.py',
    'facts.py',
    'handlers.py',
    'reddit_tracker.py',
    'scheduler.py',
    'storage.py',
    
    # Main application files
    'main.py',
    'app_simple.py',
    
    # Production deployment files
    'run_miku_bot_standalone.py',
    'healthcheck.py',
    'Procfile',
    'requirements.txt',
    
    # Any additional configuration files
    '.env',
    'README.md',
]

# Essential directories
ESSENTIAL_DIRS = [
    'templates',
    'static'
]

def create_clean_project(dest_dir='clean_project'):
    """
    Create a clean project with only essential files.
    
    Args:
        dest_dir: Destination directory for clean project
    """
    # Create the destination directory if it doesn't exist
    if os.path.exists(dest_dir):
        print(f"Destination directory {dest_dir} already exists. Please remove it first.")
        return
        
    os.makedirs(dest_dir)
    print(f"Created destination directory: {dest_dir}")
    
    # Copy essential files
    for file_name in ESSENTIAL_FILES:
        if os.path.exists(file_name):
            shutil.copy2(file_name, os.path.join(dest_dir, file_name))
            print(f"Copied {file_name}")
        else:
            print(f"Warning: Essential file {file_name} not found")
    
    # Copy essential directories
    for dir_name in ESSENTIAL_DIRS:
        if os.path.exists(dir_name):
            dest_path = os.path.join(dest_dir, dir_name)
            shutil.copytree(dir_name, dest_path)
            print(f"Copied directory {dir_name}")
        else:
            print(f"Warning: Essential directory {dir_name} not found")
    
    print(f"\nProject cleaned successfully! You can find the clean project in: {dest_dir}")
    print("This directory contains only the essential files needed for deployment.")

if __name__ == "__main__":
    dest_dir = 'clean_project'
    if len(sys.argv) > 1:
        dest_dir = sys.argv[1]
        
    create_clean_project(dest_dir)