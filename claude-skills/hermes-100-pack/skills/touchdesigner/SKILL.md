---
name: touchdesigner
description: Control a running TouchDesigner session from Claude through the twozero MCP server (Streamable HTTP on http://127.0.0.1:40404/mcp): create operators, set parameters, wire networks, run Python inside TD, build audio-reactive and GLSL visuals, record video. Use when the user mentions TouchDesigner, TD, twozero, TOPs/CHOPs/SOPs, "make a generative visual", "audio-reactive shader", "projection mapping", or asks to connect TouchDesigner to Claude. Requires TouchDesigner (Windows/macOS) with the twozero.tox installed.
---
# TouchDesigner (twozero MCP)

**Hermes original:** https://github.com/NousResearch/hermes-plugin-touchdesigner @ 88a7a78 · tier: official · category: tools · license: MIT
**Port class:** A — a portable Agent Plugins v1 package: `mcp.json` with one streamable-http server plus a bundled `touchdesigner-mcp` skill; both carry over to Claude's MCP configuration.

## What the Hermes plugin does
Registers the twozero MCP server (`td`, `http://127.0.0.1:40404/mcp`) for every Hermes session and ships `skills/touchdesigner-mcp/` (workflow rules, 21 reference files on operators, GLSL, audio-reactive chains, instancing, pitfalls, and a `scripts/setup.sh` health check). The server exposes 36 `td_*` tools (per the skill): core `td_execute_python`, `td_create_operator`, `td_set_operator_pars`, `td_get_operator_info`, `td_get_network`, `td_get_errors`, `td_get_par_info`, `td_get_hints`, `td_get_focus`; DAT/CHOP read/write; screenshots; search; perf; plus opt-in desktop input automation and admin tools. No Hermes tools or hooks of its own.

## Equivalent in Claude
Register the same MCP server, then follow the bundled skill (copied to `references/upstream-touchdesigner-mcp.md`).

Claude Code (project `.mcp.json`, same shape as the plugin's `mcp.json`):
```json
{"mcpServers": {"td": {"type": "http", "url": "http://127.0.0.1:40404/mcp"}}}
```
or `claude mcp add --transport http td http://127.0.0.1:40404/mcp`.
Claude desktop app: add the URL as a remote MCP server / custom connector in Settings; stdio-only `claude_desktop_config.json` entries do not apply to an HTTP server (not verified in this port).

Working rules from the skill (keep them):
1. Never guess parameter names: call `td_get_par_info` for the op type first; on `tdAttributeError` stop and call `td_get_operator_info`.
2. Call `td_get_hints`, `td_get_focus`, `td_get_network` before building.
3. Prefer `td_create_operator` / `td_set_operator_pars` over `td_execute_python`; wire with Python (`outputConnectors[0].connect(...)`) since no native wire tool exists; split cleanup and creation into separate calls.
4. Verify with `td_get_errors(recursive=true)`, `td_get_perf`, `td_get_screenshot`.
5. Treat `td_input_*`, `td_click_screen_point`, `td_screen_point_to_global`, `td_get_screen_screenshot`, `td_project_quit`, `td_test_session`, `td_dev_log`, `td_clear_dev_log` as opt-in: use only on explicit request.
6. Recording: MovieFileOut TOP with `prores` (macOS) or `mjpa`; H.264/H.265/AV1 need a Commercial license; Non-Commercial caps resolution at 1280x1280.

| Hermes piece | Claude equivalent |
|---|---|
| `mcp.json` server `td` | `.mcp.json` / `claude mcp add` above |
| `skills/touchdesigner-mcp/SKILL.md` | `references/upstream-touchdesigner-mcp.md` |
| `scripts/setup.sh` health check | `curl -s http://127.0.0.1:40404/mcp` (returns JSON with PID, project, TD version per the skill) |

## Setup
1. TouchDesigner 2025.32280+ on Windows or macOS (no Linux build).
2. Download `https://www.404zero.com/pisang/twozero.tox`, drag it into the TD network editor, click Install.
3. twozero icon -> Settings -> mcp -> "auto start MCP" -> Yes. Start TD before starting Claude.
4. Register the MCP server as above; verify with `curl -s http://127.0.0.1:40404/mcp`.

## Limits
- Only the SKILL.md is copied; the 21 `references/*.md` files and `setup.sh` remain upstream (same MIT license, fetch from the repo when needed).
- `td_execute_python` runs arbitrary Python inside TouchDesigner with no sandbox; the hub is localhost-only and unauthenticated, so any local process can drive it.
- `td_test_session` exports transcripts to the vendor hub; never call it unasked.
- The Hermes tool-name shortening rationale (`td` manifest name) does not matter for Claude.
- Not verified in this port: the server was not reachable here (no TouchDesigner on Linux).

## Source
- Catalog entry (reviewed commit): https://github.com/NousResearch/hermes-plugin-touchdesigner/tree/88a7a7884e5eda33cfe4b1dd5e69df7cb15d5898
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/touchdesigner.yaml
