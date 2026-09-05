"""Self-configuring live verification — zero placeholders, zero human decisions.

Finds the hosted governance URL + token from the MCP client config on THIS
machine (the one Hermes/Vellum already use), then runs the full verify battery
from verify_live.py. Nothing to fill in:

  python3 verify_live_auto.py            # auto-detect role, write+read in one place
  python3 verify_live_auto.py --write --case wire_live_1    # run on Hermes (Mac)
  python3 verify_live_auto.py --read  --case wire_live_1    # run on Pax

Config sources, in order (first hit wins; explicit env always overrides):
  1. RL_GOV_URL / RL_GOV_TOKEN already in the environment
  2. ~/.hermes/config.yaml       (Hermes; parsed with stdlib regex — no pyyaml)
  3. /workspace/config.json      (Vellum/Pax; stdlib json)

stdlib only. Python 3.9+.
"""
from __future__ import annotations

import json
import os
import re
import sys


def _from_env():
    url, tok = os.environ.get("RL_GOV_URL", ""), os.environ.get("RL_GOV_TOKEN", "")
    return (url, tok, "environment") if url else None


def _from_hermes():
    path = os.path.expanduser(os.environ.get("HERMES_CONFIG", "~/.hermes/config.yaml"))
    if not os.path.exists(path):
        return None
    text = open(path).read()
    # find the env block values wherever they appear; tolerate quotes and indent
    m_url = re.search(r"^\s*RL_GOV_URL\s*:\s*['\"]?([^'\"\s#]+)", text, re.MULTILINE)
    m_tok = re.search(r"^\s*RL_GOV_TOKEN\s*:\s*['\"]?([^'\"\s#]+)", text, re.MULTILINE)
    if not m_url:
        return None
    return (m_url.group(1), m_tok.group(1) if m_tok else "", path)


def _from_pax():
    path = os.environ.get("PAX_CONFIG", "/workspace/config.json")
    if not os.path.exists(path):
        return None
    try:
        cfg = json.load(open(path))
    except Exception:
        return None
    url = tok = ""
    # walk the whole config: values may sit in an env dict or as VAR=value args
    def walk(node):
        nonlocal url, tok
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "RL_GOV_URL" and isinstance(v, str):
                    url = v
                elif k == "RL_GOV_TOKEN" and isinstance(v, str):
                    tok = v
                else:
                    walk(v)
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, str) and item.startswith("RL_GOV_URL="):
                    url = item.split("=", 1)[1]
                elif isinstance(item, str) and item.startswith("RL_GOV_TOKEN="):
                    tok = item.split("=", 1)[1]
                else:
                    walk(item)
    walk(cfg)
    return (url, tok, path) if url else None


def main():
    found = _from_env() or _from_hermes() or _from_pax()
    if not found:
        print("FAIL could not find RL_GOV_URL in: environment, ~/.hermes/config.yaml, /workspace/config.json")
        print("     If the client config lives elsewhere, set HERMES_CONFIG or PAX_CONFIG to its path.")
        print("     If the config still spawns rl_mcp_server.py directly (no RL_GOV_URL), the fleet has")
        print("     NOT been cut over to the hosted bridge yet — run HERMES_TASK_2.md first.")
        return 1
    url, tok, src = found
    # explicit env always overrides — never let a failed config parse stomp a good token
    tok = os.environ.get("RL_GOV_TOKEN") or tok
    os.environ["RL_GOV_URL"] = url
    os.environ["RL_GOV_TOKEN"] = tok
    print(f"config: {src}")
    print(f"url:    {url}")
    print(f"token:  {'set (' + str(len(tok)) + ' chars)' if tok else 'MISSING'}")
    if not tok:
        print("WARN   no RL_GOV_TOKEN found next to the URL — the 401 check should still pass,")
        print("       but authenticated calls below will fail. Fix the client config.")
    print()

    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, here)
    import importlib
    import verify_live
    importlib.reload(verify_live)  # re-read module-level URL/TOKEN from the env we just set
    return verify_live.main()


if __name__ == "__main__":
    sys.exit(main())
