import logging
import random
import time
from telegram.ext import Updater
from api_clients import get_random_miku_image, fetch_reddit_post
from facts import get_random_miku_fact, get_random_miku_caption
from handlers import send_post
from storage import add_to_history, is_in_history
from config import (
    MAIN_POST_INTERVAL, IMAGE_POST_INTERVAL, REDDIT_POST_INTERVAL
)
from reddit_tracker import check_for_new_posts, get_batch_posts, initialize_last_post_ids

logger = logging.getLogger(__name__)

def post_miku_fact(context):
    """
    Scheduled job to post a Miku fact with an image.
    """
    try:
        # Get a random fact that hasn't been used recently
        fact = get_random_miku_fact()
        fact_attempts = 0
        max_attempts = 10
        
        while is_in_history("facts", fact) and fact_attempts < max_attempts:
            fact = get_random_miku_fact()
            fact_attempts += 1
        
        # Get a random image
        image_data = get_random_miku_image()
        if not image_data:
            logger.error("Failed to get a Miku image for fact post")
            return
            
        image_url = image_data["image_url"]
        
        # Check if this image URL has been used before
        image_attempts = 0
        while is_in_history("urls", image_url) and image_attempts < max_attempts:
            image_data = get_random_miku_image()
            if not image_data:
                logger.error("Failed to get a unique Miku image after multiple attempts")
                break
            image_url = image_data["image_url"]
            image_attempts += 1
            
        # Create the content package
        content = {
            "image_url": image_url,
            "caption": fact,
            "source": image_data.get("source", "")
        }
        
        # Send the post
        send_post(context, content)
        
        # Record used content in history
        add_to_history("facts", fact)
        add_to_history("urls", image_url)
        
    except Exception as e:
        logger.error(f"Error in post_miku_fact: {e}")

def post_miku_image(context):
    """
    Scheduled job to post just a Miku image with a short caption.
    """
    try:
        # Get a random caption
        caption = get_random_miku_caption()
        
        # Get a random image
        image_data = get_random_miku_image()
        if not image_data:
            logger.error("Failed to get a Miku image for image post")
            return
            
        image_url = image_data["image_url"]
        
        # Check if this image URL has been used before
        max_attempts = 10
        image_attempts = 0
        while is_in_history("urls", image_url) and image_attempts < max_attempts:
            image_data = get_random_miku_image()
            if not image_data:
                logger.error("Failed to get a unique Miku image after multiple attempts")
                break
            image_url = image_data["image_url"]
            image_attempts += 1
            
        # Create the content package
        content = {
            "image_url": image_url,
            "caption": caption,
            "source": image_data.get("source", "")
        }
        
        # Send the post
        send_post(context, content)
        
        # Record used content in history
        add_to_history("urls", image_url)
        
    except Exception as e:
        logger.error(f"Error in post_miku_image: {e}")

def post_reddit_miku(context):
    """
    Scheduled job to post Miku content from Reddit.
    Gets posts every 3 minutes with strict duplicate prevention.
    """
    try:
        # Get a batch of Reddit posts (just 1 at a time to avoid flooding)
        # We'll post more frequently (every 3 minutes) but with fewer posts each time
        batch_posts = get_batch_posts(max_posts=1)
        
        if not batch_posts:
            logger.info("No new Reddit posts to share at this time")
            return
            
        for post in batch_posts:
            # Check if this post URL has been shared before
            image_url = post.get("image_url", "")
            post_id = post.get("id", "")
            
            # Skip if we've posted this content before (double checking both URL and ID)
            if is_in_history("urls", image_url) or is_in_history("post_ids", post_id):
                logger.info(f"Skipping already shared post: {post_id}")
                continue
                
            # Send the post
            send_post(context, post)
            
            # Record used content in history with multiple identifiers
            add_to_history("urls", image_url)
            add_to_history("post_ids", post_id)
            if "caption" in post:
                add_to_history("captions", post["caption"])
            
            logger.info(f"Posted Reddit content: {post_id}")
        
    except Exception as e:
        logger.error(f"Error in post_reddit_miku: {e}")

def check_new_reddit_posts(context):
    """
    Frequently checks for new Reddit posts and posts them immediately.
    This allows us to post new content as soon as it appears.
    """
    try:
        # Check for new posts
        new_posts = check_for_new_posts()
        
        if not new_posts:
            return
        
        logger.info(f"Found {len(new_posts)} new Reddit posts to share immediately")
        
        # Only post one item at a time to avoid flooding
        posted_count = 0
        
        for post in new_posts:
            # Get key identifiers from the post
            image_url = post.get("image_url", "")
            post_id = post.get("id", "")
            
            # Skip if we've posted this content before (double checking both URL and ID)
            if is_in_history("urls", image_url) or is_in_history("post_ids", post_id):
                logger.info(f"Skipping already shared post: {post_id}")
                continue
            
            # Send the post
            send_post(context, post)
            
            # Record used content in history with multiple identifiers
            add_to_history("urls", image_url)
            add_to_history("post_ids", post_id)
            if "caption" in post:
                add_to_history("captions", post["caption"])
            
            posted_count += 1
            logger.info(f"Posted new Reddit content: {post_id}")
            
            # Only post one item per check to avoid flooding
            if posted_count >= 1:
                break
        
    except Exception as e:
        logger.error(f"Error in check_new_reddit_posts: {e}")

def setup_scheduler(updater: Updater):
    """
    Set up the scheduler for regular posts.
    
    Args:
        updater: The Telegram bot updater
    """
    job_queue = updater.job_queue
    
    # Initialize Reddit tracking
    initialize_last_post_ids()
    
    # Schedule the main posts every 30 minutes
    job_queue.run_repeating(
        post_miku_fact,
        interval=MAIN_POST_INTERVAL,
        first=5  # Start after 5 seconds
    )
    
    # Schedule image posts every 15 minutes (offset by 7.5 minutes from main posts)
    job_queue.run_repeating(
        post_miku_image,
        interval=IMAGE_POST_INTERVAL,
        first=IMAGE_POST_INTERVAL // 2  # Start halfway between main posts
    )
    
    # Schedule Reddit batch posts every 3 minutes
    job_queue.run_repeating(
        post_reddit_miku,
        interval=REDDIT_POST_INTERVAL,  # 3 minutes in seconds (from config)
        first=60  # Start after 1 minute
    )
    
    # Schedule frequent checks for new Reddit posts (every minute)
    job_queue.run_repeating(
        check_new_reddit_posts,
        interval=60,  # 1 minute in seconds
        first=30  # Start after 30 seconds
    )
    
    logger.info("Scheduler set up successfully")
