#!/usr/bin/env python3
"""
Web Hybrid Interface for Explorer-d334
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler

# Default settings
PORT = 8085
HOST = '0.0.0.0'

class HybridHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
            <!DOCTYPE html>
            <html>
            <head><title>Explorer-d334 Forge</title></head>
            <body>
                <h1>🔥 Explorer-d334 Forge</h1>
                <p>Sovereign AI Forge is running!</p>
                <p>Use commands in terminal: ./forge think, ./forge cubes, etc.</p>
            </body>
            </html>
            ''')
        else:
            self.send_response(404)
            self.end_headers()

def main():
    print(f"Starting web server on http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop")
    server = HTTPServer((HOST, PORT), HybridHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()
