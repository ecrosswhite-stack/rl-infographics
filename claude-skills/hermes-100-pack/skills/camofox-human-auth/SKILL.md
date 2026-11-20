---
name: camofox-human-auth
description: Human-in-the-loop browser authentication workflow, ported from the Hermes camofox-human-auth plugin. Use it whenever a browsing or automation task reaches a login, registration, SSO or OAuth consent, MFA or 2FA, OTP, CAPTCHA, device-approval, or email/phone verification page, or when the user says "log me in", "I need to sign in first", "open it headed", "handle the captcha", "reuse my saved session", or "the site wants a code". It tells Claude how to hand the browser to the user, never collect secrets in chat, and verify the signed-in state before continuing. It also documents the Camofox Browser HTTP endpoints the plugin called, for users who already run that backend.
---
# Camofox Human Auth

**Hermes original:** https://github.com/tim-toothed/hermes-camofox-human-auth @ 19946d2 · tier: community · category: web · license: no LICENSE file found
**Port class:** C — the handoff procedure works with any Claude browser tool, but the three tools drive a Camofox Browser backend (patched Camoufox server) that exists only where the plugin's installer set it up.

## What the Hermes plugin does
Opens a user-visible browser surface so the human, not the model, enters passwords, OTP and MFA codes, CAPTCHA answers and device approvals, then returns the browser to headless automation on the same persistent profile. It registers three tools: `camofox_backend_status` (GET health of the configured backend), `camofox_auth_open` (switch the native backend to a headed window, or return a noVNC URL for the Docker backend, and open the target URL in the persistent profile), and `camofox_auth_finish` (return to headless and reopen the URL). It also registers the Hermes CLI command `hermes camofox-human-auth setup|status` and a bundled `human-auth` skill with the handoff rules.

## Equivalent in Claude
Follow this procedure with whatever browser tool is available (Claude in Chrome, the browser-use MCP server, Playwright under Claude Code). The security rules are the portable part.

1. Browse public pages normally. The moment a login, consent, MFA, OTP, CAPTCHA or device-approval page appears, stop interacting with the form.
2. Tell the user to complete the step themselves in the visible browser window. Use the message: "Manual authentication is required. Enter your details directly in the open browser window. Do not send passwords, OTP codes or other secrets in chat. Say Done when finished." (The upstream skill phrases this in Russian with the word "Готово".)
3. Never request, repeat, store, type or log a password, OTP, MFA or recovery code, CAPTCHA answer, cookie, card PIN or private key. Never put one in a tool argument or URL. Do not inspect secret fields or export browser storage as a substitute for the handoff.
4. Wait for the user to say they are done. Do not poll the page while they type.
5. Take a fresh snapshot of the same tab. Authentication is verified only when a post-login marker is visible (dashboard, account name, avatar, logout control) and the challenge is gone. An HTTP 200 or a public landing page is not proof.
6. If the challenge is still there, repeat the handoff in the same tab and session. Never open a second profile or browser runtime to work around it.
7. Continue the original task in the same session.

If the user runs the plugin's Camofox backend, Claude Code can reproduce the three tools with HTTP calls per `__init__.py`:

| Hermes tool | How Claude does it |
|---|---|
| `camofox_backend_status` | `GET $BASE/health`; ready when the JSON has `ok: true` and `browserConnected: true` |
| `camofox_auth_open` (native) | `POST $BASE/admin/display-mode` with `{"mode":"headed"}`, then `POST $BASE/tabs` with `{"userId":"hermes","sessionKey":"native-auth","url":"<target>"}` |
| `camofox_auth_open` (docker) | `POST $BASE/tabs` with the same body; give the user `http://<host>:$CAMOFOX_NOVNC_PORT/vnc.html` (or `$CAMOFOX_NOVNC_PUBLIC_URL/vnc.html`) |
| `camofox_auth_finish` (native) | `POST $BASE/admin/display-mode` with `{"mode":"headless"}`, optionally `POST $BASE/tabs` again with the same ids |

`$BASE` is `CAMOFOX_HUMAN_AUTH_URL`, defaulting to `http://127.0.0.1:9377` for the native backend and `http://127.0.0.1:9378` when `CAMOFOX_HUMAN_AUTH_BACKEND=docker`. Requests use `Accept: application/json`, JSON bodies, and the header `x-admin-key` when `CAMOFOX_HUMAN_AUTH_ADMIN_KEY` is set. Default identifiers come from `CAMOFOX_HUMAN_AUTH_USER_ID` (default `hermes`) and `CAMOFOX_HUMAN_AUTH_SESSION_KEY` (default `native-auth`); keep them identical across open and finish. `CAMOFOX_PROFILE_DIR` names the persistent profile directory for diagnostics only.

## Setup
1. None for the generic handoff workflow; it uses the browser tool already configured in Claude.
2. Optional, only if you want the Camofox endpoints above: install Camofox Browser with this plugin's patches using the repository's `scripts/install.sh`, `scripts/install-native.sh` or `docker-compose.yml`, then export the `CAMOFOX_HUMAN_AUTH_*` variables listed above. The plugin's own setup command (`hermes camofox-human-auth setup`) is Hermes-only and is not reproduced.

## Limits
- Switching a running browser between headed and headless on the same profile (`/admin/display-mode`) is a feature of the plugin's patched Camofox server, not of stock Camoufox or of Claude's browser tools. With Claude in Chrome the window is always visible, so the handoff is simply "stop typing and let the user act".
- The Docker + noVNC surface requires the plugin's `docker-compose.yml` and a private network or VPN; nothing in Claude provides a remote screen.
- The Hermes CLI command and automatic backend restart on Windows (`scripts/start-native.ps1`) are not replicated.
- The upstream `skills/human-auth/SKILL.md` and `skills/camofox-vnc-auth/SKILL.md` were not copied because the repository has no LICENSE file; this card summarizes them instead.
- Not verified: the Camofox endpoints were read from the plugin source and not exercised here.

## Source
- Catalog entry (reviewed commit): https://github.com/tim-toothed/hermes-camofox-human-auth/tree/19946d2e664063ffc5259f85703d14e11b477512
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/camofox-human-auth.yaml
