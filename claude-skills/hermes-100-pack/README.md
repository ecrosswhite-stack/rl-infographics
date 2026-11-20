# Hermes 100 → Claude Skills Pack

One Claude skill per plugin from the **Hermes Agent Plugin Catalog as it stood at launch**
(100 entries: 4 official, 96 community), ported for the Claude desktop app, Cowork and Claude Code.

## Provenance (verified)

| Fact | Evidence |
|---|---|
| The "100 free plugins" set | Nous Research announced the Hermes Plugin Catalog "starting with 4 official plugins and 96 from the community" (post on X, 2026-09-16 16:51 UTC). |
| Exact membership | `hermes-agent` commit `bb0c2303664edc01960fdbbb148b47acdbe553ce` (2026-09-16, the last catalog change before that post) contains exactly 100 catalog entries: 96 `tier: community`, 4 `tier: official`. Stored in `data/launch_catalog_bb0c2303.json`. |
| Per-plugin source | Each plugin was fetched at the exact commit SHA pinned in its catalog entry and classified (`data/plugins_classified.json`). 98 of 100 fetched; `herdr-auto-reconcile` and `web-oxylabs` repositories are no longer publicly readable (checked 2026-11-20). |
| Still listed today | 93 of the 100 remain in the catalog at `hermes-agent` main (2026-11-17). Dropped: clawchat, grill-tab, herdr-auto-reconcile, hermes-evolve, self-wake, voice-call-timeout, web-oxylabs. |

The Instagram carousel that prompted this pack could not be read slide by slide (login wall); its caption
names the "100 FREE plugins" for Hermes Agent, and the catalog launch set above is the only 100-plugin
set published by the project. If the carousel used a different selection, the diff is unknown.

## What "replicated" means here

Hermes plugins are Python code that runs inside the Hermes Agent runtime. Claude cannot load them.
Each skill in `skills/<name>/SKILL.md` therefore records a **port class**:

| Class | Meaning | What you get |
|---|---|---|
| **A** Direct port | Portable package (MCP server + skills) | MCP config snippet for Claude Desktop + adapted skill |
| **B** Re-implementable | Wraps a public API / CLI / file format | Skill that has Claude call the same API with the same env vars |
| **C** Partial | Some behaviour reproducible, core needs Hermes runtime | Skill for the reproducible part, explicit limits |
| **D** Not portable | Hermes Desktop UI, chat-gateway adapter, memory/model provider | Reference card only (does not trigger on real work) |

`data/port_status.jsonl` holds one row per plugin with class, env vars, verified packages and a
confidence level. `index.html` renders the same data.

## Install

### Claude desktop app (claude.ai desktop) and claude.ai
Skills are uploaded one at a time as a ZIP whose root is the skill folder containing `SKILL.md`.
`dist/skill-zips/<name>.zip` is already in that shape.
1. Open Settings → Capabilities, make sure code execution is on.
2. Open the Skills section (in newer builds: sidebar → Customize → Skills), choose add/upload, pick the ZIP.
3. Confirm the skill appears and is toggled on. Menu labels change between app versions; the official
   help centre is the authority: https://support.claude.com

### Claude Code (terminal, desktop app, IDE)
Personal skills live in `~/.claude/skills/<skill-name>/SKILL.md` and apply to every project
(docs: https://code.claude.com/docs/en/skills).
```bash
bash scripts/install-claude-code.sh            # copies every skill folder into ~/.claude/skills
bash scripts/install-claude-code.sh --only A,B # only the directly usable ones
```

### MCP servers (class A, and class B skills that name a verified MCP package)
Claude Desktop → Settings → Developer → Edit Config opens `claude_desktop_config.json`
(macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`, Windows: `%APPDATA%\Claude\claude_desktop_config.json`).
Add the `mcpServers` entries shown in the skill, quit and relaunch the app
(docs: https://support.claude.com/en/articles/10949351-getting-started-with-local-mcp-servers-on-claude-desktop,
https://modelcontextprotocol.io/docs/develop/connect-local-servers).

## Safety notes carried over from the catalog
Several plugins talk to paid or third-party services (image/video generation, phone rental, crypto
wallets). Each SKILL.md repeats the catalog's disclosure in its **Limits** section. Env vars hold secrets;
never paste keys into a skill file or an MCP config that you share.

## Licensing
Skill text in this pack is original. Where an upstream plugin shipped its own `skills/*/SKILL.md`
under MIT, Apache-2.0 or BSD, a copy is included under `skills/<name>/references/` with attribution.
Plugins with no LICENSE file are summarised, not copied.
