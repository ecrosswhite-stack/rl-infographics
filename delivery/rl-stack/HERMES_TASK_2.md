# WORK ORDER 2 — for Hermes (autonomous): unify the fleet on ONE hosted gate

Decision (from Eris): **one shared STILLING data-gate** across Hermes + Vellum/Pax,
which are on **separate machines**. So we replace the two local stdio servers with
**one hosted HTTP server** (single ledger, single constitution) that both clients
reach through a tiny local **stdio→HTTP bridge**. Both clients keep stdio transport.

## AUTONOMY — make the infra choices yourself; do not hand them back
Eris said "make it live." Run this end to end and make the operational calls
yourself; only stop and report if you truly cannot obtain a host both machines can
reach. Specifically, decide on your own:
- **Host:** use the box that already serves `api.reticulativelogic.tech` if both
  Hermes and Pax can reach it; otherwise host on whichever machine both can reach
  over your existing tunnel/VPN, or stand up a tunnel. You know the network; pick.
- **Token:** generate one (`openssl rand -hex 32`), place it in both client env
  blocks, never commit it. Report only that it's set, not the value.
- **TLS:** terminate via your existing reverse proxy / tunnel.
- **Migration:** default to a FRESH shared ledger and archive the old local files,
  UNLESS `stilling_status` on either machine shows real (non-test) cases — then
  archive read-only and route new captures to shared (do not merge). Report counts.
Report the final `/health` URL, the cross-client proof, and the migration path taken.

Verified already (in Claude's sandbox, against the real stilling.py): bridge
handshake 10/10; a case preregistered via one bridge is visible via the other
(one shared gate). Your job: deploy it on real infra and cut both clients over.

## 0. Pull the latest payload
```bash
cd /tmp/rl-delivery && git fetch origin claude/build-discussion-39ec4b && \
  git checkout claude/build-discussion-39ec4b && git pull
cp -r /tmp/rl-delivery/delivery/rl-stack/server/. "$HOME/rl-stack/server/"   # gets http_transport.py + stdio_http_bridge.py
```

## 1. Choose the host both machines can reach
Use a box on your reticulativelogic.tech infra (or the swarm host). It needs:
`rl-stack/` (with `out/` and `constitution/`), your real `stilling.py` beside
`server/rl_mcp_server.py`, and Python 3.9+. Terminate **TLS** in front of it
(your domain / a tunnel) — the ledger accepts writes.

## 2. Run ONE hosted server (single instance — do not run replicas on one file)
```bash
export RL_GOV_TOKEN="$(openssl rand -hex 32)"          # keep this secret; you'll paste it into both clients
export RL_STILLING_STATE=/var/lib/rl/stilling_state.json   # the ONE shared ledger
export RL_CONSTITUTION_DIR=/opt/rl-stack                    # the ONE constitution
export RL_GOV_HOST=0.0.0.0 RL_GOV_PORT=8787
cd /opt/rl-stack/server && python3 http_transport.py       # run under systemd/pm2 for restart
curl -s https://gov.your-domain/health                      # -> {"ok": true, ...}
```
Record the public URL (e.g. `https://gov.reticulativelogic.tech/mcp`) and the token.

## 3. Cut BOTH clients over to the bridge (they stop spawning local servers)

**Hermes** — `/Users/ecrosswhite/.hermes/config.yaml`:
```yaml
mcp_servers:
  reticulative-logic-governance:
    command: /usr/bin/python3
    args:
      - /Users/ecrosswhite/rl-stack/server/stdio_http_bridge.py
    env:
      RL_GOV_URL: https://gov.reticulativelogic.tech/mcp
      RL_GOV_TOKEN: <PASTE_TOKEN>
    connect_timeout: 30.0
    enabled: true
```

**Vellum/Pax** — `/workspace/config.json`:
```json
{ "mcp": { "servers": { "reticulative-logic-governance": {
  "transport": { "type": "stdio", "command": "/usr/bin/env", "args": [
    "RL_GOV_URL=https://gov.reticulativelogic.tech/mcp",
    "RL_GOV_TOKEN=<PASTE_TOKEN>",
    "/usr/bin/python3", "/workspace/rl-stack/server/stdio_http_bridge.py" ] },
  "enabled": true, "defaultRiskLevel": "low" } } } }
```
Each machine still needs `stdio_http_bridge.py` present at that path (it's tiny,
stdlib-only). The local `rl_mcp_server.py` is no longer used by the client.

## 4. Prove the shared gate across the two real clients
- From Hermes: call `stilling_preregister` for a throwaway case id.
- From Vellum: call `stilling_status` — it must show that case (same ledger).
- From either: read resource `rl://constitution` — served by the one host.
Then remove the throwaway case is not possible (write-once) — so use an obviously
test decision_class like `wire_test` for this, not a real class.

## 5. Migration of the two OLD local ledgers — do NOT fake a merge
Check each old local `stilling_state.json` (Hermes `/Users/.../rl-stack/`, Vellum
`/workspace/rl-stack/`) with `stilling_status`:
- **If both are empty / only test cases** (most likely — the gate is UNMET and no
  real labeled cases have been fed): start the shared ledger fresh; archive and
  retire the two local files.
- **If either holds REAL preregistered cases:** do not re-preregister them into the
  shared server — that would rewrite timestamps/hashes and break the
  "committed-before-outcome" property (tier B integrity). Keep the old file as a
  read-only archive, and route all NEW captures to the shared server from now on.
  Report the counts so Eris/Claude decide how to treat the archived cases.

## 6. Report back
- `/health` URL + that TLS is terminated (yes/no).
- The step-4 cross-client proof output.
- Old-ledger case counts on each machine (step 5) and which migration path applied.
- Confirm the token is stored only in the two client env blocks (not committed).

Security invariants (do not relax): token required on the server; TLS in front;
one server instance per shared state file; never commit the token.
```
