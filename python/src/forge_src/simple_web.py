#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 8085
Handler = http.server.SimpleHTTPRequestHandler

print(f"🔥 Explorer-d334 Web Interface")
print(f"🌐 http://localhost:{PORT}")
print(f"📁 Serving from: {os.getcwd()}")
print("Press Ctrl+C to stop")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
