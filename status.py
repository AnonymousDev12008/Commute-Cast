from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._cors(204)

    def do_GET(self):
        self._cors(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        # C++ processes can't run on Vercel — always report stopped
        self.wfile.write(json.dumps({
            "sender":       "stopped",
            "receiver_buf": "stopped",
            "receiver_raw": "stopped",
            "note":         "C++ demo not available on Vercel. Run control_server.py locally for demo mode."
        }).encode())

    def _cors(self, code):
        self.send_response(code)
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
