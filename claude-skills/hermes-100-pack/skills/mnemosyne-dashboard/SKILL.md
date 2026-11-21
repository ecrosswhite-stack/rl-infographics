---
name: mnemosyne-dashboard
description: Start, stop, check and configure the Mnemosyne Dashboard, a stdlib-only Python web UI for browsing a Mnemosyne memory SQLite database (memories, triples, stats, consolidation history), by running its server.py from Claude Code. Use when the user has a Mnemosyne memory store (usually ~/.hermes/mnemosyne/data/mnemosyne.db) and asks to "open the memory dashboard", "start/stop the mnemosyne dashboard", "is the dashboard running", "change the dashboard port / db path", or wants to browse Mnemosyne memories in a browser.
---
# Mnemosyne Dashboard

**Hermes original:** https://github.com/wysie/mnemosyne-dashboard @ a918e5e · tier: community · category: desktop · license: MIT
**Port class:** C · the four tools only manage a local `server.py` process, which Claude can run; the data it shows comes from the Hermes Mnemosyne memory plugin, which this pack does not provide.

## What the Hermes plugin does
Registers `mnemosyne_dashboard_start`, `mnemosyne_dashboard_stop`, `mnemosyne_dashboard_status`, `mnemosyne_dashboard_config` (no hooks). Start launches `python server.py --host H --port P --db PATH` detached, records pid and runtime JSON under `~/.hermes/plugin-data/mnemosyne-dashboard/`, and waits for `/api/auth/status` to answer. The server (ThreadingHTTPServer, no external JS) opens the SQLite DB read-only, serves overview, Today digest, Context Bank, Constellation/Neural Map visualisers, search, timeline, graph/triples, consolidations, and optional password-gated maintenance (supersede, expire, importance) with backups and an `audit.jsonl`.

## Equivalent in Claude
1. Get the code (read-only clone, do not execute anything you have not read):
   `git clone https://github.com/wysie/mnemosyne-dashboard ~/.hermes/plugins/mnemosyne-dashboard` (or any directory).
2. Locate the DB: `~/.hermes/mnemosyne/data/mnemosyne.db`, or `MNEMOSYNE_DASHBOARD_DB` / `MNEMOSYNE_DB_PATH` / `MNEMOSYNE_DB` if set.
3. Start (bind to localhost unless the user wants LAN access; the plugin default is `0.0.0.0`):
   ```bash
   cd <checkout> && nohup python3 server.py --host 127.0.0.1 --port 8765 --db ~/.hermes/mnemosyne/data/mnemosyne.db > dashboard.log 2>&1 &
   echo $! > dashboard.pid
   ```
4. Status: `curl -fsS http://127.0.0.1:8765/api/health` (also `/api/auth/status`, `/api/diagnostics`). Running listener: `lsof -nP -iTCP:8765 -sTCP:LISTEN`.
5. Stop: `kill $(cat dashboard.pid)` (the plugin sends SIGTERM to the recorded pid).
6. Config: edit `~/.hermes/plugin-data/mnemosyne-dashboard/config.json` (`host`, `port`, `db_path`, `auth_enabled`, `memory_admin_enabled`) or set `MNEMOSYNE_DASHBOARD_HOST`, `MNEMOSYNE_DASHBOARD_PORT`, `MNEMOSYNE_DASHBOARD_DB`, `MNEMOSYNE_DASHBOARD_AUTH_ENABLED`, `MNEMOSYNE_DASHBOARD_CONFIG`; restart the process for host/port/db changes.
7. Open `http://127.0.0.1:8765/` for the user.

| Hermes tool | How Claude does it |
|---|---|
| `mnemosyne_dashboard_start` | Step 3 |
| `mnemosyne_dashboard_status` | Step 4 |
| `mnemosyne_dashboard_stop` | Step 5 |
| `mnemosyne_dashboard_config` | Step 6 |

## Setup
1. Python 3.11+ (stdlib only, per the plugin).
2. A Mnemosyne SQLite database produced by the Hermes Mnemosyne memory plugin.
3. Clone the repository as in step 1.

## Limits
- Without a Mnemosyne DB there is nothing to show; this pack does not port the Mnemosyne memory provider itself.
- The plugin's pid/runtime bookkeeping in `plugin-data` is replaced by a simple pid file.
- Binding to `0.0.0.0` exposes memory metadata to the LAN; enable password auth in Settings before doing so. Admin (maintenance) mode mutates the DB; leave it off unless asked.
- The macOS launchd helper script is not covered here.

## Source
- Catalog entry (reviewed commit): https://github.com/wysie/mnemosyne-dashboard/tree/a918e5e0841fdc85baad7ab582432b2b7499b2f2
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/mnemosyne-dashboard.yaml
