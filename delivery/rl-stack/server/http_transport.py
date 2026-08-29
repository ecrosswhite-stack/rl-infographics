"""Networked transport for the governance server: ONE shared ledger for the fleet.

Wraps the existing, verified `handle()` (from rl_mcp_server.py) behind an HTTP
endpoint so Hermes (Mac) and Vellum/Pax (remote) hit the SAME server process and
therefore the SAME stilling_state.json — one data gate, not two. A single process
serializes writes, so the hash-chain / write-once guarantees are preserved
unchanged; this adds a transport, not new governance logic.

stdlib only. Reuses rl_mcp_server.handle / load_state.

Security (do not skip for a networked deploy):
  - Set RL_GOV_TOKEN. Requests must send `Authorization: Bearer <token>`.
  - Bind to localhost by default; expose it only behind TLS you terminate
    (your reticulativelogic.tech domain / a tunnel). Never run token-less on a
    public interface — the ledger accepts writes.

Run:
  RL_GOV_TOKEN=... RL_STILLING_STATE=/data/stilling_state.json \
  RL_GOV_HOST=0.0.0.0 RL_GOV_PORT=8787 python3 http_transport.py
Endpoints:
  POST /mcp     one JSON-RPC message -> one JSON-RPC response (202 for notifications)
  GET  /health  -> {"ok": true}
"""
from __future__ import annotations

import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import rl_mcp_server as gov

TOKEN = os.environ.get("RL_GOV_TOKEN", "")
HOST = os.environ.get("RL_GOV_HOST", "127.0.0.1")
PORT = int(os.environ.get("RL_GOV_PORT", "8787"))
PATH = os.environ.get("RL_GOV_PATH", "/mcp")

# One lock so concurrent bridges can't interleave a preregister/record + save.
_LOCK = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _send(self, code: int, body: bytes = b"", ctype: str = "application/json"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _authed(self) -> bool:
        if not TOKEN:
            return True  # no token configured (dev only)
        return self.headers.get("Authorization", "") == f"Bearer {TOKEN}"

    def do_GET(self):
        if self.path.rstrip("/") == "/health":
            self._send(200, json.dumps({"ok": True, "server": gov.SERVER_NAME,
                                        "version": gov.SERVER_VERSION}).encode())
        else:
            self._send(404, b'{"error":"not found"}')

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b""
        if self.path.split("?")[0].rstrip("/") != PATH.rstrip("/"):
            self._send(404, b'{"error":"not found"}')
            return
        if not self._authed():
            self._send(401, b'{"error":"unauthorized"}')
            return
        try:
            req = json.loads(raw or b"{}")
        except json.JSONDecodeError:
            self._send(400, json.dumps(gov._error(None, -32700, "parse error")).encode())
            return
        with _LOCK:
            resp = gov.handle(req)
        if resp is None:
            self._send(202, b"")   # notification: accepted, no body
        else:
            self._send(200, json.dumps(resp).encode())

    def log_message(self, *a):
        pass  # quiet; wire your own logging if you want an audit trail


def main():
    gov.load_state()
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    tok = "token REQUIRED" if TOKEN else "NO TOKEN (dev only)"
    print(f"{gov.SERVER_NAME} v{gov.SERVER_VERSION} on http://{HOST}:{PORT}{PATH}  [{tok}]  "
          f"state={gov.STATE_PATH}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()
