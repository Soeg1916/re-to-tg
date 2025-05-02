#!/usr/bin/env python3
"""
IMPORTANT: This script DIRECTLY executes the bot without any main.py logic.
This ensures we completely bypass any workflow detection issues.
"""
import os
import sys
import time
import logging
import signal
from datetime import datetime
import telegram
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("miku_bot")

# Check required environment variables - support multiple token variable names
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("BOT_TOKEN")
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL")

# Messaging when token is missing
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN or BOT_TOKEN is missing! Set it in your environment variables.")
    sys.exit(1)

if not TARGET_CHANNEL:
    logger.error("TARGET_CHANNEL is missing! Set it in your environment variables.")
    sys.exit(1)

# Import our modules only after verifying required env vars
try:
    from scheduler import setup_scheduler, post_miku_fact, post_miku_image, post_reddit_miku
    from facts import get_random_miku_fact
    from api_clients import get_random_miku_image
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)

# Signal handling
def signal_handler(sig, frame):
    logger.info("Received shutdown signal, cleaning up...")
    # Clean up any temp files
    cleanup()
    sys.exit(0)

# Clean up function
def cleanup():
    try:
        # Create a marker file to indicate the bot was closed properly
        with open("/tmp/bot_stopped.txt", "w") as f:
            f.write(f"Bot was stopped at {datetime.now().isoformat()}")
        
        # Remove the running indicator file
        if os.path.exists("/tmp/bot_running.txt"):
            os.remove("/tmp/bot_running.txt")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Command handlers
def start_command(update, context):
    """
    Handle the /start command.
    Sends a welcome message and instructions to the user.
    """
    user_id = update.effective_user.id
    username = update.effective_user.username or "there"
    
    welcome_message = (
        f"Hello {username}! 👋\n\n"
        f"I'm Miku Bot, dedicated to sharing content about Nakano Miku from The Quintessential Quintuplets. "
        f"I post Miku facts, images, and content from Reddit automatically.\n\n"
        f"Commands:\n"
        f"/start - Show this welcome message\n"
        f"/status - Check my current status\n"
        f"/fact - Get a random Miku fact\n"
        f"/image - Get a random Miku image\n"
        f"/admin - Show admin commands (for channel admins)\n\n"
        f"I'll be posting content to {TARGET_CHANNEL} on a regular schedule! 📅"
    )
    
    context.bot.send_message(chat_id=user_id, text=welcome_message)
    logger.info(f"Sent welcome message to user {user_id}")

def status_command(update, context):
    """
    Handle the /status command.
    Sends information about the bot's status.
    """
    user_id = update.effective_user.id
    
    uptime = time.time() - start_time
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    from config import MAIN_POST_INTERVAL, IMAGE_POST_INTERVAL, REDDIT_POST_INTERVAL
    
    status_message = (
        f"🤖 Miku Bot Status 🤖\n\n"
        f"✅ Bot is running\n"
        f"⏱️ Uptime: {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
        f"📊 Target channel: {TARGET_CHANNEL}\n"
        f"🔄 Posting schedule active\n"
        f"- Miku facts: Every {MAIN_POST_INTERVAL // 60} minutes\n"
        f"- Miku images: Every {IMAGE_POST_INTERVAL // 60} minutes\n"
        f"- Reddit content: Every {REDDIT_POST_INTERVAL // 60} minutes with no repetitions\n\n"
        f"Bot version: 1.0.2"
    )
    
    context.bot.send_message(chat_id=user_id, text=status_message)
    logger.info(f"Sent status message to user {user_id}")

def fact_command(update, context):
    """
    Handle the /fact command.
    Sends a random Miku fact to the user.
    """
    user_id = update.effective_user.id
    
    fact = get_random_miku_fact()
    context.bot.send_message(chat_id=user_id, text=f"Miku Fact: {fact}")
    logger.info(f"Sent Miku fact to user {user_id}")

def image_command(update, context):
    """
    Handle the /image command.
    Sends a random Miku image to the user.
    """
    user_id = update.effective_user.id
    
    try:
        image_data = get_random_miku_image()
        image_url = image_data.get('image_url')
        source = image_data.get('source', 'Unknown')
        
        if image_url:
            caption = f"Miku Nakano\nSource: {source}"
            context.bot.send_photo(chat_id=user_id, photo=image_url, caption=caption)
            logger.info(f"Sent Miku image to user {user_id}")
        else:
            context.bot.send_message(chat_id=user_id, text="Sorry, I couldn't find a Miku image right now. Please try again later!")
            logger.warning(f"Failed to get image URL for user {user_id}")
    
    except Exception as e:
        logger.error(f"Error sending image to user {user_id}: {e}")
        context.bot.send_message(chat_id=user_id, text="Sorry, something went wrong while getting a Miku image. Please try again later!")

