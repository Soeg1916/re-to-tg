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

# Check required environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
TARGET_CHANNEL = os.environ.get("TARGET_CHANNEL")

# Messaging when token is missing
if not BOT_TOKEN:
    logger.error("BOT_TOKEN is missing! Set it in your environment variables.")
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
        f"/image - Get a random Miku image\n\n"
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
    
    status_message = (
        f"🤖 Miku Bot Status 🤖\n\n"
        f"✅ Bot is running\n"
        f"⏱️ Uptime: {int(hours)}h {int(minutes)}m {int(seconds)}s\n"
        f"📊 Target channel: {TARGET_CHANNEL}\n"
        f"🔄 Posting schedule active\n"
        f"- Miku facts: Every 6 hours\n"
        f"- Miku images: Every 3 hours\n"
        f"- Reddit content: Every 2 hours\n\n"
        f"Bot version: 1.0.0"
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

def test_command(update, context):
    """
    Handle the /test command.
    This is a developer-only command to test posting functionality.
    """
    user_id = update.effective_user.id
    
    # Only allow from the bot owner or admins
    # In a production environment, you'd want to check against a list of admin IDs
    
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
            f.write(f"Bot started at {datetime.now().isoformat()}")
        
        # Set up the bot
        updater = Updater(token=BOT_TOKEN)
        dispatcher = updater.dispatcher
        
        # Register command handlers
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("status", status_command))
        dispatcher.add_handler(CommandHandler("fact", fact_command))
        dispatcher.add_handler(CommandHandler("image", image_command))
        dispatcher.add_handler(CommandHandler("test", test_command))
        
        # Set up the job scheduler
        setup_scheduler(updater)
        
        # Start the bot
        updater.start_polling()
        logger.info("Bot started and polling for updates...")
        
        # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
        updater.idle()
    
    except telegram.error.InvalidToken:
        logger.error("Invalid bot token! Please check your BOT_TOKEN environment variable.")
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