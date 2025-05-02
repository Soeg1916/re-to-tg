#!/usr/bin/env python3
"""
100% STANDALONE BOT SCRIPT - NO FLASK IMPORTS WHATSOEVER
This script is designed to be run directly with no dependencies on Flask or web interfaces.
"""
import os
import time
import logging
import traceback
from telegram.ext import Updater, CommandHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def start_command(update, context):
    """
    Handle the /start command.
    Sends a welcome message and instructions to the user.
    """
    logger.info(f"User {update.effective_user.id} started the bot")
    update.message.reply_text(
        "👋 Hello! I'm the Nakano Miku Bot. I will regularly post Miku content to "
        "the configured channel. Use /status to check my current status."
    )

def status_command(update, context):
    """
    Handle the /status command.
    Sends information about the bot's status.
    """
    channel = os.getenv("TELEGRAM_CHANNEL_USERNAME", "Not configured")
    if channel and not channel.startswith('@'):
        channel = '@' + channel
        
    update.message.reply_text(
        f"✅ *Nakano Miku Bot Status*\n\n"
        f"• *Target channel:* {channel}\n"
        f"• *Post frequency:*\n"
        f"  - Image posts: Every 10 minutes\n"
        f"  - Reddit posts: Every 2 minutes\n"
        f"• *Version:* 1.1.0\n"
        f"• *Uptime:* Running since {time.strftime('%Y-%m-%d %H:%M:%S')}\n",
        parse_mode="Markdown"
    )

def setup_and_run_bot():
    """
    Set up and run the Telegram bot.
    """
    # Write a file to indicate the bot is running
    with open('/tmp/bot_running.txt', 'w') as f:
        f.write('1')
    
    logger.info("Starting the Miku bot...")
    
    # Create the Updater and pass it the bot's token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        with open('/tmp/bot_failed.txt', 'w') as f:
            f.write("TELEGRAM_BOT_TOKEN not found in environment variables")
        return

    try:
        updater = Updater(token)
        
        # Get the dispatcher to register handlers
        dispatcher = updater.dispatcher
        
        # Register command handlers
        dispatcher.add_handler(CommandHandler("start", start_command))
        dispatcher.add_handler(CommandHandler("status", status_command))
        
        # Set up the scheduler for regular posts
        from scheduler import setup_scheduler
        setup_scheduler(updater)
        
        # Start the Bot
        updater.start_polling()
        logger.info("Bot started successfully!")
        
        # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
        updater.idle()
        
    except Exception as e:
        error_message = f"Error starting bot: {e}\n{traceback.format_exc()}"
        logger.error(error_message)
        with open('/tmp/bot_failed.txt', 'w') as f:
            f.write(error_message)

if __name__ == '__main__':
    try:
        # Remove any existing lock files
        for file_path in ['/tmp/bot_running.txt', '/tmp/bot_failed.txt']:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Print a banner to show we're using the direct script
        print("=" * 60)
        print("DIRECT BOT EXECUTION - 100% STANDALONE MODE")
        print("No web interface or Flask dependencies")
        print("=" * 60)
        
        # Start the bot
        setup_and_run_bot()
        
    except Exception as e:
        error_message = f"Critical error in direct_bot_only.py: {e}\n{traceback.format_exc()}"
        print(error_message)
        with open('/tmp/bot_failed.txt', 'w') as f:
            f.write(error_message)