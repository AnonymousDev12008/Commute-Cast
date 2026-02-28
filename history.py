from http.server import BaseHTTPRequestHandler
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import _store

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._cors(204)

    def do_GET(self):
        try:
            qs = self.path.split("?", 1)[1] if "?" in self.path else ""
            n  = int(dict(p.split("=") for p in qs.split("&") if "=" in p).get("n", _store.MAX_READINGS))
        except Exception:
            n = _store.MAX_READINGS
        self._cors(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({
            "count":    len(_store._history),
            "readings": _store.get_history(n),
        }).encode())

    def _cors(self, code):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