def admin_command(update, context):
    """
    Handle the /admin command.
    Shows admin commands to authorized users.
    """
    user_id = update.effective_user.id
    
    if not is_admin(update, context):
        context.bot.send_message(chat_id=user_id, text="⛔ This command is only available to admins.")
        return
    
    admin_message = (
        "👑 *Admin Commands* 👑\n\n"
        "The following commands are available for admins:\n\n"
        "/addsubreddit [subreddit] - Add a subreddit to monitor\n"
        "/removesubreddit [subreddit] - Remove a subreddit from monitoring\n"
        "/setinterval [type] [minutes] - Set posting interval\n"
        "  Types: fact, image, reddit\n"
        "/setchannel [@channel] - Set target channel\n"
        "/forcepost [type] - Force an immediate post\n"
        "  Types: fact, image, reddit\n\n"
        "Example usage:\n"
        "/addsubreddit MikuNakano\n"
        "/setinterval reddit 5\n"
        "/setchannel @my_miku_channel"
    )
    
    context.bot.send_message(chat_id=user_id, text=admin_message, parse_mode='Markdown')
    logger.info(f"Sent admin commands to user {user_id}")

def is_admin(update, context):
    """Check if the user is an admin"""
    # Admin user IDs (add your own admin IDs here)
    admin_ids = [1159603709]  # Default admin ID
    
    # Get user ID
    user_id = update.effective_user.id
    
    # Direct admin check
    if user_id in admin_ids:
        return True
    
    # If not in admin list, try to check if they're a channel admin
    try:
        from config import TARGET_CHANNEL
        chat_id = TARGET_CHANNEL
        
        # Add @ prefix if missing
        if not chat_id.startswith('@'):
            chat_id = f"@{chat_id}"
            
        # Get chat member info to check if admin
        chat_member = context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        
        # Check if admin or creator
        return chat_member.status in ['administrator', 'creator']
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        return False

def add_subreddit_command(update, context):
    """
    Handle the /addsubreddit command.
    Adds a subreddit to the monitoring list.
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(update, context):
        context.bot.send_message(chat_id=user_id, text="⛔ This command is only available to admins.")
        return
    
    # Check if a subreddit name was provided
    if len(context.args) == 0:
        context.bot.send_message(chat_id=user_id, text="Please specify a subreddit name: /addsubreddit [subreddit]")
        return
    
    subreddit = context.args[0].strip()
    
    # Remove "r/" prefix if provided
    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]
    
    # Load current subreddits
    import json
    import os
    from config import SUBREDDITS
    
    # Create config file if it doesn't exist
    config_file = 'bot_config.json'
    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump({
                "subreddits": SUBREDDITS,
                "intervals": {
                    "fact": 600,  # 10 minutes
                    "image": 1200,  # 20 minutes
                    "reddit": 180   # 3 minutes
                },
                "target_channel": TARGET_CHANNEL
            }, f, indent=2)
    
    # Load current config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Check if subreddit is already in the list
    subreddits = config.get("subreddits", [])
    if subreddit in subreddits:
        context.bot.send_message(chat_id=user_id, text=f"Subreddit r/{subreddit} is already being monitored.")
        return
    
    # Add the subreddit
    subreddits.append(subreddit)
    config["subreddits"] = subreddits
    
    # Save the updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Log and inform
    logger.info(f"Added subreddit r/{subreddit} to monitoring list")
    context.bot.send_message(
        chat_id=user_id, 
        text=f"✅ Added r/{subreddit} to monitored subreddits. Will take effect on next bot restart."
    )

def remove_subreddit_command(update, context):
    """
    Handle the /removesubreddit command.
    Removes a subreddit from the monitoring list.
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(update, context):
        context.bot.send_message(chat_id=user_id, text="⛔ This command is only available to admins.")
        return
    
    # Check if a subreddit name was provided
    if len(context.args) == 0:
        context.bot.send_message(chat_id=user_id, text="Please specify a subreddit name: /removesubreddit [subreddit]")
        return
    
    subreddit = context.args[0].strip()
    
    # Remove "r/" prefix if provided
    if subreddit.startswith('r/'):
        subreddit = subreddit[2:]
    
    # Load current config
    import json
    import os
    config_file = 'bot_config.json'
    
    # If config doesn't exist yet, we can't remove anything
    if not os.path.exists(config_file):
        from config import SUBREDDITS
        if subreddit in SUBREDDITS:
            with open(config_file, 'w') as f:
                json.dump({
                    "subreddits": [s for s in SUBREDDITS if s != subreddit],
                    "intervals": {
                        "fact": 600,
                        "image": 1200,
                        "reddit": 180
                    },
                    "target_channel": TARGET_CHANNEL
                }, f, indent=2)
            context.bot.send_message(
                chat_id=user_id,
                text=f"✅ Removed r/{subreddit} from monitored subreddits. Will take effect on next bot restart."
            )
        else:
            context.bot.send_message(
                chat_id=user_id,
                text=f"❌ Subreddit r/{subreddit} is not currently being monitored."
            )
        return
    
    # Load current config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Check if subreddit is in the list
    subreddits = config.get("subreddits", [])
    if subreddit not in subreddits:
        context.bot.send_message(
            chat_id=user_id,
            text=f"❌ Subreddit r/{subreddit} is not currently being monitored."
        )
        return
    
    # Remove the subreddit
    subreddits.remove(subreddit)
    config["subreddits"] = subreddits
    
    # Save the updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Log and inform
    logger.info(f"Removed subreddit r/{subreddit} from monitoring list")
    context.bot.send_message(
        chat_id=user_id, 
        text=f"✅ Removed r/{subreddit} from monitored subreddits. Will take effect on next bot restart."
    )

