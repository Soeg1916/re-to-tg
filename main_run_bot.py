#!/usr/bin/env python3
"""
A completely standalone script for the run_miku_bot workflow.
This script runs the bot without any web interface or Flask dependencies.
"""

import os
import sys
import time
import signal
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("main_run_bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("main_run_bot")

def start_command(update, context):
    """
    Handle the /start command.
    Sends a welcome message and instructions to the user.
    """
    message = (
        "👋 Hello! I'm Miku Bot, dedicated to sharing Nakano Miku content.\n\n"
        "🤖 Commands:\n"
        "/start - Show this help message\n"
        "/status - Check bot status\n"
        "/fact - Get a random Miku fact\n"
        "/image - Get a random Miku image\n\n"
        "I also automatically post Miku content to the configured channel!"
    )
    update.message.reply_text(message)
    logger.info(f"Sent welcome message to user {update.effective_user.id}")

def status_command(update, context):
    """
    Handle the /status command.
    Sends information about the bot's status.
    """
    from config import DEFAULT_CHANNEL, MAIN_POST_INTERVAL, IMAGE_POST_INTERVAL, REDDIT_POST_INTERVAL
    
    channel = DEFAULT_CHANNEL
    if channel and not channel.startswith('@'):
        channel = '@' + channel
    
    message = (
        "📊 Miku Bot Status:\n"
        f"🤖 Version: 1.0.1\n"
        f"📢 Target Channel: {channel}\n"
        f"⏱️ Post Intervals:\n"
        f"  - Facts: Every {MAIN_POST_INTERVAL // 60} minutes\n"
        f"  - Images: Every {IMAGE_POST_INTERVAL // 60} minutes\n"
        f"  - Reddit: Every {REDDIT_POST_INTERVAL // 60} minutes\n"
        f"📱 Reddit tracking: {'Enabled' if os.getenv('REDDIT_CLIENT_ID') else 'Disabled'}\n"
        f"🔄 Uptime: Running in standalone mode\n"
    )
    update.message.reply_text(message)
    logger.info(f"Sent status to user {update.effective_user.id}")

def setup_and_run_bot():
    """
    Set up and run the Telegram bot.
    """
    # Import here to avoid circular imports
    import telegram
    from telegram.ext import Updater, CommandHandler
    
    # Get bot token from environment
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment. Please set this variable.")
        sys.exit(1)
    
    try:
        # Create the Updater and dispatcher
        updater = Updater(token=bot_token, use_context=True)
        dispatcher = updater.dispatcher
        
        # Register command handlers
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("status", status_command))
        
        # Import and register other command handlers
        from direct_miku_bot import fact_command, image_command, test_command
        dispatcher.add_handler(CommandHandler("fact", fact_command))
        dispatcher.add_handler(CommandHandler("image", image_command))
        dispatcher.add_handler(CommandHandler("test", test_command))
        
        # Set up the scheduler
        from scheduler import setup_scheduler
        job_queue = updater.job_queue
        setup_scheduler(job_queue)
        
        # Start the Bot
        updater.start_polling()
        logger.info("Bot started and polling for updates...")
        
        # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT
        updater.idle()
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Set marker
    with open(".run_miku_bot", "w") as f:
        f.write("1")
    
    # First kill any competing processes to avoid conflicts
    subprocess.run("pkill -f 'python.*flask'", shell=True)
    subprocess.run("pkill -f 'python.*5000'", shell=True)
    time.sleep(1)
    
    # Create a marker file to indicate the bot is running
    with open("/tmp/bot_running.txt", "w") as f:
        f.write("1")
    
    # Run the bot
    setup_and_run_bot()