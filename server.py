#!/usr/bin/env python3
import http.server
import os

PORT = 58472
ROOT = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_POST(self):
        ALLOWED = {'/data/geocache.json', '/data/verifications.json'}
        if self.path in ALLOWED:
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            filename = self.path.lstrip('/')  # e.g. "data/geocache.json"
            out = os.path.join(ROOT, filename)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, 'wb') as f:
                f.write(body)
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(405)
            self.end_headers()

    def log_message(self, *args):
        pass  # suppress per-request noise

if __name__ == '__main__':
    os.chdir(ROOT)
    with http.server.HTTPServer(('localhost', PORT), Handler) as httpd:
        print(f'Serveris veikia: http://localhost:{PORT}', flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