def set_interval_command(update, context):
    """
    Handle the /setinterval command.
    Sets posting intervals for the bot.
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(update, context):
        context.bot.send_message(chat_id=user_id, text="⛔ This command is only available to admins.")
        return
    
    # Check arguments
    if len(context.args) < 2:
        context.bot.send_message(
            chat_id=user_id, 
            text="Please specify the type and minutes: /setinterval [fact|image|reddit] [minutes]"
        )
        return
    
    # Parse arguments
    interval_type = context.args[0].lower()
    if interval_type not in ['fact', 'image', 'reddit']:
        context.bot.send_message(
            chat_id=user_id,
            text="Invalid interval type. Use 'fact', 'image', or 'reddit'."
        )
        return
    
    try:
        minutes = int(context.args[1])
        if minutes < 1:
            context.bot.send_message(
                chat_id=user_id,
                text="Interval must be at least 1 minute."
            )
            return
    except ValueError:
        context.bot.send_message(
            chat_id=user_id,
            text="Minutes must be a number."
        )
        return
    
    # Load or create config
    import json
    import os
    config_file = 'bot_config.json'
    
    if not os.path.exists(config_file):
        from config import SUBREDDITS, MAIN_POST_INTERVAL, IMAGE_POST_INTERVAL, REDDIT_POST_INTERVAL
        with open(config_file, 'w') as f:
            json.dump({
                "subreddits": SUBREDDITS,
                "intervals": {
                    "fact": MAIN_POST_INTERVAL,
                    "image": IMAGE_POST_INTERVAL,
                    "reddit": REDDIT_POST_INTERVAL
                },
                "target_channel": TARGET_CHANNEL
            }, f, indent=2)
    
    # Load current config
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    # Update interval
    config["intervals"][interval_type] = minutes * 60  # Convert to seconds
    
    # Save updated config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Log and inform
    logger.info(f"Updated {interval_type} posting interval to {minutes} minutes")
    context.bot.send_message(
        chat_id=user_id,
        text=f"✅ Set {interval_type} posting interval to {minutes} minutes. Will take effect on next bot restart."
    )

def set_channel_command(update, context):
    """
    Handle the /setchannel command.
    Sets the target channel for posting.
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(update, context):
        context.bot.send_message(chat_id=user_id, text="⛔ This command is only available to admins.")
        return
    
    # Check if a channel was provided
    if len(context.args) == 0:
        context.bot.send_message(chat_id=user_id, text="Please specify a channel: /setchannel [@channel]")
        return
    
    # Get channel name
    channel = context.args[0].strip()
    
    # Ensure channel starts with @
    if not channel.startswith('@'):
        channel = f"@{channel}"
    
    # Load or create config
    import json
    import os
    config_file = 'bot_config.json'
    
    if not os.path.exists(config_file):
        from config import SUBREDDITS, MAIN_POST_INTERVAL, IMAGE_POST_INTERVAL, REDDIT_POST_INTERVAL
        with open(config_file, 'w') as f:
            json.dump({
                "subreddits": SUBREDDITS,
                "intervals": {
                    "fact": MAIN_POST_INTERVAL,
                    "image": IMAGE_POST_INTERVAL,
                    "reddit": REDDIT_POST_INTERVAL
                },
                "target_channel": channel
            }, f, indent=2)
    else:
        # Load current config
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        # Update channel
        config["target_channel"] = channel
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    # Log and inform
    logger.info(f"Set target channel to {channel}")
    context.bot.send_message(
        chat_id=user_id,
        text=f"✅ Set target channel to {channel}. Will take effect on next bot restart."
    )

