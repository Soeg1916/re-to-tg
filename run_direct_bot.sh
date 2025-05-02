#!/bin/bash
# Special shell script to ensure the bot runs directly without any Flask dependencies
# This script should be used by the run_miku_bot workflow

# Exit on any error
set -e

echo "=================================================="
echo "DIRECT BOT EXECUTION"
echo "This script completely bypasses main.py"
echo "=================================================="

# Clean up any previous lock files
rm -f /tmp/bot_running.txt /tmp/bot_failed.txt

# Run the completely standalone bot script
exec python direct_miku_bot.py