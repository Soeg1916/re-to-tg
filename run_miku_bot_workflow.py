"""
IMPORTANT: This file is specifically for the run_miku_bot workflow.
It explicitly checks for port conflicts and runs the bot without the web interface.
"""
import os
import sys
import socket
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Check if a port is already in use
def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    """Run the Miku bot in standalone mode, avoiding port conflicts"""
    # Check if we're in the run_miku_bot workflow
    workflow = os.environ.get('REPL_WORKFLOW', '')
    print(f"Current workflow: {workflow}")
    
    # If port 5000 is in use, force standalone mode
    if is_port_in_use(5000):
        print("Port 5000 is already in use. Running bot in standalone mode.")
        import run_bot_override
        return
    
    # But also run standalone if we're in the run_miku_bot workflow
    if workflow == 'run_miku_bot':
        print("Detected run_miku_bot workflow. Running bot in standalone mode.")
        import run_bot_override
        return
    
    # Otherwise, run in combined mode
    try:
        print("Running in combined mode.")
        from flask import Flask
        
        app = Flask(__name__)
        
        @app.route('/')
        def home():
            return "Miku Bot Running"
            
        @app.route('/status')
        def status():
            return "Bot is active"
        
        # Start the bot in a separate thread
        import threading
        from bot import setup_bot
        
        bot_thread = threading.Thread(target=setup_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000)
    except ImportError:
        # If Flask import fails, run standalone
        print("Could not import Flask. Running in standalone mode.")
        import run_bot_override
        
if __name__ == "__main__":
    main()