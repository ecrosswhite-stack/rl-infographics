"""A real MCP client that drives the governance server over stdio.

This is the honest version of "smoke-test the handshake": it spawns the server as
a subprocess and runs the exact connect sequence a spec-compliant MCP client
(Hermes, Vellum, Claude-via-MCP) performs — initialize -> initialized ->
tools/list -> resources/list -> resources/read -> tools/call -> ping — asserting
the server's replies conform. Passing here proves the SERVER side is conformant.
The remaining delta vs. YOUR specific client build stays a DESIGN_ARGUMENT until
you point the real Hermes/Vellum at this same server.

Run:  RL_CONSTITUTION_DIR=/path/to/rl-stack python3 server/mcp_smoke_client.py [path/to/rl_mcp_server.py]
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

PROTO = "2025-06-18"


def main() -> int:
    server = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "rl_mcp_server.py")
    proc = subprocess.Popen([sys.executable, server], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            text=True, bufsize=1)

    def send(obj):
        proc.stdin.write(json.dumps(obj) + "\n")
        proc.stdin.flush()

    def rpc(rid, method, **params):
        send({"jsonrpc": "2.0", "id": rid, "method": method, **({"params": params} if params else {})})
        return json.loads(proc.stdout.readline())

    tests, fail = [], []
    def check(name, cond):
        tests.append(name); print(("PASS " if cond else "FAIL ") + name)
        if not cond: fail.append(name)

    try:
        # 1. initialize
        r = rpc(1, "initialize", protocolVersion=PROTO, capabilities={},
                clientInfo={"name": "mcp-smoke-client", "version": "1.0"})
        res = r["result"]
        check("initialize_ok", r.get("id") == 1 and "serverInfo" in res)
        check("protocol_echoed", res["protocolVersion"] == PROTO)
        check("advertises_tools", "tools" in res["capabilities"])
        check("advertises_resources", "resources" in res["capabilities"])

        # 2. initialized notification (no response)
        send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        # 3. tools/list
        r = rpc(2, "tools/list")
        names = {t["name"] for t in r["result"]["tools"]}
        check("tools_present", "stilling_status" in names and len(names) == 5)

        # 4. resources/list + templates
        r = rpc(3, "resources/list")
        uris = {x["uri"] for x in r["result"]["resources"]}
        check("resources_present", "rl://constitution" in uris)
        r = rpc(4, "resources/templates/list")
        tmpls = {t["uriTemplate"] for t in r["result"]["resourceTemplates"]}
        check("worker_template_present", any("worker/{" in t for t in tmpls))

        # 5. resources/read
        r = rpc(5, "resources/read", uri="rl://constitution/structure")
        text = r["result"]["contents"][0]["text"]
        check("read_structure", "Pipeline" in text)

        # 6. tools/call
        r = rpc(6, "tools/call", name="stilling_status", arguments={})
        check("call_status_ok", r["result"]["isError"] is False)

        # 7. ping
        r = rpc(7, "ping")
        check("ping_ok", r["result"] == {})

    finally:
        proc.stdin.close()
        proc.terminate()

    print(f"\n=== {len(tests)-len(fail)} passed, {len(fail)} failed, {len(tests)} total ===")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
