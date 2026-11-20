---
name: hermes-ssh
description: Reference card for the Hermes SSH plugin, a Hermes Desktop UI page ("Connections") that saves SSH machines and opens remote Hermes workspaces. Not a working skill. Read it only when someone asks what hermes-ssh did, how it compares to Claude, or how to reach a remote machine from Claude instead (answer: run ssh in Claude Code's shell).
---
# Hermes SSH (reference card)

**Hermes original:** https://github.com/Adolanium/hermes-ssh @ 02c6b34 · tier: community · category: desktop · license: no LICENSE file found
**Port class:** D — a Hermes Desktop renderer plugin (`desktop/plugin.js`) with no agent tools, hooks or middleware; it drives Desktop gateway methods (`shell.exec`, `profiles.create`, `cli.exec`) that have no Claude counterpart.

## What the Hermes plugin does
Adds a "Connections" page and a `/ssh <machine>` command to Hermes Desktop. The user saves a machine (host, user, port, key path, remote folder), tests access, and opens a workspace; Hermes then creates a new profile and task whose terminal and file tools run on the remote machine through the stock Hermes SSH backend. Supports existing keys, the SSH agent, or generating an Ed25519 key; interactive passwords are not supported. The catalog package (`catalog/`) registers nothing on the agent side (`provides_tools: []`).

## Equivalent in Claude
No direct equivalent: Claude has no plugin surface for adding Desktop pages or profile routing. In Claude Code, run SSH yourself from the shell (`ssh -p <port> user@host '<command>'`, `scp`, `rsync`) with keys the user already has; prompt the user before accepting unknown host keys.

## Setup
None.

## Limits
- No saved-machine registry, no "Connections" UI, no `/ssh` command.
- No remote workspace: Claude's file tools stay local; remote work goes through explicit ssh/scp commands.
- The plugin's skill/credential synchronization to the remote host is not replicated and would be a data-exposure concern anyway.
- No LICENSE file in the repository, so no upstream text is copied.

## Source
- Catalog entry (reviewed commit): https://github.com/Adolanium/hermes-ssh/tree/02c6b34ee604a30827df25a082cba03fbf6fdf17/catalog
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-ssh.yaml
