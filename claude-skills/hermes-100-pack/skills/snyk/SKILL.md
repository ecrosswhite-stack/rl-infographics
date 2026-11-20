---
name: snyk
description: Scan code (SAST), dependencies (SCA), container images, infrastructure-as-code and SBOMs with Snyk's first-party MCP server, pinned to snyk@1.1306.0 over npx stdio, and follow the bundled snyk-security-scan workflow (auth, trust, scan, fix, re-scan). Use when the user says "scan this with Snyk", "security scan", "check this package before I add it", "vulnerable dependencies", "SAST", "scan my Dockerfile/Terraform", "SBOM", "snyk_code_scan", or asks whether a dependency upgrade is safe.
---
# Snyk security scanning

**Hermes original:** https://github.com/NousResearch/hermes-plugin-snyk @ 2a41a07 · tier: official · category: tools · license: MIT
**Port class:** A · a portable Agent Plugins v1 package (`plugin.json` + `mcp.json` + `skills/`); its MCP server entry drops into Claude's MCP configuration unchanged.

## What the Hermes plugin does
Ships one MCP server entry, `sn`, launched as `npx -y snyk@1.1306.0 mcp -t stdio --profile full --DISABLE_ANALYTICS` with `SNYK_DISABLE_ANALYTICS=1`, plus the skill `snyk-security-scan`. The server (inside the Snyk CLI) exposes 13 tools: `snyk_code_scan`, `snyk_sca_scan`, `snyk_container_scan`, `snyk_iac_scan`, `snyk_sbom_scan`, `snyk_aibom`, `snyk_package_health_check`, `snyk_breakability_check`, `snyk_auth`, `snyk_trust`, `snyk_logout`, `snyk_version`, `snyk_send_feedback`. The plugin itself registers no Hermes tools or hooks.

## Equivalent in Claude
Add the same server to Claude, then follow the upstream workflow in `references/upstream-snyk-security-scan.md`.

1. `snyk_auth` once per machine (browser login; token stays in the Snyk CLI config).
2. Resolve the absolute path of the target (`pwd`); every `path`/`file` argument must be absolute.
3. On a trust error, call `snyk_trust` with that absolute path, only for the folder the user asked to scan.
4. Run the scanner; start with `severity_threshold: "high"` on large trees. Python SCA requires `command: "python3"`.
5. Fix what the user agrees to, re-run the same scan, report before/after counts.

| Hermes usage | How Claude does it |
|---|---|
| `mcp__agent_plugin_snyk_<hash>__sn__snyk_code_scan` etc. | the same tool names under the `sn` server in Claude's MCP tool list |
| `skill_view agent-plugin-snyk-...:snyk-security-scan` | read `references/upstream-snyk-security-scan.md` |
| `hermes plugins enable snyk` | add the JSON below and restart Claude |

## Setup
1. Install Node.js so `npx` is on `PATH`. Verified: `npm view snyk@1.1306.0 name version` returns `name = 'snyk'`, `version = '1.1306.0'` (latest at check time was 1.1309.0; keep the pin unless you review the bump).
2. Add the server (copied from the plugin's `mcp.json`) to `claude_desktop_config.json`, or to Claude Code with `claude mcp add-json sn '<the object below>'`:
   ```json
   {
     "mcpServers": {
       "sn": {
         "command": "npx",
         "args": ["-y", "snyk@1.1306.0", "mcp", "-t", "stdio", "--profile", "full", "--DISABLE_ANALYTICS"],
         "env": { "SNYK_DISABLE_ANALYTICS": "1" }
       }
     }
   }
   ```
3. Start a new session; the first launch downloads the pinned CLI (tens of MB).
4. Create a free Snyk account; run the `snyk_auth` tool before the first scan.
5. For SCA, have the project's package manager installed so Snyk can resolve the dependency tree.

## Limits
- Scans are network calls: SAST uploads source and SCA uploads the dependency graph to Snyk's cloud. Ask before scanning private or client repositories and skip directories holding secrets or `.env` files.
- `snyk_trust` is a one-way grant on the user's machine; use it only for the requested folder.
- `snyk_send_feedback` sends issue-count telemetry to Snyk; treat it as opt-in and never call it unprompted.
- Free-tier accounts have monthly test limits; "limit reached" is not a bug.
- `snyk_aibom` is a gated preview feature and may be unavailable.
- The server key is `sn` rather than `snyk` because `snyk_package_health_check` with a `snyk` prefix hit the 64-character tool-name cap in OpenAI-style wire formats (per the plugin README); Claude does not enforce that cap, but keep `sn` so the upstream skill's names match.
- Only `SKILL.md` was copied; the full per-tool argument table lives upstream at `skills/snyk-security-scan/references/tools.md`.

## Source
- Catalog entry (reviewed commit): https://github.com/NousResearch/hermes-plugin-snyk/tree/2a41a07f81e45125bf82a19af1b13396ace4b81f
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/snyk.yaml
