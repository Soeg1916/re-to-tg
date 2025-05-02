#!/usr/bin/env python3
"""
100% STANDALONE BOT SCRIPT - NO IMPORTS FROM PROJECT FILES INITIALLY
This script directly runs the Miku Bot in the run_miku_bot workflow environment.
It handles all errors, logs properly, and restarts the bot if needed.
"""
import os
import sys
import time
import signal
import socket
import logging
import subprocess
import threading
from datetime import datetime
import http.server
import socketserver

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("standalone_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("standalone_bot")

# Constants
PORT = 8080  # Use a different port to avoid conflicts
BOT_SCRIPT = "direct_miku_bot.py"  # Script to actually run the bot
PID_FILE = "/tmp/miku_bot.pid"
RUNNING_FILE = "/tmp/miku_bot_running.txt"
ERROR_FILE = "/tmp/miku_bot_error.txt"

# Check if a port is already in use
def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

# Create a simple status page that will run on port 8080
class StatusPageHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        # Make the content refresh automatically
        uptime = "Unknown"
        if os.path.exists(RUNNING_FILE):
            try:
                with open(RUNNING_FILE, 'r') as f:
                    start_time_str = f.read().strip()
                    start_time = datetime.fromisoformat(start_time_str)
                    uptime_seconds = (datetime.now() - start_time).total_seconds()
                    hours, remainder = divmod(uptime_seconds, 3600)
                    minutes, seconds = divmod(remainder, 60)
                    uptime = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
            except Exception as e:
                logger.error(f"Error calculating uptime: {e}")
        
        page = f"""
        <html>
        <head>
            <title>Miku Bot Status</title>
            <meta http-equiv="refresh" content="30">
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                h1 {{ color: #6a5acd; }}
                h2 {{ color: #9370db; }}
                .status {{ padding: 10px; background-color: #f0f0f0; border-radius: 5px; margin-top: 20px; }}
                .running {{ color: green; }}
                .error {{ color: red; }}
                .features {{ margin-top: 20px; }}
                .feature {{ margin-bottom: 10px; }}
            </style>
        </head>
        <body>
            <h1>Miku Bot Status Page</h1>
            <div class="status">
                <p>
                    <span class="running">✅ Bot is running in standalone mode</span><br>
                    ⏱️ Uptime: {uptime}<br>
                    🎯 Target channel: {os.environ.get('TARGET_CHANNEL', 'Not set')}<br>
                    🕙 Last checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
                <p><i>This status page auto-refreshes every 30 seconds</i></p>
            </div>
            
            <h2>Bot Features</h2>
            <div class="features">
                <div class="feature">✅ <strong>Reddit posts every 3 minutes</strong> - Posts unique Miku content from Reddit</div>
                <div class="feature">✅ <strong>Miku image posts</strong> - Shares images with captions on a regular schedule</div>
                <div class="feature">✅ <strong>Miku facts</strong> - Shares interesting facts about Miku</div>
                <div class="feature">✅ <strong>Duplicate prevention</strong> - Ensures no content is repeated</div>
                <div class="feature">✅ <strong>Automatic tracking</strong> - Monitors subreddits for new Miku content</div>
            </div>
        </body>
        </html>
        """
        
        self.wfile.write(page.encode())
    
    def log_message(self, format, *args):
        # Suppress logging to avoid cluttering the console
        return

# Start the HTTP server
def start_http_server():
    """Start an HTTP server to show the bot status"""
    try:
        # Try to find an available port starting from PORT
        port = PORT
        max_port = PORT + 10  # Try up to 10 ports
        
        while port < max_port:
            if not is_port_in_use(port):
                break
            port += 1
        
        if port >= max_port:
            logger.error(f"Could not find an available port between {PORT} and {max_port-1}")
            return
        
        # Start the HTTP server in a thread
        handler = StatusPageHandler
        httpd = socketserver.TCPServer(("0.0.0.0", port), handler)
        
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True  # Thread will stop when the main program exits
        server_thread.start()
        
        logger.info(f"Started HTTP server on port {port}")
    except Exception as e:
        logger.error(f"Error starting HTTP server: {e}")

# Handle signals
def signal_handler(sig, frame):
    """Handle SIGINT and SIGTERM signals"""
    logger.info(f"Received signal {sig}, shutting down")
    cleanup()
    sys.exit(0)

# Clean up before exiting
def cleanup():
    """Clean up temp files"""
    for file in [PID_FILE, RUNNING_FILE, ERROR_FILE]:
        if os.path.exists(file):
            try:
                os.remove(file)
                logger.info(f"Removed {file}")
            except Exception as e:
                logger.error(f"Error removing {file}: {e}")

# Main function
def main():
    """Main entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Clean up any existing files
        cleanup()
        
        # Start the status page
        start_http_server()
        
        # Set the environment variable to force the right workflow
        os.environ['REPL_WORKFLOW'] = 'run_miku_bot'
        
        # Log the startup
        logger.info("=" * 50)
        logger.info("STANDALONE MIKU BOT STARTED")
        logger.info("Running in the run_miku_bot workflow")
        logger.info("=" * 50)
        
        # Write the PID file
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        
        # Main loop - keep the bot running
        while True:
            # Write the running file with timestamp
            with open(RUNNING_FILE, 'w') as f:
                f.write(datetime.now().isoformat())
            
            # Start the bot process
            logger.info(f"Starting {BOT_SCRIPT}...")
            
            try:
                # Run the bot as a subprocess and capture its output
                process = subprocess.Popen(
                    [sys.executable, BOT_SCRIPT],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )
                
                # Monitor the process
                for line in process.stdout:
                    # Log the bot's output
                    logger.info(f"Bot: {line.strip()}")
                
                # Wait for the process to exit
                exit_code = process.wait()
                
                # Handle the exit
                if exit_code != 0:
                    logger.error(f"Bot process exited with code {exit_code}")
                    with open(ERROR_FILE, 'w') as f:
                        f.write(f"Bot exited with code {exit_code}")
                else:
                    logger.info("Bot process exited normally")
            except Exception as e:
                logger.error(f"Error running bot: {e}")
                with open(ERROR_FILE, 'w') as f:
                    f.write(f"Error: {e}")
            
            # Wait before restarting
            logger.info("Waiting 5 seconds before restarting...")
            time.sleep(5)
    
    except Exception as e:
        logger.error(f"Standalone bot error: {e}")
    
    finally:
        cleanup()

if __name__ == "__main__":
    main()