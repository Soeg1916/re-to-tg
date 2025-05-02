import logging
import requests
import random
import praw
from config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT,
    SUBREDDITS as MIKU_SUBREDDITS, WAIFU_PICS_API, ANIME_PICS_API, SAFEBOORU_API
)
import time

logger = logging.getLogger(__name__)

# Global variable for Reddit client
reddit_client = None

def initialize_reddit_client():
    """Initialize and return the Reddit client if credentials are available"""
    global reddit_client
    
    if reddit_client:
        return reddit_client  # Already initialized
        
    if REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET:
        try:
            reddit_client = praw.Reddit(
                client_id=REDDIT_CLIENT_ID,
                client_secret=REDDIT_CLIENT_SECRET,
                user_agent=REDDIT_USER_AGENT
            )
            logger.info("Reddit client initialized")
            return reddit_client
        except Exception as e:
            logger.error(f"Error initializing Reddit client: {e}")
            return None
    else:
        logger.warning("Reddit API credentials not found, Reddit features disabled")
        return None

# Initialize Reddit client on module import
initialize_reddit_client()

def fetch_image_from_waifu_pics():
    """
    Fetch an anime image from waifu.pics API.
    This is only used as a fallback since it's harder to get specific Miku images.
    
    Returns:
        dict: Contains image_url and source
    """
    try:
        # Note: waifu.pics doesn't allow specific character searches,
        # so this is only used as a last resort fallback
        response = requests.get(WAIFU_PICS_API)
        if response.status_code == 200:
            data = response.json()
            return {
                "image_url": data.get("url"),
                "source": "waifu.pics (Fallback - may not be Miku)"
            }
    except Exception as e:
        logger.error(f"Error fetching from waifu.pics: {e}")
    return None

def fetch_image_from_waifu_im():
    """
    Fetch a Nakano Miku image from waifu.im API.
    
    Returns:
        dict: Contains image_url and source
    """
    try:
        # Make sure we're specifically requesting Nakano Miku
        params = {
            "included_tags": "miku_nakano",
            "height": ">=1000",  # Better quality images
            "many": "true"       # Get multiple results to choose from
        }
        response = requests.get(ANIME_PICS_API, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'images' in data and len(data['images']) > 0:
                # Choose a random image from the results
                img = random.choice(data['images'])
                return {
                    "image_url": img.get("url"),
                    "source": f"waifu.im - {img.get('source', 'Unknown')}"
                }
    except Exception as e:
        logger.error(f"Error fetching from waifu.im: {e}")
    return None

def fetch_image_from_safebooru():
    """
    Fetch a Miku image from Safebooru.
    
    Returns:
        dict: Contains image_url and source
    """
    try:
        params = {"limit": 100}
        response = requests.get(SAFEBOORU_API, params=params)
        if response.status_code == 200:
            posts = response.json()
            if posts and len(posts) > 0:
                # Select a random post
                post = random.choice(posts)
                # Safebooru image URL format
                image_url = f"https://safebooru.org/images/{post['directory']}/{post['image']}"
                return {
                    "image_url": image_url,
                    "source": f"Safebooru - Post #{post['id']}"
                }
    except Exception as e:
        logger.error(f"Error fetching from Safebooru: {e}")
    return None

def fetch_reddit_post():
    """
    Fetch a Nakano Miku-related post from Reddit.
    
    Returns:
        dict: Contains image_url, caption, and source
    """
    if not reddit_client:
        logger.warning("Reddit client not initialized")
        return None
        
    try:
        # Pick a random Miku-related subreddit
        subreddit_name = random.choice(MIKU_SUBREDDITS)
        subreddit = reddit_client.subreddit(subreddit_name)
        
        # Get hot posts from the subreddit
        posts = list(subreddit.hot(limit=50))
        
        # Only get image posts that are related to Miku
        image_posts = []
        for post in posts:
            # Check if this is an image post
            is_image = (hasattr(post, 'url') and
                      any(post.url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']))
            
            # Check if it's specifically about Miku
            has_miku_reference = False
            if hasattr(post, 'title'):
                title_lower = post.title.lower()
                has_miku_reference = ('miku' in title_lower or 
                                     'nakano' in title_lower or
                                     'third sister' in title_lower or
                                     'headphones' in title_lower)
            
            # For the MikuNakano and Nakano_Miku subreddits, all posts are about Miku
            if subreddit_name in ['MikuNakano', 'Nakano_Miku']:
                has_miku_reference = True
                
            # Add to our list if it meets both criteria
            if is_image and has_miku_reference:
                image_posts.append(post)
        
        # If no suitable posts found, try another subreddit
        if not image_posts:
            logger.warning(f"No Miku image posts found in r/{subreddit_name}")
            return None
            
        # Pick a random image post
        post = random.choice(image_posts)
        
        return {
            "image_url": post.url,
            "caption": post.title,
            "source": f"Reddit r/{subreddit_name} - u/{post.author.name}"
        }
        
    except Exception as e:
        logger.error(f"Error fetching from Reddit: {e}")
        return None

def get_random_miku_image():
    """
    Try different sources to get a random Miku image.
    Prioritizes Miku-specific sources.
    
    Returns:
        dict: Contains image_url and source
    """
    # We now use a more sophisticated selection approach
    # that favors high-quality Miku-specific sources
    
    # Primary sources for Nakano Miku (These are the most reliable)
    primary_fetchers = [
        fetch_image_from_safebooru,  # Safebooru with nakano_miku tag
        fetch_image_from_waifu_im,   # Waifu.im with miku_nakano tag
    ]
    
    # Fallback source (less likely to be Miku, only used if all else fails)
    fallback_fetchers = [
        fetch_image_from_waifu_pics  # Generic anime images
    ]
    
    # Try the primary sources first (with randomization for variety)
    random.shuffle(primary_fetchers)
    for fetcher in primary_fetchers:
        result = fetcher()
        if result and 'image_url' in result:
            return result
    
    # If primary sources fail, try fallbacks
    for fetcher in fallback_fetchers:
        result = fetcher()
        if result and 'image_url' in result:
            logger.warning("Using fallback image source - may not be Miku")
            return result
    
    # If all fetchers fail, return a default error response
    logger.error("All image sources failed")
    return None
