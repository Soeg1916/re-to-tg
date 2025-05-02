#!/usr/bin/env python3
"""
IMPORTANT: This file is specifically for the run_miku_bot workflow.
It explicitly checks for port conflicts and runs the bot without the web interface.
"""
import os
import sys
import time
import socket
import logging
import subprocess
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("workflow_runner.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("workflow_runner")

# Check if a port is already in use
def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    """Run the Miku bot in standalone mode, avoiding port conflicts"""
    # Mark the start
    logger.info("=" * 60)
    logger.info("WORKFLOW RUNNER STARTED - MIKU BOT ONLY")
    logger.info("This script runs only the bot in the run_miku_bot workflow")
    logger.info("=" * 60)
    
    # Check if port 5000 is in use (likely by the Start application workflow)
    if is_port_in_use(5000):
        logger.info("Port 5000 is in use - running bot only with minimal HTTP server")
        
        # Set up simple status server on port 8080
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class SimpleHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                if self.path == '/':
                    content = f"""
                    <html>
                    <head>
                        <title>Miku Bot Status</title>
                        <meta http-equiv="refresh" content="30">
                        <style>
                            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                            h1 {{ color: #6a5acd; }}
                            .status {{ padding: 10px; background-color: #f0f0f0; border-radius: 5px; }}
                            .running {{ color: green; }}
                        </style>
                    </head>
                    <body>
                        <h1>Miku Bot Status</h1>
                        <div class="status">
                            <p><span class="running">✅ Bot is running in standalone mode</span></p>
                            <p>Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                            <p>Target channel: {os.environ.get('TARGET_CHANNEL', 'Not set')}</p>
                            <p>This status page auto-refreshes every 30 seconds</p>
                        </div>
                    </body>
                    </html>
                    """
                elif self.path == '/status':
                    content = '{"status": "running", "mode": "standalone"}'
                else:
                    content = '{"error": "Not found"}'
                
                self.wfile.write(content.encode())
            
            def log_message(self, format, *args):
                # Suppress logging to avoid cluttering the console
                pass
        
        # Start HTTP server in a separate thread
        import threading
        server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        logger.info("Started status server on port 8080")
    
    # Set environment variable to indicate we're in the correct workflow
    os.environ['REPL_WORKFLOW'] = 'run_miku_bot'
    
    # Run the direct bot script
    try:
        logger.info("Starting direct_miku_bot.py...")
        subprocess.run([sys.executable, "direct_miku_bot.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Bot process failed with exit code {e.returncode}")
    except Exception as e:
        logger.error(f"Error running bot: {e}")

if __name__ == "__main__":
    main()