def force_post_command(update, context):
    """
    Handle the /forcepost command.
    Forces an immediate post of the specified type.
    """
    user_id = update.effective_user.id
    
    # Check if user is admin
    if not is_admin(update, context):
        context.bot.send_message(chat_id=user_id, text="⛔ This command is only available to admins.")
        return
    
    # Check if a post type was provided
    if len(context.args) == 0:
        context.bot.send_message(chat_id=user_id, text="Please specify a post type: /forcepost [fact|image|reddit]")
        return
    
    # Get post type
    post_type = context.args[0].lower().strip()
    
    # Validate post type
    if post_type not in ['fact', 'image', 'reddit']:
        context.bot.send_message(chat_id=user_id, text="Invalid post type. Use 'fact', 'image', or 'reddit'.")
        return
    
    # Send the requested post
    try:
        if post_type == 'fact':
            post_miku_fact(context)
            context.bot.send_message(chat_id=user_id, text="✅ Sent a Miku fact to the channel.")
        elif post_type == 'image':
            post_miku_image(context)
            context.bot.send_message(chat_id=user_id, text="✅ Sent a Miku image to the channel.")
        elif post_type == 'reddit':
            post_reddit_miku(context)
            context.bot.send_message(chat_id=user_id, text="✅ Sent Reddit content to the channel.")
    except Exception as e:
        logger.error(f"Error in force post command: {e}")
        context.bot.send_message(chat_id=user_id, text=f"❌ Error sending post: {str(e)}")

def test_command(update, context):
    """
    Handle the /test command.
    This is a developer-only command to test posting functionality.
    """
    user_id = update.effective_user.id
    
    # Only allow from the bot owner or admins
    # In a production environment, you'd want to check against a list of admin IDs
    if not is_admin(update, context):
        context.bot.send_message(chat_id=user_id, text="⛔ This command is only available to admins.")
        return
    
    try:
        # Create a simple test post
        post_miku_fact(context)
        context.bot.send_message(chat_id=user_id, text="Test fact post sent!")
    except Exception as e:
        logger.error(f"Error in test command: {e}")
        context.bot.send_message(chat_id=user_id, text=f"Test failed: {str(e)}")

def setup_and_run_bot():
    """
    Set up and run the Telegram bot.
    """
    global start_time
    start_time = time.time()
    
    try:
        # Create a file to indicate the bot is running
        with open("/tmp/bot_running.txt", "w") as f:
            f.write(str(int(start_time)))
        
        # Set up the bot
        updater = Updater(token=BOT_TOKEN)
        dispatcher = updater.dispatcher
        
        # Register command handlers
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("status", status_command))
        dispatcher.add_handler(CommandHandler("fact", fact_command))
        dispatcher.add_handler(CommandHandler("image", image_command))
        dispatcher.add_handler(CommandHandler("test", test_command))
        
        # Register admin commands
        dispatcher.add_handler(CommandHandler("admin", admin_command))
        dispatcher.add_handler(CommandHandler("addsubreddit", add_subreddit_command))
        dispatcher.add_handler(CommandHandler("removesubreddit", remove_subreddit_command))
        dispatcher.add_handler(CommandHandler("setinterval", set_interval_command))
        dispatcher.add_handler(CommandHandler("setchannel", set_channel_command))
        dispatcher.add_handler(CommandHandler("forcepost", force_post_command))
        
        # Set up the job scheduler
        setup_scheduler(updater)
        
        # Start the bot
        updater.start_polling()
        logger.info("Bot started and polling for updates...")
        
        # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
        updater.idle()
    
    except telegram.error.InvalidToken:
        logger.error("Invalid bot token! Please check your TELEGRAM_BOT_TOKEN environment variable.")
        with open("/tmp/bot_failed.txt", "w") as f:
            f.write("Invalid bot token")
    
    except telegram.error.NetworkError as e:
        logger.error(f"Network error: {e}")
        with open("/tmp/bot_failed.txt", "w") as f:
            f.write(f"Network error: {e}")
    
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        with open("/tmp/bot_failed.txt", "w") as f:
            f.write(f"Error: {e}")
    
    finally:
        cleanup()

if __name__ == "__main__":
    print("=" * 50)
    print("DIRECT MIKU BOT EXECUTION - BYPASSING MAIN.PY")
    print("This script directly runs the Telegram bot")
    print("=" * 50)
    setup_and_run_bot()