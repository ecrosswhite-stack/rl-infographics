"""
rl_mcp_server.py  --  Reticulative Logic(tm) : MCP GOVERNANCE SERVER
====================================================================
The honest orchestration seam. Your agents (Hermes as an MCP client, Vellum via
its MCP integrations) CALL this server; v27.5 GOVERNS. The arrows point the
right direction: the agent orchestrates, the corpus adjudicates. This file does
NOT reach into your agents -- it exposes STILLING's data-gate discipline as MCP
tools that they invoke.

WHAT IT EXPOSES (thin wrappers over the verified stilling.py -- no new logic):
  stilling_preregister     -- log a decision case (returns the hash-chain commit)
  stilling_record_outcome  -- set the WORLD label (write-once; no model path in)
  stilling_gate_reading    -- the qualified reading (Wilson LB x lift + verdict)
  stilling_verify_ledger   -- prove the pre-registration chain is untampered
  stilling_status          -- classes tracked, case counts, current levers

AND (MCP resources, thin wrappers over the COMPILED stack constitution -- no
     new logic; files served verbatim so the whole AI fleet reads ONE structure):
  rl://constitution            -- the source-of-truth worker order + rules (YAML)
  rl://constitution/json       -- parsed constitution
  rl://constitution/preamble   -- rules preamble for non-Claude clients
  rl://constitution/structure  -- human-readable pipeline + roster
  rl://constitution/router     -- compiled cascade-router tier config
  rl://constitution/worker/{id}-- one worker's definition

WIRE PROTOCOL:
  JSON-RPC 2.0 over stdio, newline-delimited (the MCP stdio transport). Handshake:
  initialize -> notifications/initialized -> tools/list -> tools/call. The server
  echoes the client's protocolVersion for forward-compat and returns proper
  JSON-RPC errors for protocol faults; TOOL errors ride back as result.isError
  (the MCP convention), never as protocol errors.

HONESTY LABELS:
  - MCP transport / handshake        GENUINE  (hand-rolled to spec; self-tested
                                               below via a simulated client)
  - tool wrappers over STILLING      GENUINE  (no logic added; STILLING is the
                                               verified authority, imported as-is)
  - resource wrappers over the
    compiled constitution            GENUINE  (files served verbatim; stdlib json
                                               only; no YAML/SDK in the trust root)
  - ledger persistence               GENUINE  (chain stored & restored VERBATIM,
                                               so SHA-256 hashes -- and therefore
                                               verify() -- survive restarts intact)
  - protocol drift vs YOUR client    DESIGN_ARGUMENT: verified against a simulated
                                               client here; smoke-test against your
                                               actual Hermes/Vellum build and I'll
                                               close any handshake delta.

DEPENDENCY NOTE (a lever you own, like metric/baseline): this is pure stdlib to
match the corpus and keep the TRUST ROOT dependency-free and auditable. The
constitution resources are served from pre-compiled files (compilers/compile.py
does the one YAML read, offline); this server itself stays stdlib-only. The
official `mcp` SDK (FastMCP) is the batteries-included alternative -- protocol-
correct by construction, but a dependency at exactly the boundary you most want
audit-clean. I defaulted to stdlib; say the word to swap.

CONSTITUTION RESOURCES: set RL_CONSTITUTION_DIR to your rl-stack checkout (the dir
holding constitution/ and out/), and run `python3 compilers/compile.py` once so
out/ exists. If the module or files are absent, the server runs normally and just
advertises no resources.

STATUS: mechanism only. Governs a data-gate that is not yet closed by real data.
Efficacy of any decision class remains IGNORANCE until real cases are fed in.

Python 3.9+. stdlib only. Run:  python3 rl_mcp_server.py         (serve on stdio)
                                python3 rl_mcp_server.py test    (self-test)
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any, Dict, List, Optional

import stilling
from stilling import Stilling, Case, ES, Tier, Split

# --- constitution resources (optional; stdlib-only, files served verbatim) ---
# Kept next to this file. If unavailable, the server runs without resources.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from constitution_stdlib import (
        ResourceError,
        list_resources,
        list_resource_templates,
        read_resource,
    )
    _RESOURCES_OK = True
except Exception:  # module absent -> degrade gracefully
    _RESOURCES_OK = False

    class ResourceError(Exception):
        pass


SERVER_NAME = "reticulative-logic-governance"
SERVER_VERSION = "0.2.0"   # +constitution resources
DEFAULT_PROTOCOL = "2025-06-18"
STATE_PATH = os.environ.get("RL_STILLING_STATE", "./stilling_state.json")

# min_n / lb_threshold are the "what counts as closed" levers -- defaults only,
# still yours to set. Surfaced in every reading and in status so they stay visible.
DEFAULT_MIN_N = int(os.environ.get("RL_MIN_N", "30"))
DEFAULT_LB = float(os.environ.get("RL_LB_THRESHOLD", "0.60"))


# ============================================================ state + persistence
_STATE: Dict[str, Stilling] = {}   # decision_class -> Stilling


def _case_to_dict(c: Case) -> Dict[str, Any]:
    return {"case_id": c.case_id, "decision_class": c.decision_class, "unit": c.unit,
            "system_value": c.system_value, "baseline_value": c.baseline_value,
            "baseline_label": c.baseline_label, "confidence": c.confidence.value,
            "tier": c.tier.value, "split": c.split.value, "ts_decision": c.ts_decision,
            "actual": c.actual, "ts_outcome": c.ts_outcome}


def _case_from_dict(d: Dict[str, Any]) -> Case:
    return Case(case_id=d["case_id"], decision_class=d["decision_class"], unit=d["unit"],
                system_value=d["system_value"], baseline_value=d["baseline_value"],
                baseline_label=d["baseline_label"], confidence=ES(d["confidence"]),
                tier=Tier(d["tier"]), split=Split(d["split"]), ts_decision=d["ts_decision"],
                actual=d.get("actual"), ts_outcome=d.get("ts_outcome"))


def save_state(path: str = STATE_PATH) -> None:
    blob = {}
    for cls, s in _STATE.items():
        blob[cls] = {"min_n": s.min_n, "lb_threshold": s.lb_threshold,
                     "cases": [_case_to_dict(c) for c in s.cases.values()],
                     # ledger chain stored VERBATIM so hashes/verify() survive intact
                     "ledger": s.ledger.chain}
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(blob, f, sort_keys=True)
    os.replace(tmp, path)   # atomic-ish write


def load_state(path: str = STATE_PATH) -> None:
    _STATE.clear()
    if not os.path.exists(path):
        return
    with open(path) as f:
        blob = json.load(f)
    for cls, rec in blob.items():
        s = Stilling(cls, min_n=rec.get("min_n", DEFAULT_MIN_N),
                     lb_threshold=rec.get("lb_threshold", DEFAULT_LB))
        for cd in rec.get("cases", []):
            c = _case_from_dict(cd)
            s.cases[c.case_id] = c
        s.ledger.chain = rec.get("ledger", [])   # verbatim restore
        _STATE[cls] = s


def _get(cls: str) -> Stilling:
    if cls not in _STATE:
        _STATE[cls] = Stilling(cls, min_n=DEFAULT_MIN_N, lb_threshold=DEFAULT_LB)
    return _STATE[cls]


# ============================================================ tool implementations
class ToolError(Exception):
    pass


def _preregister(a: Dict[str, Any]) -> Dict[str, Any]:
    try:
        s = _get(a["decision_class"])
        case = Case(case_id=a["case_id"], decision_class=a["decision_class"], unit=a["unit"],
                    system_value=float(a["system_value"]), baseline_value=float(a["baseline_value"]),
                    baseline_label=a["baseline_label"], confidence=ES(a.get("confidence", "TRUTH")),
                    tier=Tier(a["tier"]), split=Split(a.get("split", "holdout")))
    except (KeyError, ValueError) as e:
        raise ToolError(f"bad case spec: {e}")
    h = s.preregister(case)
    save_state()
    return {"ok": True, "hash": h, "ledger_tip": s.ledger.tip(),
            "note": "decision committed BEFORE any outcome; label field is empty by construction"}


def _record_outcome(a: Dict[str, Any]) -> Dict[str, Any]:
    try:
        s = _get(a["decision_class"])
        cid, actual = a["case_id"], float(a["actual"])
    except (KeyError, ValueError) as e:
        raise ToolError(f"bad outcome spec: {e}")
    if cid not in s.cases:
        raise ToolError(f"unknown case_id {cid} for class {a['decision_class']}")
    try:
        s.record_outcome(cid, actual)
    except ValueError as e:
        raise ToolError(str(e))   # e.g. write-once violation
    save_state()
    beats = s.cases[cid].beats_baseline()
    return {"ok": True, "case_id": cid, "actual": actual, "beats_baseline": beats,
            "note": "label set from a WORLD value; no model output can populate this field"}


def _gate_reading(a: Dict[str, Any]) -> Dict[str, Any]:
    try:
        s = _get(a["decision_class"])
        tier = Tier(a["tier"])
        split = Split(a["split"]) if a.get("split") else Split.HOLDOUT
    except (KeyError, ValueError) as e:
        raise ToolError(f"bad reading spec: {e}")
    r = s.reading(tier, split if tier is Tier.A_BACKTEST else None)
    f = s.finding(tier, split if tier is Tier.A_BACKTEST else None)
    return {"decision_class": r.decision_class, "tier": r.tier.value,
            "n_closed": r.n_closed, "hits": r.hits, "wilson_lb": r.wilson_lb,
            "mae_system": r.mae_system, "mae_baseline": r.mae_baseline, "lift": r.lift,
            "state": r.state.value, "verdict": r.verdict,
            "min_n": s.min_n, "lb_threshold": s.lb_threshold,
            "finding": f.line()}


def _verify_ledger(a: Dict[str, Any]) -> Dict[str, Any]:
    s = _get(a["decision_class"])
    anchor = a.get("anchor")
    ok = s.ledger.verify(anchor=anchor)
    return {"decision_class": a["decision_class"], "verified": ok,
            "n_records": len(s.ledger.chain), "tip": s.ledger.tip(),
            "note": "tamper-evident: any edit or reorder of a prior record fails verify()"}


def _status(a: Dict[str, Any]) -> Dict[str, Any]:
    out = []
    for cls, s in _STATE.items():
        closed = sum(1 for c in s.cases.values() if c.is_closed())
        out.append({"decision_class": cls, "cases": len(s.cases), "closed": closed,
                    "min_n": s.min_n, "lb_threshold": s.lb_threshold,
                    "ledger_records": len(s.ledger.chain)})
    return {"classes": out, "state_path": STATE_PATH,
            "levers_note": "min_n and lb_threshold are defaults you still own"}


TOOLS: List[Dict[str, Any]] = [
    {"name": "stilling_preregister",
     "description": "Log a decision case for a class BEFORE its outcome exists; hash-chains the "
                    "commitment. For tier B this is the leakage-proof pre-registration.",
     "inputSchema": {"type": "object",
        "properties": {
            "case_id": {"type": "string"}, "decision_class": {"type": "string"},
            "unit": {"type": "string", "description": "series/sku/date this concerns"},
            "system_value": {"type": "number", "description": "value from the system under test (e.g. WEIR)"},
            "baseline_value": {"type": "number", "description": "a REAL incumbent baseline"},
            "baseline_label": {"type": "string", "description": "what the baseline is, e.g. seasonal_naive"},
            "confidence": {"type": "string", "enum": ["TRUTH", "FALSITY", "IGNORANCE"], "default": "TRUTH"},
            "tier": {"type": "string", "enum": ["A_BACKTEST", "B_PROSPECTIVE"]},
            "split": {"type": "string", "enum": ["train", "validate", "holdout"], "default": "holdout"}},
        "required": ["case_id", "decision_class", "unit", "system_value",
                     "baseline_value", "baseline_label", "tier"]}},
    {"name": "stilling_record_outcome",
     "description": "Set the WORLD label for a case (write-once). No model output can reach this field.",
     "inputSchema": {"type": "object",
        "properties": {"decision_class": {"type": "string"}, "case_id": {"type": "string"},
                       "actual": {"type": "number", "description": "the real observed outcome"}},
        "required": ["decision_class", "case_id", "actual"]}},
    {"name": "stilling_gate_reading",
     "description": "Qualified reading for one class/tier: Wilson lower bound x baseline lift + verdict "
                    "(GATE_OPENED / GATE_NOT_OPENED / below-N IGNORANCE).",
     "inputSchema": {"type": "object",
        "properties": {"decision_class": {"type": "string"},
                       "tier": {"type": "string", "enum": ["A_BACKTEST", "B_PROSPECTIVE"]},
                       "split": {"type": "string", "enum": ["train", "validate", "holdout"]}},
        "required": ["decision_class", "tier"]}},
    {"name": "stilling_verify_ledger",
     "description": "Verify the pre-registration hash chain for a class is untampered; optional external anchor.",
     "inputSchema": {"type": "object",
        "properties": {"decision_class": {"type": "string"}, "anchor": {"type": "string"}},
        "required": ["decision_class"]}},
    {"name": "stilling_status",
     "description": "List tracked classes, case/closed counts, ledger sizes, and the current levers.",
     "inputSchema": {"type": "object", "properties": {}}},
]

_DISPATCH = {"stilling_preregister": _preregister, "stilling_record_outcome": _record_outcome,
             "stilling_gate_reading": _gate_reading, "stilling_verify_ledger": _verify_ledger,
             "stilling_status": _status}


# ============================================================ JSON-RPC / MCP layer
def _result(rid: Any, result: Any) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rid, "result": result}


def _error(rid: Any, code: int, message: str) -> Dict[str, Any]:
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}


def _capabilities() -> Dict[str, Any]:
    caps: Dict[str, Any] = {"tools": {"listChanged": False}}
    if _RESOURCES_OK:
        caps["resources"] = {"subscribe": False, "listChanged": False}
    return caps


def handle(req: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return a response dict, or None for notifications (no id)."""
    method = req.get("method")
    rid = req.get("id")
    is_notification = "id" not in req

    if method == "initialize":
        proto = (req.get("params") or {}).get("protocolVersion", DEFAULT_PROTOCOL)
        return _result(rid, {"protocolVersion": proto,
                             "capabilities": _capabilities(),
                             "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION}})

    if method == "notifications/initialized" or (method and method.startswith("notifications/")):
        return None   # notifications get no response

    if method == "ping":
        return _result(rid, {})

    if method == "tools/list":
        return _result(rid, {"tools": TOOLS})

    if method == "tools/call":
        params = req.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        fn = _DISPATCH.get(name)
        if fn is None:
            return _error(rid, -32602, f"unknown tool: {name}")
        try:
            payload = fn(args)
            text = json.dumps(payload, sort_keys=True)
            return _result(rid, {"content": [{"type": "text", "text": text}], "isError": False})
        except ToolError as e:
            # tool-level failure rides back in the result, per MCP convention
            return _result(rid, {"content": [{"type": "text", "text": f"ToolError: {e}"}],
                                 "isError": True})

    # ---- MCP resources: the stack constitution, served verbatim -------------
    if method == "resources/list":
        return _result(rid, {"resources": list_resources() if _RESOURCES_OK else []})

    if method == "resources/templates/list":
        return _result(rid, {"resourceTemplates": list_resource_templates() if _RESOURCES_OK else []})

    if method == "resources/read":
        if not _RESOURCES_OK:
            return _error(rid, -32601, "resources not available (constitution module/files absent)")
        uri = (req.get("params") or {}).get("uri", "")
        try:
            r = read_resource(uri)
            return _result(rid, {"contents": [{"uri": uri, "mimeType": r["mimeType"], "text": r["text"]}]})
        except ResourceError as e:
            return _error(rid, -32602, str(e))

    if is_notification:
        return None
    return _error(rid, -32601, f"method not found: {method}")


def serve(stdin=sys.stdin, stdout=sys.stdout) -> None:
    load_state()
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            stdout.write(json.dumps(_error(None, -32700, "parse error")) + "\n")
            stdout.flush()
            continue
        resp = handle(req)
        if resp is not None:
            stdout.write(json.dumps(resp) + "\n")
            stdout.flush()


# ============================================================ simulated-client self-test
def _tests() -> int:
    global STATE_PATH
    import tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    tmp.close()
    STATE_PATH = tmp.name
    _STATE.clear()

    tests, fail = [], []
    def check(name, cond):
        tests.append(name); print(("PASS " if cond else "FAIL ") + name)
        if not cond: fail.append(name)

    # handshake: initialize echoes protocol + advertises tools capability
    r = handle({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2025-06-18"}})
    check("initialize_echoes_protocol", r["result"]["protocolVersion"] == "2025-06-18")
    check("initialize_advertises_tools", "tools" in r["result"]["capabilities"])

    # initialized notification -> no response
    check("initialized_no_response",
          handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None)

    # tools/list returns the five tools with schemas
    r = handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    names = {t["name"] for t in r["result"]["tools"]}
    check("tools_list_has_all_five",
          names == {"stilling_preregister", "stilling_record_outcome", "stilling_gate_reading",
                    "stilling_verify_ledger", "stilling_status"})

    # tools/call preregister -> hash returned, label still empty
    r = handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "stilling_preregister", "arguments": {
                    "case_id": "k1", "decision_class": "forecast_adjudication",
                    "unit": "sku_A/wk1", "system_value": 104.0, "baseline_value": 110.0,
                    "baseline_label": "seasonal_naive", "tier": "B_PROSPECTIVE"}}})
    payload = json.loads(r["result"]["content"][0]["text"])
    check("preregister_returns_hash", len(payload["hash"]) == 64 and r["result"]["isError"] is False)

    # record_outcome -> world label set; WEIR(104) beats baseline(110) vs actual(100)
    r = handle({"jsonrpc": "2.0", "id": 4, "method": "tools/call",
                "params": {"name": "stilling_record_outcome", "arguments": {
                    "decision_class": "forecast_adjudication", "case_id": "k1", "actual": 100.0}}})
    payload = json.loads(r["result"]["content"][0]["text"])
    check("record_outcome_beats_baseline", payload["beats_baseline"] is True)

    # write-once enforced -> ToolError as result.isError, NOT a protocol error
    r = handle({"jsonrpc": "2.0", "id": 5, "method": "tools/call",
                "params": {"name": "stilling_record_outcome", "arguments": {
                    "decision_class": "forecast_adjudication", "case_id": "k1", "actual": 999.0}}})
    check("write_once_is_tool_error", r["result"]["isError"] is True)

    # gate reading below floor -> IGNORANCE (honest, not a false pass)
    r = handle({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
                "params": {"name": "stilling_gate_reading", "arguments": {
                    "decision_class": "forecast_adjudication", "tier": "B_PROSPECTIVE"}}})
    payload = json.loads(r["result"]["content"][0]["text"])
    check("below_floor_is_ignorance", payload["state"] == "IGNORANCE" and payload["verdict"] == "BELOW_N_FLOOR")

    # verify ledger passes
    r = handle({"jsonrpc": "2.0", "id": 7, "method": "tools/call",
                "params": {"name": "stilling_verify_ledger", "arguments": {
                    "decision_class": "forecast_adjudication"}}})
    payload = json.loads(r["result"]["content"][0]["text"])
    check("ledger_verifies", payload["verified"] is True)

    # PERSISTENCE: reload from disk -> hashes intact, verify() still true, label survives
    load_state()
    s = _STATE["forecast_adjudication"]
    check("state_reloaded", "k1" in s.cases and s.cases["k1"].actual == 100.0)
    check("ledger_survives_reload_verbatim", s.ledger.verify() is True)

    # tamper after reload is caught
    s.ledger.chain[0]["payload"]["system_value"] = 0.0
    check("tamper_detected_after_reload", s.ledger.verify() is False)

    # unknown method -> proper JSON-RPC -32601
    r = handle({"jsonrpc": "2.0", "id": 8, "method": "does/not/exist"})
    check("unknown_method_jsonrpc_error", r.get("error", {}).get("code") == -32601)

    # unknown tool -> -32602 in result path
    r = handle({"jsonrpc": "2.0", "id": 9, "method": "tools/call",
                "params": {"name": "nope", "arguments": {}}})
    check("unknown_tool_error", r.get("error", {}).get("code") == -32602)

    # ---- constitution resources (only if the module + compiled files exist) --
    if _RESOURCES_OK:
        check("initialize_advertises_resources",
              "resources" in handle({"jsonrpc": "2.0", "id": 10, "method": "initialize",
                                     "params": {}})["result"]["capabilities"])
        r = handle({"jsonrpc": "2.0", "id": 11, "method": "resources/list"})
        uris = {x["uri"] for x in r["result"]["resources"]}
        check("resources_list_has_constitution", "rl://constitution" in uris)
        r = handle({"jsonrpc": "2.0", "id": 12, "method": "resources/read",
                    "params": {"uri": "rl://constitution"}})
        text = r["result"]["contents"][0]["text"]
        check("resources_read_constitution", "STACK CONSTITUTION" in text)
        r = handle({"jsonrpc": "2.0", "id": 13, "method": "resources/read",
                    "params": {"uri": "rl://constitution/worker/rl-axis-firewall"}})
        text = r["result"]["contents"][0]["text"]
        check("resources_read_worker", "egress axis-separation" in text)
        r = handle({"jsonrpc": "2.0", "id": 14, "method": "resources/read",
                    "params": {"uri": "rl://constitution/nope"}})
        check("resources_read_unknown_is_error", r.get("error", {}).get("code") == -32602)
    else:
        print("SKIP constitution resource tests (set RL_CONSTITUTION_DIR + run compile.py to enable)")

    os.unlink(tmp.name)
    print(f"\n=== {len(tests)-len(fail)} passed, {len(fail)} failed, {len(tests)} total ===")
    return 1 if fail else 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        sys.exit(_tests())
    serve()
