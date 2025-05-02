# Deploying Miku Bot on Render

This guide walks you through deploying the Miku Bot on Render.com.

## Option 1: Manual Deployment (Web UI)

### Step 1: Create a New Web Service

1. Log in to your [Render Dashboard](https://dashboard.render.com/)
2. Click **New** and select **Web Service**
3. Connect your repository or upload this folder
4. Fill in the following settings:
   - **Name**: `miku-bot-dashboard`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`

### Step 2: Configure Environment Variables

Add the following environment variables:
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token from @BotFather
- `TARGET_CHANNEL` - Your Telegram channel name (e.g., @MikuChannel)
- `REDDIT_CLIENT_ID` - (Optional) Your Reddit API client ID
- `REDDIT_CLIENT_SECRET` - (Optional) Your Reddit API client secret

### Step 3: Deploy the Bot Worker

1. Go back to your Render Dashboard
2. Click **New** and select **Background Worker**
3. Connect to the same repository 
4. Fill in the following settings:
   - **Name**: `miku-bot-worker`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run_miku_bot_standalone.py`
5. Use the same environment variables as the web service

## Option 2: Automatic Deployment (render.yaml)

If you want to deploy both the web interface and bot worker at once:

1. Log in to your [Render Dashboard](https://dashboard.render.com/)
2. Click **New** and select **Blueprint**
3. Connect your repository that contains this `render.yaml` file
4. Render will automatically detect both services
5. Fill in the required environment variables
6. Click **Apply**

## Verifying Your Deployment

1. Once deployed, open your web service URL
2. You should see the Miku Bot Dashboard
3. The status should show "Online" once both services are running
4. Check your Telegram channel to confirm the bot is posting content

## Troubleshooting

- If the bot shows as offline, check the logs for the bot worker
- Make sure your Telegram bot token is valid and the bot has permission to post to your channel
- Ensure your bot is an admin in the target channel with post permissions
- Check if Reddit API credentials are correct (if using Reddit features)