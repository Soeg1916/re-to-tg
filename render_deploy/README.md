# Miku Bot

A Telegram bot that automatically shares content about Nakano Miku from various sources including Reddit, anime image APIs, and more.

## Features

- Posts Miku facts on a regular schedule
- Shares Miku images from multiple sources
- Monitors Reddit for new Miku content
- Provides a web dashboard to monitor bot status
- Includes admin commands for channel management

## Deployment on Render

### Prerequisites

1. Telegram Bot Token (from @BotFather)
2. Reddit API credentials (optional, for Reddit functionality)
3. Target Telegram channel where the bot will post content

### Environment Variables

Set the following environment variables in your Render dashboard:

- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `TARGET_CHANNEL`: Your target Telegram channel (e.g., @YourChannel)
- `REDDIT_CLIENT_ID`: Your Reddit application client ID (optional)
- `REDDIT_CLIENT_SECRET`: Your Reddit application client secret (optional)

### Deployment Steps

1. Fork or clone this repository
2. Create a new Web Service on Render
3. Connect your GitHub repository
4. Set the build command: `pip install -r requirements.txt`
5. Set the start command: `gunicorn --bind 0.0.0.0:$PORT main:app`
6. Add the required environment variables
7. Deploy the service

### Running Both Bot and Web Interface

The Procfile includes configurations for both:
- `web`: Runs the web dashboard on the specified port
- `bot`: Runs the standalone bot

On Render, you can create a second service for the bot with the start command:
`python run_miku_bot_standalone.py`

## Local Development

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (create a `.env` file)
4. Run the bot: `python run_miku_bot_standalone.py`
5. Run the web interface: `python -m flask run`

## Project Structure

- `api_clients.py`: API client implementations
- `config.py`: Configuration settings
- `facts.py`: Miku facts database
- `handlers.py`: Telegram message handlers
- `reddit_tracker.py`: Reddit tracking functionality  
- `scheduler.py`: Scheduling system
- `storage.py`: Data storage utilities
- `bot.py`: Main bot implementation
- `main.py`: Entry point
- `app_simple.py`: Web interface for dashboard

## License

MIT License