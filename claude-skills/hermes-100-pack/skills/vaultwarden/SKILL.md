---
name: vaultwarden
description: Pull environment variables out of a Vaultwarden or Bitwarden Password Manager vault item's custom fields using the bw CLI, replicating the Hermes vaultwarden secret-source plugin. Use it when the user says "load my API keys from Vaultwarden", "export the fields of my 'hermes-secrets' vault item as env vars", "unlock Bitwarden and get BW_SESSION", "sync the vault and show which env vars would be set", "my self-hosted Vaultwarden does not work with bws", or wants secrets kept in Bitwarden rather than a .env file. Uses the same BW_SESSION convention and bw commands as the plugin. Read-only against the vault.
---
# Vaultwarden / Bitwarden secret source

**Hermes original:** https://github.com/hansipie/hermes-vaultwarden @ a461ecf · tier: community · category: general · license: no LICENSE file found
**Port class:** B · the plugin shells out to the `bw` CLI (`bw get item`) and maps JSON fields to env vars; Claude can run the same commands.

## What the Hermes plugin does
Registers a bulk `SecretSource` named `vaultwarden` and the CLI tree `hermes vaultwarden setup|status|sync|disable`; no agent tools. At startup it reads the session token from the env var named by `secrets.vaultwarden.session_env` (default `BW_SESSION`), runs `bw get item -- "<item_name>"` with `BW_SESSION` passed in the child environment (never on argv), and offers every custom field whose name is a valid env-var identifier as an environment variable. `login.username`, `login.password` and `notes` are exported only when `username_env` / `password_env` / `notes_env` are configured. Results are cached (default 300 s) in memory and in `~/.hermes/cache/vaultwarden_cache.json` keyed on a session fingerprint. The session env var is protected from being overwritten. Failures never block startup. `bw` is not auto-installed; `BITWARDENCLI_APPDATA_DIR` is passed through when set.

## Equivalent in Claude
Commands below are the ones the plugin and its README run.

1. Point the CLI at the server and log in once: `bw config server https://your-vaultwarden.example.com` then `bw login`.
2. Unlock and hold the session token in the same variable the plugin uses: `export BW_SESSION=$(bw unlock --raw)`. Ask the user to run this themselves; Claude must not see the master password.
3. Optional refresh: `bw sync` (the plugin's `sync` command runs this first).
4. Fetch the item as JSON: `bw get item -- "<item_name>"` (the `--` keeps odd item names from parsing as flags). Resolve `bw` from `binary_path`, `~/.hermes/bin/bw`, then PATH, in that order.
5. Map fields with `python3 -I`: for each entry in `.fields[]` take `name` and `value`; keep only names matching `^[A-Za-z_][A-Za-z0-9_]*$`; warn and skip others. If the user configured `username_env` / `password_env` / `notes_env`, add `.login.username`, `.login.password`, `.notes` under those names (they win over a same-named custom field, with a warning). Never let a field overwrite `BW_SESSION`.
6. Write `export NAME='value'` lines to a 0600 file and tell the user to `source` it; do not print values. For a dry run (plugin `sync` without `--apply`) print only the names and whether each would be new or would override an existing variable (`override_existing` default false).

| Hermes command / source | How Claude does it |
|---|---|
| `hermes vaultwarden status` | `command -v bw`, `bw status` (server URL, login state), check `BW_SESSION` is set (do not print it) |
| `hermes vaultwarden sync` | steps 3-5, table of names only |
| `hermes vaultwarden sync --apply` | step 6 |
| `hermes vaultwarden setup` | `bw list items` to let the user pick `item_name`; record `item_name` and optional bindings in a config file the user owns |
| secret source at startup | not replicated; run step 6 before launching the process that needs the vars |
| `hermes vaultwarden disable` | delete the generated env file and cache |

## Setup
1. Install the Bitwarden CLI: `npm install -g @bitwarden/cli` (verified on npm: `@bitwarden/cli` 2026.11.0, "A secure and free password manager for all of your devices."), or snap / native binary from https://bitwarden.com/help/cli/.
2. Create one vault item whose custom fields are named after the env vars to set (e.g. `OPENROUTER_API_KEY`).
3. `bw config server <url>`, `bw login`, `export BW_SESSION=$(bw unlock --raw)`.
4. Optional: `export BITWARDENCLI_APPDATA_DIR=...` if bw data lives in a custom location.

## Limits
- No automatic injection into a running agent; Claude produces an env file for the user to source.
- The 300 s two-layer cache and session fingerprinting are not replicated; every run calls `bw`.
- `BW_SESSION` expires when the vault locks; the user must re-run `bw unlock --raw`.
- Vault contents are secrets: Claude keeps values out of chat, logs and shell history, and asks before overwriting existing env vars.
- No LICENSE file at the reviewed commit, so no upstream text is copied; the commands above are restated facts from `vw_source.py`, `vw_cli.py` and the README.
- No upstream skills/ directory exists.

## Source
- Catalog entry (reviewed commit): https://github.com/hansipie/hermes-vaultwarden/tree/a461ecf127299a701404233cec8f097ac0450225
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/vaultwarden.yaml
