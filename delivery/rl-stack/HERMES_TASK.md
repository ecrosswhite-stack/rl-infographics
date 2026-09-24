# WORK ORDER — for Hermes (autonomous)

You (Hermes) are being asked to install and self-test the Reticulative Logic
**stack constitution** governance server on this Mac, then wire yourself and
Vellum to it. Run every step; do not hand steps back to the human. Report results.

Assumes you have shell + filesystem access on this machine. If you do not, say so
and stop — that is the one thing that blocks you.

## 1. Pull the payload from GitHub
```bash
REPO=https://github.com/ecrosswhite-stack/rl-infographics.git
BR=claude/build-discussion-39ec4b
rm -rf /tmp/rl-delivery
git clone --branch "$BR" --single-branch "$REPO" /tmp/rl-delivery
cp -r /tmp/rl-delivery/delivery/rl-stack "$HOME/rl-stack"
```

## 2. Place stilling.py beside the server (the server imports it)
```bash
find "$HOME" -name stilling.py -not -path '*/.venv/*' 2>/dev/null   # pick the real one
cp <THE_PATH_ABOVE> "$HOME/rl-stack/server/stilling.py"
```

## 3. Self-test (stdlib only — no pip, out/ is prebuilt)
```bash
cd "$HOME/rl-stack/server"
RL_CONSTITUTION_DIR="$HOME/rl-stack" python3 rl_mcp_server.py test
RL_CONSTITUTION_DIR="$HOME/rl-stack" python3 mcp_smoke_client.py rl_mcp_server.py
```
Expect `19 passed` then `10 passed`. If either fails, capture full output.

## 4. Register this server in your OWN MCP client config
It is a stdio server. Add an entry equivalent to:
```json
{
  "reticulative-logic-governance": {
    "command": "python3",
    "args": ["ABSOLUTE/PATH/rl-stack/server/rl_mcp_server.py"],
    "env": {
      "RL_CONSTITUTION_DIR": "ABSOLUTE/PATH/rl-stack",
      "RL_STILLING_STATE": "ABSOLUTE/PATH/stilling_state.json"
    }
  }
}
```
Use absolute paths. After registering, connect and confirm you can call
`tools/list` (5 STILLING tools) and read the resource `rl://constitution`.

## 5. Do the same for Vellum
If you can edit Vellum's MCP integration config, add the same stdio server entry.
If you cannot, report Vellum's config file path and format instead.

## 6. Report back (this is the deliverable)
Return to the human, for relay to Claude:
1. The `19 passed` / `10 passed` output (or the failure).
2. Your MCP config: file path + format, and the exact entry you added.
3. The `protocolVersion` you negotiate on `initialize`.
4. Whether you consume `resources/*` or only `tools/*`.
5. Vellum's config path + format (and whether you wired it).

With (2)–(5) Claude will finalize exact, ready-to-paste entries for both clients
and close the last open item (handshake verified against the real clients).
```
