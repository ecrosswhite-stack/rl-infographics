---
name: hermes-plugin-chrome-profiles
description: Launch or reach a specific Chrome or Microsoft Edge profile with remote debugging (CDP) enabled so browser automation can use that profile's cookies and logins, replicating the Hermes chrome-profiles plugin. Use it when the user says "open my work Chrome profile for automation", "start Chrome with remote debugging on port 9250 using this user-data-dir", "switch the browser tools to my personal profile", "connect to the Chrome running on my other machine", "list my browser profiles and which is reachable", or wants a logged-in Gmail/AWS console session available to a CDP-based tool. Covers local launch, remote reachability checks and the config.yaml profile format; wiring the endpoint into a Claude browser tool depends on that tool.
---
# Chrome/Edge Profiles via CDP

**Hermes original:** https://github.com/anpicasso/hermes-plugin-chrome-profiles @ 5b9c325 · tier: community · category: web · license: no LICENSE file found
**Port class:** C · launching browsers with `--remote-debugging-port` and probing `/json/version` is plain shell work; the part that redirected Hermes' built-in browser tools through `BROWSER_CDP_URL` is Hermes-specific.

## What the Hermes plugin does
Registers one tool, `browser_profile(name)` (toolset `chrome_profiles`). It reads `config.yaml` next to the plugin (re-read on every call), where each profile is `type: local|remote`, `port`, and for Chrome `data_dir`, for Edge `browser_type: edge` plus `profile_directory`, or for remote `host`. Local profiles are launched if CDP is not already answering; remote profiles are only checked for reachability. On success it sets `BROWSER_CDP_URL=http://<host>:<port>` in the Hermes process and flushes Hermes browser sessions so later `browser_navigate`, `browser_click`, `browser_snapshot` calls use that browser. Called with no name it lists profiles with `active` and `reachable` flags. Launched PIDs are terminated at exit.

## Equivalent in Claude
Commands below mirror `__init__.py`.

1. Keep the same `config.yaml` shape (example from the README):
   ```yaml
   profiles:
     work:     {type: local, port: 9250, data_dir: ~/.config/chrome-work}
     devsu:    {type: local, browser_type: edge, port: 9223, profile_directory: "Default"}
     remote-1: {type: remote, host: 192.168.1.100, port: 9250}
   ```
2. Check readiness exactly as the plugin does: `curl -s --max-time 2 http://127.0.0.1:$PORT/json/version` must return JSON containing `webSocketDebuggerUrl`. For remote profiles the plugin only checks that the TCP port is open (`nc -z $HOST $PORT` or `bash -c 'exec 3<>/dev/tcp/$HOST/$PORT'`); it never launches remotely.
3. Launch a local Chrome profile when CDP is not answering. Binary search order: profile `chrome_binary`, top-level `chrome_binary`, then PATH names `google-chrome`, `google-chrome-stable`, `google-chrome-beta`, `chromium-browser`, `chromium`.
   `setsid "$CHROME" --user-data-dir="$DATA_DIR" --remote-debugging-port=$PORT --no-first-run --no-default-browser-check >/dev/null 2>"$DATA_DIR/chrome-launch.log" &`
   Then poll step 2 every 0.5 s for `launch_timeout` seconds (default 10).
4. Launch a local Edge profile: PATH names `microsoft-edge`, `microsoft-edge-stable`, `edge`; flags `--profile-directory="$PROFILE_DIRECTORY" --remote-debugging-port=$PORT --no-first-run --no-default-browser-check`.
5. Report the result in the plugin's JSON shape: `{"success":true,"profile":"work","type":"local","cdp_url":"http://127.0.0.1:9250"}` or `{"error": "..."}`; for a listing, one entry per profile with `active`, `reachable`, `browser_type`.
6. Hand the `cdp_url` to whichever browser tool the user runs. `chrome-devtools-mcp` (npm, version 1.13.0, "MCP server for Chrome DevTools") documents connecting to a running Chrome instance instead of starting a new one in its Advanced Usage Guide; the flag name was not verified here, so read that guide before configuring it.

| Hermes tool call | How Claude does it |
|---|---|
| `browser_profile()` | parse config.yaml, probe each port (step 2), print table |
| `browser_profile(name="work")` | steps 2-3, then print `cdp_url` |
| `browser_profile(name="remote-1")` | TCP check only, print `cdp_url` or unreachable error |
| set `BROWSER_CDP_URL` | no effect on Claude tools; configure the browser MCP/CLI with the URL instead |

## Setup
1. Install Chrome or Edge locally; create separate data directories (Chrome) or know the Edge profile directory name.
2. Write `config.yaml` as above; keep ports distinct per profile (1-65535, validated by the plugin).
3. Optional: `npx chrome-devtools-mcp@1.13.0` (verified with `npm view chrome-devtools-mcp name version description`) and follow its guide for attaching to the launched instance.

## Limits
- Redirecting Hermes' native browser tools (`BROWSER_CDP_URL`, `cleanup_all_browsers`) is Hermes-only; Claude's browser tooling must be pointed at the CDP URL by its own configuration.
- Per-profile launch locks, PID tracking and atexit cleanup are not replicated; Claude should remember PIDs it started and ask before killing browsers.
- Exposing a remote debugging port grants full control of that logged-in browser; the plugin binds to 127.0.0.1 for local profiles and the user must secure remote hosts themselves.
- No LICENSE file at the reviewed commit, so no upstream text is copied; commands above are restated facts.

## Source
- Catalog entry (reviewed commit): https://github.com/anpicasso/hermes-plugin-chrome-profiles/tree/5b9c3257b464c0f926d4355149a8aed9c8f307b4
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-plugin-chrome-profiles.yaml
