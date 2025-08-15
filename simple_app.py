#!/usr/bin/env python3
"""Simple HTTP server without dependencies"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
from datetime import datetime

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response = {
            "status": "running",
            "message": "Simple Python server working!",
            "version": "NO-DEPS-v1",
            "timestamp": datetime.now().isoformat(),
            "port": os.environ.get('PORT', '8080'),
            "path": self.path
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Server starting on port {port}")
    server.serve_forever()