---
name: herdr-auto-reconcile
description: Reference card only. Describes the retired Hermes community plugin herdr-auto-reconcile, which woke a Hermes agent when allowlisted "Herdr panes" needed reconciliation. It has no Claude equivalent and its source is no longer public, so this skill exists to answer "what was herdr-auto-reconcile", "can Claude do what the Herdr reconcile plugin did", or to explain why the port was not possible. Do not trigger on real automation or reconciliation work; nothing here runs anything.
---
# Herdr Auto Reconcile (reference card)

**Hermes original:** https://github.com/chris-yyau/hermes-herdr-auto-reconcile @ 7a01878 · tier: community · category: automation · license: no LICENSE file found (source not available to check)
**Port class:** D — a Hermes wake-up automation tied to an external "Herdr" pane system; no source could be read and no Claude-native hook exists for it.

## What the Hermes plugin does
Per the catalog row only: "Wake Hermes when allowlisted Herdr panes need reconciliation, without routing or controlling pane work." The catalog lists no tools, hooks or required env vars, and marks the plugin as no longer in the catalog (`still_in_catalog: false`). What "Herdr" is, how panes were detected, and how the wake was delivered are not verified; the checkout directory for this plugin is empty.

Source repository no longer public at 2026-11-20 (checked: the local checkout directory is empty; a direct GitHub fetch from this session was blocked by network policy, so the "not public" status comes from the porting task notes and could not be independently confirmed).

## Equivalent in Claude
None. Claude cannot be woken by an external pane state it has no access to, and the plugin's own mechanism is unknown. Nearest Claude-native feature: none identified. (Claude Code Remote offers scheduled tasks and inbound webhooks that can wake a session, but mapping them to "Herdr pane reconciliation" would require the missing source; treat as not verified.)

## Setup
None.

## Limits
- Entire plugin not replicated: no source, no API, no documented protocol.
- Catalog description is the only fact available; anything beyond it would be invention.
- If the user has a private copy of the repository, re-run this port with the source present before relying on any claim here.

## Source
- Catalog entry (reviewed commit): https://github.com/chris-yyau/hermes-herdr-auto-reconcile/tree/7a01878039c217f7b3a5500a3086dd62a077d100
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/herdr-auto-reconcile.yaml
