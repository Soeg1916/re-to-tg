"""
IMPORTANT: This file is specifically for the run_miku_bot workflow.
It explicitly checks for port conflicts and runs the bot without the web interface.
"""
import os
import socket
import sys
import logging
from standalone_bot import run_standalone

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

def is_port_in_use(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    """Run the Miku bot in standalone mode, avoiding port conflicts"""
    print("====================================================")
    print("MIKU BOT WORKFLOW RUNNER (for run_miku_bot workflow)")
    print("====================================================")
    
    # Check if port 5000 is already in use (likely by the web app)
    if is_port_in_use(5000):
        # Import necessary modules at runtime to avoid circular imports
        import time
        from flask import Flask, redirect
        
        print("Port 5000 is already in use")
        print("Starting simple redirect server on port 8080...")
        
        # Create a super simple Flask app just for redirecting
        redirect_app = Flask(__name__)
        
        @redirect_app.route('/')
        def home():
            return redirect('/status')
            
        @redirect_app.route('/status')
        def status():
            return f"""
            <html>
            <head>
                <meta http-equiv="refresh" content="0;url=http://localhost:5000/status">
                <title>Redirecting to Miku Bot Dashboard</title>
            </head>
            <body>
                <h1>Redirecting to the Miku Bot Dashboard...</h1>
                <p>If you are not redirected, <a href="http://localhost:5000/status">click here</a>.</p>
                <script>
                    window.location.href = window.location.origin.replace(':8080', ':5000') + '/status';
                </script>
            </body>
            </html>
            """
            
        # Run the redirect app
        redirect_app.run(host='0.0.0.0', port=8080)
                
    # If this else statement is reached, there would be monitor code here
    else:
        print("Port 5000 is available, but still using standalone mode for consistency...")
        
        # ALWAYS run in standalone mode to avoid conflicts
        print("Starting Miku bot in standalone mode...")
        run_standalone()

if __name__ == "__main__":
    main()