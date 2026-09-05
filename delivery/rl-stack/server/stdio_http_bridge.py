"""Per-machine stdio -> HTTP bridge.

Hermes and Vellum speak stdio MCP. This tiny bridge IS a stdio MCP server to the
client, but forwards every JSON-RPC message to the ONE hosted governance server
over HTTP and returns its reply. So both clients keep their known stdio transport,
while all state lives in a single shared ledger on the hosted server.

The bridge is a dumb, faithful pass-through: it adds nothing to the protocol.

stdlib only.

Client spawns it as:  python3 stdio_http_bridge.py
Env it needs:
  RL_GOV_URL    e.g. https://gov.reticulativelogic.tech/mcp   (the hosted server)
  RL_GOV_TOKEN  the bearer token the hosted server requires
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request

URL = os.environ.get("RL_GOV_URL", "http://127.0.0.1:8787/mcp")
TOKEN = os.environ.get("RL_GOV_TOKEN", "")
TIMEOUT = float(os.environ.get("RL_GOV_TIMEOUT", "30"))


def _post(obj: dict):
    data = json.dumps(obj).encode()
    req = urllib.request.Request(URL, data=data, method="POST",
                                 headers={"Content-Type": "application/json",
                                          # Cloudflare blocks urllib's default UA (1010).
                                          "User-Agent": "RL-Governance-Bridge/1.0"})
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        if resp.status == 202:
            return None  # notification accepted, no body
        body = resp.read()
    return json.loads(body) if body else None


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            sys.stdout.write(json.dumps(
                {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}) + "\n")
            sys.stdout.flush()
            continue
        is_notification = "id" not in req
        try:
            resp = _post(req)
        except Exception as e:  # network/auth failure -> surface as JSON-RPC error
            if not is_notification:
                sys.stdout.write(json.dumps(
                    {"jsonrpc": "2.0", "id": req.get("id"),
                     "error": {"code": -32001, "message": f"governance server unreachable: {e}"}}) + "\n")
                sys.stdout.flush()
            continue
        if resp is not None:
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
