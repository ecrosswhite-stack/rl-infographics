---
name: hermes-tailscale
description: "Browse and act on the local Tailscale tailnet from Claude Code using the installed tailscale CLI, matching what the Hermes Tailscale desktop plugin did: list devices with OS, IPv4 and online state, ping a peer, produce an ssh line, send a file with Taildrop, pick an exit node, switch accounts, or publish a local port to the tailnet with tailscale serve. Use it when a user says \"which of my tailnet machines are online\", \"tailscale status\", \"ssh into my Pi over tailscale\", \"send this file to my laptop with taildrop\", \"set an exit node\", or \"expose port 9119 on the tailnet\". The Hermes Desktop sidebar page itself is not reproduced."
---
# Hermes Tailscale

**Hermes original:** https://github.com/Adolanium/hermes-tailscale @ 6dad1d5 · tier: community · category: desktop · license: MIT
**Port class:** C · every action shells out to the Tailscale CLI, which Claude Code can run, but the plugin is a Hermes Desktop sidebar page (renderer `plugin.js`) with no agent tools, so the UI half has no counterpart.

## What the Hermes plugin does
Per the README and `catalog/plugin.yaml`, it adds a "Tailscale" page to Hermes Desktop (`provides_tools: []`, `provides_hooks: []`). The page polls `tailscale status --json` (cached to `status-cache.json` next to the plugin), lists peers with name, OS, IPv4 and status, copies IPs or MagicDNS names, pings peers, opens SSH in an in-app xterm, sends files with Taildrop (`tailscale file cp`), picks an exit node, switches accounts (`tailscale switch --list --json`), and publishes the local Hermes port with `tailscale serve --bg --yes <port>` after checking something listens on `127.0.0.1:<port>`. It never calls the Tailscale cloud API and stores no token; mutating actions ask for confirmation first and Funnel stays off.

## Equivalent in Claude
Run the CLI in Bash on the machine that is on the tailnet. Binary locations the plugin probes: `tailscale` on PATH, `/usr/local/bin/tailscale`, `/opt/homebrew/bin/tailscale`, `/Applications/Tailscale.app/Contents/MacOS/Tailscale` (with `TAILSCALE_BE_CLI=1`), `/usr/bin/tailscale`, `/snap/bin/tailscale`, `C:\Program Files\Tailscale\tailscale.exe`.

| Hermes page action | How Claude does it |
|---|---|
| Roster, online count | `tailscale status --json`; parse `Self` and `Peer` entries (DNSName, OS, TailscaleIPs, Online, LastSeen); hide shared or tagged nodes unless asked |
| Version check | `tailscale version --json` |
| Copy IP / MagicDNS / ssh line | Print the IPv4 or DNSName; ssh line is `tailscale ssh <host>` when the peer advertises SSH host keys, otherwise `ssh <user>@<host>` with a user the person supplies |
| Ping | `tailscale ping <host-or-ip>` |
| Taildrop send | `tailscale file cp <path> <host>:` (confirm first) |
| Exit node | `tailscale set --exit-node=<name>` to set, `--exit-node=` to clear (confirm first) |
| Account switch | `tailscale switch --list --json`, then `tailscale switch <account>` (confirm first) |
| Publish Hermes | check a listener on `127.0.0.1:<port>` with `curl`, then `tailscale serve --bg --yes <port>`; inspect with `tailscale serve status --json` |
| Client down | tell the user to run `tailscale up` |

Ask before any write (serve, exit node, switch, file send), exactly as the page does. Never enable Funnel.

## Setup
1. Install the Tailscale client and log in on the machine running Claude Code (`tailscale up`).
2. `tailscale serve --bg` needs Tailscale 1.48 or newer (README).
3. No API key or env vars; the plugin declares `requires_env: []`.

## Limits
- No sidebar page, polling, status bar count, in-app xterm SSH overlay, or Taildrop progress bar; Claude runs one-off commands.
- SSH sessions are interactive; Claude can print the ssh line but should not hold an interactive PTY open.
- The exact `tailscale set --exit-node` and `tailscale switch <account>` forms are inferred from the `--exit-node=` flag string and `switch --list --json` call in `plugin.js`; verify with `tailscale --help` on the user's version.
- Cowork or cloud sessions are not on the user's tailnet; use Claude Code locally.
- Commands were not executed during this port.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-tailscale/tree/6dad1d5aac443a196f7ba83736a1f4c9e3a75048/catalog
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-tailscale.yaml
