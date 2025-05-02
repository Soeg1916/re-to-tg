import os
import logging
from telegram.ext import Updater, CommandHandler

logger = logging.getLogger(__name__)

# Global variables to be accessible from other parts of the application
bot_updater = None
bot_instance = None

def start_command(update, context):
    """
    Handle the /start command.
    Sends a welcome message and instructions to the user.
    """
    update.message.reply_text(
        "Hello! I'm the Nakano Miku Bot! 💙\n\n"
        "I'll be posting Miku content regularly in this chat.\n"
        "Facts and images every 30 minutes, and extra images every 15 minutes!\n\n"
        "Just sit back and enjoy the Miku content! 🎧"
    )

def get_bot():
    """
    Return the bot instance for use in other parts of the application
    """
    global bot_updater, bot_instance
    
    # First, try to return the direct bot instance if available
    if bot_instance:
        return bot_instance
    
    # Otherwise, try to get it from the updater
    if bot_updater and hasattr(bot_updater, 'bot'):
        bot_instance = bot_updater.bot
        return bot_instance
    
    return None

def setup_bot():
    """
    Setup and start the Telegram bot.
    """
    global bot_updater, bot_instance
    
    # Import here to avoid circular imports
    from scheduler import setup_scheduler
    
    # Get token from environment variable
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
        return

    # Create the Updater and pass it the bot's token
    updater = Updater(token=token, use_context=True)
    bot_updater = updater
    bot_instance = updater.bot  # Store direct reference to bot
    
    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("start", start_command))

    # Set up the scheduler for timed posts
    setup_scheduler(updater)

    # Start the Bot
    logger.info("Starting bot...")
    updater.start_polling()
    
    # When running in a thread, we should not call idle()
    # as it will try to set signal handlers which only work in main thread
    # updater.idle()
    
    return updater
