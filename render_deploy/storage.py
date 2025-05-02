import json
import os
import logging
from config import HISTORY_FILE

logger = logging.getLogger(__name__)

def load_post_history():
    """
    Load the post history from a JSON file.
    
    Returns:
        dict: The post history or an empty dict if the file doesn't exist
    """
    if not os.path.exists(HISTORY_FILE):
        return {"urls": [], "facts": []}
    
    try:
        with open(HISTORY_FILE, 'r') as file:
            history = json.load(file)
            return history
    except Exception as e:
        logger.error(f"Error loading post history: {e}")
        return {"urls": [], "facts": []}

def save_post_history(history):
    """
    Save the post history to a JSON file.
    
    Args:
        history (dict): The post history to save
    """
    try:
        with open(HISTORY_FILE, 'w') as file:
            json.dump(history, file)
    except Exception as e:
        logger.error(f"Error saving post history: {e}")

def add_to_history(item_type, item_content):
    """
    Add an item to the post history.
    
    Args:
        item_type (str): The type of item ('urls' or 'facts')
        item_content (str): The content to add
    """
    history = load_post_history()
    
    # Ensure the type exists in history
    if item_type not in history:
        history[item_type] = []
    
    # Add the item if it's not already there
    if item_content not in history[item_type]:
        history[item_type].append(item_content)
        
        # Limit the history size to prevent unlimited growth
        max_history = 500
        if len(history[item_type]) > max_history:
            history[item_type] = history[item_type][-max_history:]
        
        save_post_history(history)

def is_in_history(item_type, item_content):
    """
    Check if an item is in the post history.
    
    Args:
        item_type (str): The type of item ('urls' or 'facts')
        item_content (str): The content to check
        
    Returns:
        bool: True if the item is in the history, False otherwise
    """
    history = load_post_history()
    return item_type in history and item_content in history[item_type]
