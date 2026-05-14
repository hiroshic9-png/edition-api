#!/usr/bin/env python3
"""SPA-aware HTTP server for EDITION development."""
import http.server
import os

PORT = 8899
DIR = os.path.dirname(os.path.abspath(__file__))

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def do_GET(self):
        # Serve static files if they exist
        path = self.translate_path(self.path)
        if os.path.isfile(path):
            return super().do_GET()
        # For directory paths that have index.html
        if os.path.isdir(path) and os.path.isfile(os.path.join(path, 'index.html')):
            return super().do_GET()
        # SPA fallback: serve index.html for all other routes
        self.path = '/index.html'
        return super().do_GET()

if __name__ == '__main__':
    with http.server.HTTPServer(('', PORT), SPAHandler) as httpd:
        print(f"  EDITION dev server: http://localhost:{PORT}/")
        httpd.serve_forever()
