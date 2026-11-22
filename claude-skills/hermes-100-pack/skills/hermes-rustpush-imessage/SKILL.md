---
name: hermes-rustpush-imessage
description: Reference card for the Hermes "hermes-rustpush-imessage" platform plugin, a local-only iMessage gateway adapter backed by a launchd-supervised OpenBubbles RustPush sidecar on macOS. Use it only when someone asks what this plugin is, whether Claude can send or receive iMessages the same way, or how Hermes chat-platform adapters relate to Claude. It does not give Claude iMessage access.
---
# Local iMessage via RustPush (reference card)

**Hermes original:** https://github.com/boobutler/hermes-rustpush-imessage @ 695f747 · tier: community · category: platform · license: MIT (adapter code; bundled patches are MPL-2.0 and SSPL-1.0)
**Port class:** D · it is a Hermes gateway platform adapter (`kind: platform`) that feeds inbound chats into the Hermes gateway; Claude has no gateway or platform-adapter slot.

## What the Hermes plugin does
Registers the Hermes platform `imessage_cli` (label "Local iMessage (RustPush)"). A Python sidecar (`ai.hermes.rustpush-sidecar`, supervised by launchd) wraps a locally built, pinned OpenBubbles RustPush library through a UniFFI binding and talks to Apple's iMessage service directly over APNs/IDS. The Hermes adapter speaks newline-delimited JSON to the sidecar over a same-user mode-0600 Unix socket (`~/.hermes/rustpush/run/bridge.sock`). Supported surface per the README: inbound/outbound messages, typing and read receipts, tapbacks, replies, edits, undo-send, attachments, and group create/rename/participant changes. It does not control Messages.app, use Accessibility automation, or relay through a third party. Optional env vars: `RUSTPUSH_ALLOWED_USERS`, `RUSTPUSH_ALLOW_ALL_USERS`. Apple credentials are read only from `/dev/tty` during `scripts/local_account_setup.py`.

## Equivalent in Claude
None identified in the Claude product itself. A Claude plugin named `imessage` (skills `imessage:access`, `imessage:configure`) appeared in the plugin listing of the environment used for this port; it is a different implementation and was not evaluated here, so do not assume parity.

## Setup
None.

## Limits
- No inbound message routing: Claude cannot run as a chat-platform gateway.
- The runtime requires macOS 12+, Xcode CLT, Rust/Cargo, `protoc`, a locally compiled RustPush build pinned in `pins.env`, an Apple ID eligible for iMessage, and Apple Contact Key Verification disabled; none of this is portable.
- Uses Apple's private iMessage protocols; the README warns Apple can change or restrict them and that sign-in may trigger account/device notifications.
- Redistributing a built runtime brings in SSPL-1.0 (RustPush) and MPL-2.0 (Corten wrapper) obligations; only the adapter code is MIT.

## Source
- Catalog entry (reviewed commit): https://github.com/boobutler/hermes-rustpush-imessage/tree/695f74755cbcdbcd742baa51021fdb96a78ac10e
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-rustpush-imessage.yaml
