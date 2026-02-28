from http.server import BaseHTTPRequestHandler
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import _store

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._cors(204)

    def do_GET(self):
        # GET /signal → same as /signal/history shortcut
        self._cors(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "count":    len(_store._history),
            "readings": _store.get_history(),
        }).encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        body   = {}
        if length:
            try:
                body = json.loads(self.rfile.read(length).decode())
            except Exception:
                pass
        if not body:
            self._cors(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error":"empty body"}')
            return
        _store.push(body)
        self._cors(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "ok",
            "stored": len(_store._history),
        }).encode())

    def _cors(self, code):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
