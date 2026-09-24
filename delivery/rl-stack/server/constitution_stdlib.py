"""Constitution as MCP resources — stdlib only, no YAML, no SDK.

Serves the COMPILED constitution files (produced by compilers/compile.py) so the
governance server stays dependency-free and audit-clean, matching its trust-root
policy. The server reads these files verbatim; it adds no logic and no parsing
beyond stdlib json.

Point RL_CONSTITUTION_DIR at your rl-stack checkout (the dir containing
`constitution/` and `out/`). Defaults to ./rl-stack.

Exposed resources:
  rl://constitution            raw YAML source of truth        (text/yaml)
  rl://constitution/json       parsed constitution             (application/json)
  rl://constitution/preamble   preamble for non-Claude clients (text/markdown)
  rl://constitution/structure  human-readable pipeline+roster  (text/markdown)
  rl://constitution/router     compiled router tier config     (application/json)
  rl://constitution/worker/{id}  one worker's definition       (application/json)
"""
from __future__ import annotations

import json
import os

BASE_DIR = os.environ.get("RL_CONSTITUTION_DIR", "./rl-stack")


def _p(*parts) -> str:
    return os.path.join(BASE_DIR, *parts)


# static resources: uri -> (file path, mimeType, human name, description)
_FILES = {
    "rl://constitution":            ("constitution/stack-constitution.yaml", "text/yaml", "Stack Constitution (YAML)", "The single source of truth for worker order and rules."),
    "rl://constitution/json":       ("out/constitution.json", "application/json", "Stack Constitution (JSON)", "Parsed constitution."),
    "rl://constitution/preamble":   ("out/system_preamble.md", "text/markdown", "System preamble", "Rules preamble for non-Claude clients (Kimi/GPT/Gemini/Grok/Hermes)."),
    "rl://constitution/structure":  ("out/STRUCTURE.md", "text/markdown", "Stack structure", "Human-readable pipeline + roster."),
    "rl://constitution/router":     ("out/router_config.json", "application/json", "Router config", "Compiled cascade-router tier + routing config."),
}

_TEMPLATES = [
    {"uriTemplate": "rl://constitution/worker/{worker_id}",
     "name": "Worker definition",
     "description": "One governance worker's role, pipeline placement, and rules.",
     "mimeType": "application/json"},
]


def list_resources() -> list[dict]:
    out = []
    for uri, (_, mime, name, desc) in _FILES.items():
        out.append({"uri": uri, "name": name, "description": desc, "mimeType": mime})
    return out


def list_resource_templates() -> list[dict]:
    return list(_TEMPLATES)


class ResourceError(Exception):
    pass


def read_resource(uri: str) -> dict:
    """Return {'text': str, 'mimeType': str} for a resource uri, or raise ResourceError."""
    if uri in _FILES:
        rel, mime, _, _ = _FILES[uri]
        path = _p(rel)
        if not os.path.exists(path):
            raise ResourceError(f"resource file missing: {path} (run compilers/compile.py)")
        with open(path) as f:
            return {"text": f.read(), "mimeType": mime}

    prefix = "rl://constitution/worker/"
    if uri.startswith(prefix):
        worker_id = uri[len(prefix):]
        cj = _p("out/constitution.json")
        if not os.path.exists(cj):
            raise ResourceError(f"resource file missing: {cj} (run compilers/compile.py)")
        with open(cj) as f:
            c = json.load(f)
        w = c.get("workers", {}).get(worker_id)
        if not w:
            raise ResourceError(f"unknown worker: {worker_id}")
        step = next((s for s in c.get("pipeline", []) if s["worker"] == worker_id), {})
        payload = {"id": worker_id, "definition": w, "pipeline": step,
                   "hard_rules": c.get("hard_rules", {}), "version": c["meta"]["version"]}
        return {"text": json.dumps(payload, indent=2), "mimeType": "application/json"}

    raise ResourceError(f"unknown resource uri: {uri}")


if __name__ == "__main__":
    # tiny self-check
    print("resources:", [r["uri"] for r in list_resources()])
    print("templates:", [t["uriTemplate"] for t in list_resource_templates()])
    try:
        r = read_resource("rl://constitution")
        print("read rl://constitution ->", len(r["text"]), "bytes,", r["mimeType"])
    except ResourceError as e:
        print("ERR:", e)
