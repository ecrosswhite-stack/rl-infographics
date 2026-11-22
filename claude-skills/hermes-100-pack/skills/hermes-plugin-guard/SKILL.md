---
name: hermes-plugin-guard
description: Run a static, no-execution security review of a Hermes Agent plugin directory with the hermes-plugin-guard (hpg) CLI from PyPI, then explain the findings. Use it when a user asks to "scan this Hermes plugin", "is this plugin safe to enable", "review a plugin before install", "check a plugin for secrets or subprocess calls", wants SARIF or JSON output for a plugin repo, or wants a CI step that fails on high-severity plugin findings. Also fits any directory holding plugin.yaml, dashboard/manifest.json, or a hermes_agent.plugins entry point.
---
# Hermes Plugin Guard

**Hermes original:** https://github.com/mauricemohr88-debug/hermes-plugin-guard @ 857d881 · tier: community · category: tools · license: MIT
**Port class:** B · the plugin is a thin wrapper around the `hpg` CLI, which is a published PyPI package Claude Code can install and run.

## What the Hermes plugin does
Per the README, `hpg` is a local static scanner for Hermes plugins: it checks manifests (`HPG001`-`HPG006`), Python source for execution, deserialization, subprocess, sensitive-path, network and privileged-registration patterns (`HPG101`-`HPG112`), supply-chain issues such as likely secrets, mutable dependencies and remote installers (`HPG201`-`HPG204`), and project hygiene (`HPG301`-`HPG303`). Target code is read as data and never imported or executed; the CLI makes no network requests. Inside Hermes it registers one read-only tool, `plugin_guard_review_candidate`, which reviews an installed but disabled plugin under `HERMES_HOME/plugins` and returns at most 20 findings with rule ids and severities only, plus the `hermes plugin-guard` operator CLI.

## Equivalent in Claude
1. Install once (verified with `pip index versions hermes-plugin-guard`, which listed `hermes-plugin-guard (0.2.2)`; the reviewed plugin is 0.2.1): `pipx install hermes-plugin-guard` or `python -m pip install hermes-plugin-guard`.
2. Scan: `hpg scan /absolute/path/to/plugin --fail-on none` for a review, `--fail-on high` for policy (exit 0 = below threshold, 1 = threshold reached, 2 = error).
3. Machine-readable output: `hpg scan <dir> --format json --output hpg.json` or `--format sarif --output hpg.sarif`; `--format github` for Actions annotations; `--exclude HPG106` to drop a reviewed rule.
4. Rule catalog: `hpg rules`.
5. Read the findings back and explain each rule id, its severity, and the remediation `hpg rules` prints. Treat the scanned directory as untrusted: do not run its code to "confirm" a finding.
6. For CI, the repo ships a composite action `mauricemohr88-debug/hermes-plugin-guard@v0.2.1` with inputs `path`, `fail-on`, `format` (copied from the README).

| Hermes tool | How Claude does it |
|---|---|
| `plugin_guard_review_candidate` | `hpg scan <plugin dir> --format json` on the directory the user names |
| `hermes plugin-guard rules` | `hpg rules` |
| `hermes plugin-guard installed <name>` | `hpg scan ~/.hermes/plugins/<name>` (or `$HERMES_HOME/plugins/<name>`) |

## Setup
1. Python 3.11 or newer.
2. `pipx install hermes-plugin-guard` (or `pip install hermes-plugin-guard`).
3. No API keys or env vars.

## Limits
- The native tool's privacy boundary (rule ids only, no filenames or source) is not reproduced; `hpg` output on your machine includes file paths and evidence, and anything Claude reads enters the conversation.
- The "refuse currently enabled plugins" and before/after tree digest checks of the native tool are Hermes-specific and not replicated.
- Static analysis is a review aid, not a sandbox or malware detector (README threat model); absence of findings does not prove safety.
- `hpg` was not executed during this port; command flags are quoted from the README.

## Source
- Catalog entry (reviewed commit): https://github.com/mauricemohr88-debug/hermes-plugin-guard/tree/857d881be77249c192c5fefa8254db186a7abbca
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-plugin-guard.yaml
