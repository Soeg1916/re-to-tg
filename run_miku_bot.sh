#!/bin/bash
# Shell script to run the Miku bot directly, bypassing main.py completely
# This is designed to be used by the run_miku_bot workflow

echo "==============================================="
echo "✅ MIKU BOT DIRECT EXECUTION SHELL SCRIPT"
echo "This script completely bypasses main.py"
echo "==============================================="

# Remove any lock files
for file in /tmp/bot_running.txt /tmp/web_interface_running.txt /tmp/bot_failed.txt
do
  if [ -f "$file" ]; then
    echo "Removing lock file: $file"
    rm "$file"
  fi
done

# Directly execute our bot-only script
python main_run_bot.py