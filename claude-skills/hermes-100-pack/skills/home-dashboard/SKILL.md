---
name: home-dashboard
description: Reference card for the Hermes "home-dashboard" plugin, a customizable Home page of draggable glass widgets (clock, calendar, tokens, host stats, sessions, cron, logs, notes, pomodoro and more) for the Hermes web dashboard and Hermes Desktop. Use it only when someone asks what this plugin is or whether Claude has a similar home screen. It adds no UI to Claude and should not trigger on dashboard-building requests about the user's own data.
---
# Hermes Home Dashboard (reference card)

**Hermes original:** https://github.com/albertocvrrbs/hermes-home-dashboard @ a8a0182 · tier: community · category: desktop · license: MIT
**Port class:** D · it is a React bundle rendered inside the Hermes web dashboard and Hermes Desktop, fed by Hermes host APIs; Claude has no renderer-plugin surface or equivalent host data.

## What the Hermes plugin does
Adds a `Home` tab (web, via `dashboard/manifest.json` and `window.__HERMES_PLUGINS__`) and a native Desktop page, sidebar entry and command-palette action (via `@hermes/plugin-sdk`). It renders a free 12-column grid of 16 widgets (Clock, Calendar, Moon, Tokens, Host, Gateway, Sessions, Cron, Logs, Notes, Pomodoro, Countdown, Ascii, Matrix, Heartbeat, Life) with drag, resize, auto-swap and hover controls. Widget data comes from the Hermes host API (status, system, analytics, sessions, cron, logs). A FastAPI router (`dashboard/plugin_api.py`, mounted at `/api/plugins/home-dashboard/`) persists the layout to `~/.hermes/plugins/home-dashboard/layout.json` and exposes read-only `/system`, `/analytics`, `/cron`, `/sessions` adapters for Desktop. It registers no agent tools, commands or hooks.

## Equivalent in Claude
None identified. The widgets display Hermes-internal state (token usage, gateway health, Hermes cron jobs, Hermes sessions and logs) that Claude does not have.

## Setup
None.

## Limits
- No Home tab, widget grid or layout persistence in Claude.
- Widget data sources are Hermes host endpoints; there is nothing equivalent to poll.
- The Desktop installer (`scripts/install-desktop.mjs`) links into `desktop-plugins/`, a Hermes Desktop concept.

## Source
- Catalog entry (reviewed commit): https://github.com/albertocvrrbs/hermes-home-dashboard/tree/a8a018225d8ecd21b281788131775adeade4c577
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/home-dashboard.yaml
