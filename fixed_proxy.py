#!/usr/bin/env python3
"""
Fixed HTTP Proxy Server for AIBOA Frontend
Properly handles GET requests to API endpoints
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
from urllib.error import URLError
import socket

class ProxyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_html()
        elif self.path == "/health":
            self.send_json({"status": "healthy", "service": "frontend-proxy"})
        elif self.path == "/favicon.ico":
            # Handle favicon request
            self.send_response(404)
            self.end_headers()
        elif self.path.startswith("/api/transcribe/"):
            # Handle GET requests to transcription API (job status)
            self.proxy_request("http://localhost:8000")
        elif self.path.startswith("/api/analyze/"):
            # Handle GET requests to analysis API
            self.proxy_request("http://localhost:8001")
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        if self.path.startswith("/api/transcribe/"):
            self.proxy_request("http://localhost:8000")
        elif self.path.startswith("/api/analyze/"):
            self.proxy_request("http://localhost:8001")
        else:
            self.send_error(404, "API endpoint not found")
    
    def serve_html(self):
        try:
            with open("index.html", "r", encoding="utf-8") as f:
                content = f.read()
            
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(content.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "UI file not found")
    
    def proxy_request(self, target_base):
        try:
            # Get request body if POST
            content_length = int(self.headers.get('Content-Length', 0))
            body_data = self.rfile.read(content_length) if content_length > 0 else b''
            
            # Build target URL
            target_url = f"{target_base}{self.path}"
            
            # Create request
            req = urllib.request.Request(
                target_url,
                data=body_data if body_data else None,
                method=self.command
            )
            
            # Copy headers (except problematic ones)
            skip_headers = {'host', 'content-length', 'connection', 'accept-encoding'}
            for header, value in self.headers.items():
                if header.lower() not in skip_headers:
                    req.add_header(header, value)
            
            # Make request with timeout
            try:
                with urllib.request.urlopen(req, timeout=30) as response:
                    response_data = response.read()
                    
                    # Send response
                    self.send_response(response.code)
                    
                    # Copy response headers
                    for header, value in response.headers.items():
                        if header.lower() not in {'connection', 'transfer-encoding'}:
                            self.send_header(header, value)
                    
                    self.end_headers()
                    self.wfile.write(response_data)
                    
            except URLError as e:
                print(f"Proxy error for {target_url}: {e}")
                self.send_json({"error": f"Backend service unavailable: {str(e)}"}, 503)
                
        except Exception as e:
            print(f"General proxy error: {e}")
            self.send_json({"error": f"Proxy error: {str(e)}"}, 500)
    
    def send_json(self, data, status=200):
        json_data = json.dumps(data).encode('utf-8')
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(json_data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
        self.wfile.write(json_data)
    
    def do_OPTIONS(self):
        # Handle CORS preflight
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[{self.address_string()}] {format % args}")

if __name__ == "__main__":
    port = 3000
    server = HTTPServer(("0.0.0.0", port), ProxyHandler)
    print(f"🚀 Fixed frontend proxy server running on port {port}")
    print(f"🌐 Access at: http://localhost:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.shutdown()