#!/usr/bin/env python3
"""
Simple HTTP server on port 7788 serving agent_log.json.
Run: python3 agent_server.py

Endpoints:
  GET /log?since=N  — returns all log entries with id > N (default: all)
  GET /log/clear    — resets the log file
"""
import json, os, sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

LOG_FILE  = os.path.join(os.path.dirname(__file__), 'agent_log.json')
GRID_FILE  = os.path.join(os.path.dirname(__file__), 'agent_grid.json')
TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'token_state.json')
PORT = 7788


def read_log():
    import time
    try:
        with open(LOG_FILE) as f:
            log = json.load(f)
        if log:
            today = time.strftime('%Y-%m-%d', time.localtime())
            first_day = time.strftime('%Y-%m-%d', time.localtime(log[0]['ts']))
            if first_day != today:
                with open(LOG_FILE, 'w') as f:
                    json.dump([], f)
                return []
        return log
    except (FileNotFoundError, json.JSONDecodeError):
        return []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence access logs

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/log':
            log = read_log()
            qs = parse_qs(parsed.query)
            since = int(qs.get('since', ['-1'])[0])
            entries = [e for e in log if e.get('id', 0) > since]
            # Day reset: client counter is ahead of current log (IDs restarted from 0)
            # Return all entries so the browser's reset detection can trigger
            if not entries and since > 0 and log:
                entries = log
            body = json.dumps(entries).encode()
        elif parsed.path == '/log/clear':
            try:
                with open(LOG_FILE, 'w') as f:
                    json.dump([], f)
            except Exception:
                pass
            body = json.dumps({'ok': True}).encode()
        elif parsed.path == '/tokens':
            try:
                with open(TOKEN_FILE) as f:
                    body = f.read().encode()
            except FileNotFoundError:
                body = json.dumps({'pct_remaining': 100, 'pct_used': 0}).encode()
        elif parsed.path == '/grid':
            try:
                with open(GRID_FILE) as f:
                    body = f.read().encode()
            except FileNotFoundError:
                body = b'[]'
        else:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self._cors()
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/grid':
            length = int(self.headers.get('Content-Length', 0))
            data = self.rfile.read(length)
            try:
                json.loads(data)  # validate JSON
                with open(GRID_FILE, 'wb') as f:
                    f.write(data)
                body = json.dumps({'ok': True}).encode()
                self.send_response(200)
            except Exception:
                body = json.dumps({'error': 'invalid'}).encode()
                self.send_response(400)
            self._cors()
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')


if __name__ == '__main__':
    server = HTTPServer(('localhost', PORT), Handler)
    print(f'Agent server running at http://localhost:{PORT}/log')
    print(f'Reading log from: {LOG_FILE}')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nStopped.')
        sys.exit(0)
