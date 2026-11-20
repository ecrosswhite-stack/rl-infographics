---
name: metamask-wallet
description: Drive a MetaMask Agent Wallet from Claude Code through the `mm` CLI (npm package @metamask/agent-wallet) with `--json` output, the same commands the Hermes metamask-wallet plugin wraps. Use when the user asks to "set up my MetaMask agent wallet", "what's my wallet address/balance", "price of ETH", "show my transactions", "quote a swap", "send N USDC to 0x... on Base", "sign this message", "what's pending 2FA", "raise my outflow limit / allowlist an address", or mentions MetaMask, mm CLI, Guard Mode. Every fund-moving or signing command needs explicit user confirmation first.
---
# MetaMask Agent Wallet (mm CLI)

**Hermes original:** https://github.com/akugone/hermes-metamask-wallet @ b56d6bb · tier: community · category: tools · license: MIT
**Port class:** B — every tool is a subprocess call to `mm <args> --json`; Claude Code can run the same CLI, with its own permission prompt standing in for the Hermes approval gate.

## What the Hermes plugin does
Registers `mm_status`, `mm_setup`, `mm_balance`, `mm_market`, `mm_history`, `mm_swap_quote`, `mm_transfer`, `mm_swap_execute`, `mm_sign`, `mm_requests`, `mm_policy`, a `/wallet` slash command and a bundled skill. A `pre_tool_call` hook escalates transfers, swaps, signatures, policy changes and sensitive setup steps to Hermes's human-approval prompt (fail-closed without a human) and flags direct `mm` write commands typed into the terminal as bypass attempts; a `post_tool_call` hook starts a watcher for requests stuck in `AWAITING_MFA`. Keys stay in MetaMask (server-wallet TEE or BYOK via `MM_MNEMONIC`).

## Equivalent in Claude
CLI: `mm` from `@metamask/agent-wallet`. Verified with `npm view @metamask/agent-wallet name version description`: name `@metamask/agent-wallet`, version `8.0.0`, "Command-line MetaMask wallet (mm) for agents and scripts". The plugin pins major 6 (`npm install -g @metamask/agent-wallet@6`); newer majors are not tested by the plugin.
Env vars (same names, per the plugin source): `MM_CLI_TOKEN` (sign-in token, never on argv), `MM_MNEMONIC` (BYOK only), `MM_PASSWORD`. Always append `--json`; `mm` may emit NDJSON `{"_notice": ...}` lines before the final envelope. Pass free text as `--flag=value`.

| Hermes tool | mm commands (from the plugin README) |
|---|---|
| `mm_status` | `mm doctor`, `mm init show`, `mm wallet address`, `mm wallet trading-mode get`, `mm wallet policy get` |
| `mm_setup` | `npm i -g @metamask/agent-wallet@6`, `mm login browser --no-wait`, `mm login` (token via `MM_CLI_TOKEN`), `mm init`, `mm wallet create`, `mm logout` |
| `mm_balance` | `mm wallet balance` (`--testnet` probe when mainnets are empty) |
| `mm_market` | `mm price spot`, `mm token list search|trending|popular`, `mm chains list` |
| `mm_history` | `mm tx history`, `mm tx`, `mm decode` |
| `mm_swap_quote` | `mm swap quote --all-quotes` (compare only) |
| `mm_requests` | `mm wallet requests list|watch` |
| `mm_transfer` | `mm transfer`; with explicit fees `mm wallet send-transaction` (EIP-1559 payload) |
| `mm_swap_execute` | `mm swap execute` by quoteId |
| `mm_sign` | `mm wallet sign-message`, `mm wallet sign-typed-data` |
| `mm_policy` | `mm wallet policy get|template`, `mm wallet policy set --policy <yaml> --no-wait` |

Procedure (mirrors the bundled skill, copied in `references/`):
1. Start with the status commands; follow what is missing (CLI, sign-in, wallet).
2. Reads (balance, market, history, quote, requests, policy get) run freely.
3. Writes (transfer, swap execute, sign, policy set, beast/BYOK/logout setup): restate recipient, amount, token, chain id (1 Ethereum, 8453 Base, 42161 Arbitrum, 10 Optimism, 137 Polygon) in plain words, get an explicit yes, then run once. Never retry a write on your own; after `TX_FAILED`/`rpc_fee_too_low` ask before one retry with explicit fees.
4. `AWAITING_MFA` with a pollingId: tell the user to approve on MetaMask Mobile or e-mail; check with `mm wallet requests watch`.
5. Never ask for or echo a seed phrase or CLI token in chat; never recommend Beast mode or removing the outflow limit to avoid 2FA.

## Setup
1. Node.js 22.18+ and `npm install -g @metamask/agent-wallet@6` (confirm with the user first).
2. `mm login browser --no-wait`, open the link, then `MM_CLI_TOKEN=<token> mm login --json`.
3. `mm init` (server-wallet + guard recommended) and `mm wallet create`.
4. Configure Guard Mode: `mm wallet policy set` with an outflow limit and allowlist (one MetaMask 2FA).

## Limits
- The Hermes approval gate, "always approve this exact intent" rules, shell-bypass detection and the background MFA watcher are not replicated; Claude Code's Bash permission prompt plus explicit user confirmation replace them. Do not run writes in unattended/auto-approve modes.
- `/wallet` status card and plugin settings (`default_chain_id`, `default_currency`, `command_timeout`) become explicit flags per command.
- These commands move real funds and sign on-chain data; MetaMask policy and Blockaid checks apply server-side. Command names were taken from the README for `mm` major 6 and are not verified against `mm` 8.0.0.

## Source
- Catalog entry (reviewed commit): https://github.com/akugone/hermes-metamask-wallet/tree/b56d6bbf575391d172280016abf778d31c5ca8bd
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/metamask-wallet.yaml
