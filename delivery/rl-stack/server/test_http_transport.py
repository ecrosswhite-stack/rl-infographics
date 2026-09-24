"""Regression tests for the hosted governance transport and bridge."""
from __future__ import annotations

import http.client
import importlib.util
import json
import os
import sys
import threading
import types
import unittest
from pathlib import Path
from unittest import mock

import stdio_http_bridge


SERVER_DIR = Path(__file__).resolve().parent


def _load_transport():
    fake_governance = types.ModuleType("rl_mcp_server")
    fake_governance.__dict__.update(
        SERVER_NAME="test-governance",
        SERVER_VERSION="test",
        STATE_PATH="/tmp/test-state.json",
        load_state=lambda: None,
    )
    fake_governance.__dict__["_error"] = lambda request_id, code, message: {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }
    fake_governance.__dict__["handle"] = lambda request: {
        "jsonrpc": "2.0",
        "id": request.get("id"),
        "result": {},
    }
    spec = importlib.util.spec_from_file_location(
        "http_transport_under_test", SERVER_DIR / "http_transport.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load http_transport.py")
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, {"rl_mcp_server": fake_governance}):
        spec.loader.exec_module(module)
    return module


class HttpTransportConnectionTests(unittest.TestCase):
    def test_bridge_sets_cloudflare_safe_user_agent(self):
        captured = {}

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self):
                return b'{"jsonrpc":"2.0","id":1,"result":{}}'

        def fake_urlopen(request, timeout):
            captured["user_agent"] = request.get_header("User-agent")
            return Response()

        with mock.patch.object(stdio_http_bridge.urllib.request, "urlopen", fake_urlopen):
            stdio_http_bridge._post({"jsonrpc": "2.0", "id": 1, "method": "ping"})

        self.assertEqual("RL-Governance-Bridge/1.0", captured["user_agent"])

    def test_unauthorized_post_does_not_poison_keepalive_connection(self):
        """The server consumes a rejected body before the socket is reused."""
        with mock.patch.dict(
            os.environ,
            {
                "RL_GOV_TOKEN": "correct-token",
                "RL_GOV_HOST": "127.0.0.1",
                "RL_GOV_PORT": "0",
            },
        ):
            transport = _load_transport()

        server = transport.ThreadingHTTPServer(("127.0.0.1", 0), transport.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        connection = http.client.HTTPConnection(
            "127.0.0.1", server.server_address[1], timeout=2
        )
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "ping"})
        try:
            connection.request(
                "POST",
                "/mcp",
                body=body,
                headers={"Content-Type": "application/json"},
            )
            response = connection.getresponse()
            response.read()
            self.assertEqual(401, response.status)

            connection.request(
                "POST",
                "/mcp",
                body=body,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer correct-token",
                },
            )
            response = connection.getresponse()
            payload = json.loads(response.read())
            self.assertEqual(200, response.status)
            self.assertEqual({}, payload["result"])
        finally:
            connection.close()
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
