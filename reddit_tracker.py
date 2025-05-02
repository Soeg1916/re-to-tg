"""
Reddit post tracker and batch posting functionality.
Detects new posts from Miku-related subreddits and manages batched posting.
"""
import logging
import time
from datetime import datetime
from api_clients import reddit_client, MIKU_SUBREDDITS
from storage import load_post_history, add_to_history, is_in_history

logger = logging.getLogger(__name__)

# Dictionary to store the latest post ID for each subreddit
last_post_ids = {}

# Dictionary to store tracked posts
tracked_posts = {}

# How far back to look when searching for new posts (seconds)
NEW_POST_LOOKBACK = 3600  # 1 hour

def initialize_last_post_ids():
    """Initialize last post IDs for all monitored subreddits"""
    global last_post_ids
    
    if not reddit_client:
        logger.warning("Reddit client not initialized. Can't track post IDs.")
        return
    
    try:
        for subreddit_name in MIKU_SUBREDDITS:
            try:
                subreddit = reddit_client.subreddit(subreddit_name)
                # Get most recent post to establish baseline
                for post in subreddit.new(limit=1):
                    last_post_ids[subreddit_name] = post.id
                    logger.info(f"Initialized tracking for r/{subreddit_name} with post ID: {post.id}")
                    break
            except Exception as e:
                if "404" in str(e):
                    logger.error(f"Error initializing tracking for r/{subreddit_name}: received 404 HTTP response")
                    # Mark this subreddit as inactive but don't fail
                    last_post_ids[subreddit_name] = None
                else:
                    logger.error(f"Error initializing tracking for r/{subreddit_name}: {e}")
    except Exception as e:
        logger.error(f"Error in initialize_last_post_ids: {e}")

def is_miku_post(post, subreddit_name):
    """
    Check if a post is Miku-related based on content and subreddit.
    
    Args:
        post: Reddit post object
        subreddit_name: Name of the subreddit
        
    Returns:
        bool: True if the post is Miku-related
    """
    # Check if it's an image post
    is_image = (hasattr(post, 'url') and
              any(post.url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']))
    
    if not is_image:
        return False
    
    # For Miku-specific subreddits, all posts are considered Miku-related
    if subreddit_name in ['MikuNakano', 'Nakano_Miku', 'churchofmiku']:
        return True
    
    # For other subreddits, check if the title contains Miku-related keywords
    has_miku_reference = False
    if hasattr(post, 'title'):
        title_lower = post.title.lower()
        has_miku_reference = ('miku' in title_lower or 
                             'nakano' in title_lower or
                             'third sister' in title_lower or
                             'headphones' in title_lower)
    
    return has_miku_reference

def check_for_new_posts():
    """
    Check all monitored subreddits for new posts.
    
    Returns:
        list: List of new posts formatted for immediate posting
    """
    global last_post_ids, tracked_posts
    
    if not reddit_client:
        logger.warning("Reddit client not initialized. Can't check for new posts.")
        return []
    
    new_posts = []
    
    try:
        for subreddit_name in MIKU_SUBREDDITS:
            try:
                # Skip if we haven't initialized tracking for this subreddit
                if subreddit_name not in last_post_ids:
                    continue
                
                subreddit = reddit_client.subreddit(subreddit_name)
                
                # Get new posts from the subreddit
                latest_posts = []
                for post in subreddit.new(limit=10):
                    # If we've seen this post before, we don't need to check older posts
                    if post.id == last_post_ids.get(subreddit_name):
                        break
                    
                    # Check if this post is newer than our cutoff time
                    post_time = datetime.fromtimestamp(post.created_utc)
                    current_time = datetime.now()
                    time_diff = (current_time - post_time).total_seconds()
                    
                    if time_diff > NEW_POST_LOOKBACK:
                        # Skip posts older than our lookback period
                        continue
                    
                    latest_posts.append(post)
                
                # Process posts in chronological order (oldest first)
                latest_posts.reverse()
                
                # Update the last seen post ID if we found new posts
                if latest_posts:
                    last_post_ids[subreddit_name] = latest_posts[-1].id
                
                # Add Miku-related posts to the result list
                for post in latest_posts:
                    if is_miku_post(post, subreddit_name):
                        # Format the post for sending
                        post_data = {
                            "image_url": post.url,
                            "caption": post.title,
                            "source": f"Reddit r/{subreddit_name} - u/{post.author.name}",
                            "id": post.id,
                            "permalink": post.permalink
                        }
                        
                        # Check if we've already posted this URL
                        if not is_in_history("urls", post.url):
                            new_posts.append(post_data)
                            # Add to tracked posts for potential batch posting
                            tracked_posts[post.id] = post_data
                            logger.info(f"New Miku post detected: {post.title[:30]}... in r/{subreddit_name}")
                
            except Exception as e:
                logger.error(f"Error checking r/{subreddit_name} for new posts: {e}")
    except Exception as e:
        logger.error(f"Error in check_for_new_posts: {e}")
    
    return new_posts

def get_batch_posts(max_posts=5):
    """
    Get a batch of unposted Miku content from all subreddits.
    
    Args:
        max_posts: Maximum number of posts to return
        
    Returns:
        list: List of post data dictionaries
    """
    if not reddit_client:
        logger.warning("Reddit client not initialized. Can't get batch posts.")
        return []
    
    batch_posts = []
    posts_added = 0
    
    try:
        # First check for any new posts we're tracking
        for post_id, post_data in list(tracked_posts.items()):
            if not is_in_history("urls", post_data["image_url"]):
                batch_posts.append(post_data)
                posts_added += 1
                
                # Remove from tracked posts so we don't check it again
                # (it will be added to history after posting)
                del tracked_posts[post_id]
                
                if posts_added >= max_posts:
                    return batch_posts
        
        # If we still need more posts, check all subreddits for more content
        for subreddit_name in MIKU_SUBREDDITS:
            if posts_added >= max_posts:
                break
                
            try:
                subreddit = reddit_client.subreddit(subreddit_name)
                
                # Try hot posts first
                for post in subreddit.hot(limit=25):
                    if is_miku_post(post, subreddit_name) and not is_in_history("urls", post.url):
                        post_data = {
                            "image_url": post.url,
                            "caption": post.title,
                            "source": f"Reddit r/{subreddit_name} - u/{post.author.name}",
                            "id": post.id,
                            "permalink": post.permalink
                        }
                        batch_posts.append(post_data)
                        posts_added += 1
                        
                        if posts_added >= max_posts:
                            break
                
                # If we still need more, try top posts
                if posts_added < max_posts:
                    for post in subreddit.top(time_filter="week", limit=25):
                        if is_miku_post(post, subreddit_name) and not is_in_history("urls", post.url):
                            post_data = {
                                "image_url": post.url,
                                "caption": post.title,
                                "source": f"Reddit r/{subreddit_name} - u/{post.author.name}",
                                "id": post.id,
                                "permalink": post.permalink
                            }
                            batch_posts.append(post_data)
                            posts_added += 1
                            
                            if posts_added >= max_posts:
                                break
                
            except Exception as e:
                if "404" in str(e):
                    logger.error(f"Error getting batch posts from r/{subreddit_name}: received 404 HTTP response")
                else:
                    logger.error(f"Error getting batch posts from r/{subreddit_name}: {e}")
                
    except Exception as e:
        logger.error(f"Error in get_batch_posts: {e}")
    
    return batch_posts

# Initialize tracking when module is loaded
initialize_last_post_ids()