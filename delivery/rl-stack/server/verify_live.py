"""Verify a LIVE hosted governance deployment. Run on the fleet, not the sandbox.

Proves the things "live" must mean, against the real hosted server:
  1. /health reachable over its URL (and, if https, TLS terminated)
  2. token enforced: an unauthenticated write is rejected (401)
  3. tools + resources both served (initialize)
  4. the constitution resource is served (rl://constitution, version)
  5. a write lands and the SAME server reads it back (shared ledger)
  6. the pre-registration ledger verifies (tamper-evident) — prints the tip hash

Cross-MACHINE proof (one shared gate across Hermes + Pax) needs two runs:
  on Hermes:  python3 verify_live.py --write   --case wire_$(date +%s)
  on Pax:     python3 verify_live.py --read    --case <same id Hermes printed>
A --read that finds the id a --write created on the OTHER machine IS the shared gate.
With no flag it does write+read in one place (proves shared server, one machine).

Env: RL_GOV_URL (e.g. https://gov.example/mcp), RL_GOV_TOKEN.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request

URL = os.environ.get("RL_GOV_URL", "http://127.0.0.1:8787/mcp")
TOKEN = os.environ.get("RL_GOV_TOKEN", "")
CLASS = os.environ.get("RL_VERIFY_CLASS", "wire_test")
# Cloudflare blocks urllib's default UA (error 1010) — same fact the bridge handles.
UA = "rl-verify/1.0"


def _health_url() -> str:
    base = URL.rsplit("/", 1)[0] if "/" in URL.split("://", 1)[-1] else URL
    return base.rstrip("/") + "/health"


def _post(obj, token=TOKEN, timeout=30):
    req = urllib.request.Request(URL, data=json.dumps(obj).encode(), method="POST",
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": UA})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            try:
                return r.status, (json.loads(body or b"null"))
            except ValueError:
                return r.status, None
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception as e:  # DNS, refused, TLS, timeout — record FAIL, don't crash
        print(f"  transport error: {e}")
        return 0, None


def _call(name, args):
    _, resp = _post({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                     "params": {"name": name, "arguments": args}})
    if not resp or "result" not in resp:
        return None
    try:
        return json.loads(resp["result"]["content"][0]["text"])
    except (KeyError, IndexError, TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--read", action="store_true")
    ap.add_argument("--case", default=None, help="case_id (use the same on both machines)")
    ap.add_argument("--expect-tip", default=None,
                    help="full ledger tip printed by the --write run on the other machine")
    a = ap.parse_args()
    do_write = a.write or not a.read
    do_read = a.read or not a.write
    case_id = a.case or f"wire_{os.getpid()}"

    tests, fail = [], []
    def check(name, cond, extra=""):
        tests.append(name); print(("PASS " if cond else "FAIL ") + name + (f"  {extra}" if extra else ""))
        if not cond: fail.append(name)

    # 1. health (custom UA — Cloudflare rejects urllib's default with error 1010)
    try:
        hreq = urllib.request.Request(_health_url(), headers={"User-Agent": UA})
        with urllib.request.urlopen(hreq, timeout=15) as r:
            h = json.loads(r.read())
        check("health_reachable", h.get("ok") is True, _health_url())
        check("tls_https", _health_url().startswith("https://"), "(else terminate TLS)")
    except Exception as e:
        check("health_reachable", False, f"{_health_url()} -> {e}")

    # 2. token enforced (unauth write rejected)
    code, _ = _post({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                     "params": {"name": "stilling_status", "arguments": {}}}, token="")
    check("token_enforced_401", code == 401, f"(got {code}; 401 required for a live deploy)")

    # 3. initialize advertises tools + resources
    _, ini = _post({"jsonrpc": "2.0", "id": 2, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
    caps = (ini or {}).get("result", {}).get("capabilities", {})
    check("advertises_tools", "tools" in caps)
    check("advertises_resources", "resources" in caps)

    # 4. constitution resource
    _, rr = _post({"jsonrpc": "2.0", "id": 3, "method": "resources/read",
                   "params": {"uri": "rl://constitution"}})
    text = (rr or {}).get("result", {}).get("contents", [{}])[0].get("text", "")
    check("constitution_served", "STACK CONSTITUTION" in text)

    # 5. write / read the shared ledger
    if do_write:
        p = _call("stilling_preregister", {
            "case_id": case_id, "decision_class": CLASS, "unit": "wire/verify",
            "system_value": 1.0, "baseline_value": 2.0, "baseline_label": "wire_baseline",
            "tier": "B_PROSPECTIVE"})
        check("write_preregister", bool(p and len(p.get("hash", "")) == 64), f"case_id={case_id}")
        if p and p.get("ledger_tip"):
            print(f"  hand to the reader:  --read --case {case_id} --expect-tip {p['ledger_tip']}")
    if do_read:
        if a.expect_tip:
            # Sound cross-machine proof: identical full tip hash => identical chain
            # => the reader's server holds the writer's commit. (A mismatch can also
            # mean another write landed in between — false FAIL, never false PASS.)
            v0 = _call("stilling_verify_ledger", {"decision_class": CLASS})
            tip = (v0 or {}).get("tip") or ""
            check("read_sees_write_tip", tip == a.expect_tip,
                  f"tip={tip[:16]} expected={a.expect_tip[:16]}")
        else:
            st = _call("stilling_status", {})
            seen = any(c["decision_class"] == CLASS and c["cases"] >= 1 for c in (st or {}).get("classes", []))
            check("read_sees_case", seen,
                  f"WEAK: class-count only, not a cross-machine proof — pass --expect-tip (class={CLASS})")

    # 6. ledger verifies
    v = _call("stilling_verify_ledger", {"decision_class": CLASS})
    check("ledger_verifies", bool(v and v.get("verified") is True),
          f"tip={ (v or {}).get('tip','')[:16] }")

    print(f"\n=== {len(tests)-len(fail)} passed, {len(fail)} failed, {len(tests)} total ===")
    if fail:
        print("NOT verified live. Failures above name what's missing.")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
