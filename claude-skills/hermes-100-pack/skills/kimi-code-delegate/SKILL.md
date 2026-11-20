---
name: kimi-code-delegate
description: Delegate a self-contained, read-only analysis prompt to a locally installed and logged-in Kimi Code CLI over its ACP (Agent Client Protocol) stdio interface, the way the Hermes "kimi-code-delegate" plugin does, by driving `kimi acp` from Claude Code with a small JSON-RPC script. Use when the user says "ask Kimi", "get a second opinion from Kimi Code", "delegate this to kimi k3", "kimi_code_delegate", or wants Kimi's advisory answer without giving it file, terminal or network access.
---
# Kimi Code read-only delegation

**Hermes original:** https://github.com/s-a-s-k-i-a/hermes-kimi-code @ 72c741c · tier: community · category: tools · license: MIT
**Port class:** B · the plugin spawns the user's `kimi` CLI as `[command, "acp"]` and speaks JSON-RPC over stdio; Claude Code can run the same process and protocol with a script, leaving only the tool registration, `hermes kimi-code doctor` and `config.yaml` keys as Hermes-specific.

## What the Hermes plugin does
Registers one tool, `kimi_code_delegate(prompt, model?, thinking?)` (kind `standalone`), plus the CLI command `hermes kimi-code doctor`. Per call it starts one fresh `kimi acp` process with an allowlisted environment (`PATH`, `HOME`, `KIMI_CODE_HOME`, proxy and locale variables; no Hermes secrets), runs `initialize` (protocolVersion 1, `fs` read/write disabled), `authenticate` with `methodId: "login"`, `session/new` with `mcpServers: []`, sets `model` (`kimi-code/k3` or `kimi-code/k3-256k`) and `thinking` through `session/set_config_option`, then sends `session/prompt`. It rejects every ACP permission request and answers filesystem/terminal requests with errors, caps prompts at 100,000 characters, redacts secrets from diagnostics, and treats an empty reply as an error (`empty_response`). It deliberately does not register Kimi as a Hermes model provider.

## Equivalent in Claude
Prefer Claude Code subagents for ordinary delegation. When the user specifically wants Kimi's view:

1. Locate the CLI exactly as the plugin does: `~/.kimi-code/bin/kimi` first, then `command -v kimi`. If absent, stop and tell the user to install Kimi Code and run `kimi login` interactively. Never ask for or handle Kimi tokens.
2. Write a small Python script (outside any untrusted directory) that starts `subprocess.Popen([kimi_path, "acp"], stdin=PIPE, stdout=PIPE, stderr=PIPE, text=True, cwd=<read-only context dir>, env=<allowlist: PATH, HOME, TMPDIR, LANG, LC_*, KIMI_CODE_HOME, proxy vars>)` and exchanges newline-delimited JSON-RPC 2.0 messages, in this order (params copied from the plugin source):
   - `initialize` → `{"protocolVersion": 1, "clientCapabilities": {"fs": {"readTextFile": false, "writeTextFile": false}}, "clientInfo": {"name": "...", "version": "..."}}`; require `protocolVersion == 1`, an `agentInfo.name` containing "kimi", and an `authMethods` entry with id `login`.
   - `authenticate` → `{"methodId": "login"}`.
   - `session/new` → `{"cwd": "<dir>", "mcpServers": []}`; read `sessionId` and `configOptions`.
   - `session/set_config_option` → `{"sessionId", "configId": "model", "value": "kimi-code/k3"}` (or `kimi-code/k3-256k`), only if that value appears in the advertised options; same for `configId: "thinking"` (keep the advertised `currentValue` for "auto").
   - `session/prompt` → `{"sessionId", "prompt": [{"type": "text", "text": "READ-ONLY DELEGATION BOUNDARY: Return analysis or suggested text only. Do not execute tools... Delegated task:\n" + prompt}]}`; collect streamed `session/update` text chunks until the result arrives.
3. While waiting, answer any inbound JSON-RPC request from Kimi: permission requests get the `reject_once` option (or `{"outcome": "cancelled"}`); `fs/*` and `terminal/*` requests get a JSON-RPC error.
4. Enforce the plugin's bounds: prompt ≤ 100,000 chars, startup timeout about 10 s, overall timeout 300 s (max 1800), kill the process group afterwards. Treat an empty text result as a failure and report that provider status is unknown (check `kimi login` and quota).
5. Return Kimi's text to the user labelled as Kimi's advisory output. The prompt must be self-contained; paste the needed non-secret context into it.

| Hermes piece | How Claude does it |
|---|---|
| `kimi_code_delegate` tool | run the ACP script above with the user's prompt |
| `hermes kimi-code doctor` | run steps `initialize` + `authenticate` only and report agent name/version |
| `plugins.entries.kimi-code-delegate.{command,working_directory,timeout_seconds,model,thinking}` | script arguments |

## Setup
1. Install Kimi Code CLI (the plugin was tested with Kimi Code 0.29.2; install instructions are Kimi's, not verified here) and run `kimi login` in an interactive terminal.
2. Optionally set `KIMI_CODE_HOME` if Kimi's config lives outside the default `HOME`.
3. No Claude-side MCP server is involved; `pip index versions kimi-cli` returns 1.52.0 but it was not verified to be the same product as "Kimi Code", so do not install it on that assumption.

## Limits
- The exact ACP wire shapes for streamed updates (`session/update`) and the `stopReason` field were taken from the plugin's client; behavior of newer Kimi releases is not verified.
- Delegation spends the user's Kimi quota and sends the prompt to Moonshot's service.
- No model-provider integration: Kimi is never used for Claude's own turns, matching the plugin's fail-closed design.
- Doctor-style handshake success does not prove a live login; only a successful prompt does (per the plugin README).

## Source
- Catalog entry (reviewed commit): https://github.com/s-a-s-k-i-a/hermes-kimi-code/tree/72c741cc166ec1db2aec4cd5316f7b7281a74b40
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/kimi-code-delegate.yaml
