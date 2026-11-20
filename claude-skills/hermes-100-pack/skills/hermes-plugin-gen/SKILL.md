---
name: hermes-plugin-gen
description: Scaffold, extend and bundle Hermes Agent plugins (plugin.yaml, __init__.py, schemas.py, tools.py, optional skills/) by writing the files directly, following the templates of the hermes-plugin-gen plugin. Use when the user says "create a Hermes plugin that does X", "scaffold a hermes-agent plugin", "add a tool to my Hermes plugin", "bundle a skill with my Hermes plugin", or is working inside ~/.hermes/plugins/.
---
# Hermes Plugin Generator

**Hermes original:** https://github.com/iruzen-dono/hermes-plugin-gen @ 75899f9 · tier: community · category: tools · license: MIT
**Port class:** B — the plugin is a pure-stdlib file generator for a documented directory layout; Claude can write the same files with its file tools.

## What the Hermes plugin does
Registers three tools: `plugin_scaffold` (create a full plugin directory from a description), `plugin_add_tool` (append a tool to an existing plugin: schema, handler, registration, manifest entry) and `plugin_add_skill` (write `skills/<name>/SKILL.md` and register it). Generated handlers contain `TODO` stubs; the plugin refuses to overwrite an existing plugin. It ships a bundled skill (in French) describing when and how to use the tools.

## Equivalent in Claude
Target directory: `$HERMES_HOME/plugins/<name>/` (default `~/.hermes/plugins/<name>/`). Names: lowercase with hyphens, max 64 chars; tool function names in snake_case.

Write these files (structure taken from the plugin's templates in `tools.py`):
1. `plugin.yaml`
   ```yaml
   name: <name>
   kind: standalone
   version: 0.1.0
   description: "<one line>"
   author: <author>
   requires_env:            # only if needed
     - name: MY_API_KEY
       description: "..."
       prompt: "..."
       password: true
   provides_tools:
     - <tool-name>
   ```
2. `schemas.py`: one dict per tool, `TOOL_NAME = {"name": "<tool-name>", "description": "...", "parameters": {"type": "object", "properties": {...}, "required": [...]}}`.
3. `tools.py`: `def <tool_fn>(args: dict, **kwargs) -> str` returning `json.dumps(result)`; wrap in try/except and return `{"error": str(e)}` on failure. If env vars are required, add `_REQUIRED_ENV_VARS = [...]` and `def check_requirements() -> bool: return all(os.getenv(v) for v in _REQUIRED_ENV_VARS)`.
4. `__init__.py`:
   ```python
   from . import schemas, tools
   def register(ctx):
       ctx.register_tool(name="<tool-name>", toolset="<name>", schema=schemas.TOOL_NAME,
                         handler=tools.tool_fn, check_fn=tools.check_requirements,  # check_fn only with env vars
                         description="...", emoji="🔧", is_async=False)
   ```
   Hooks (optional): `ctx.register_hook("pre_tool_call", tools.pre_tool_call_hook)` / `"post_tool_call"`.
5. Skill (optional): `skills/<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`, `version`, `author`), plus in `__init__.py` a loop over `Path(__file__).parent / "skills"` calling `ctx.register_skill(child.name, skill_md)`, and `provides_skills:` in `plugin.yaml`.

| Hermes tool | How Claude does it |
|---|---|
| `plugin_scaffold` | Check the directory does not exist, then write files 1 to 5 |
| `plugin_add_tool` | Append a schema dict, a handler function, a `ctx.register_tool(...)` block after the last one, and a `provides_tools` entry |
| `plugin_add_skill` | Write `skills/<skill>/SKILL.md`, add the register_skill loop if absent, add `provides_skills` |

Then tell the user to run `hermes plugins enable <name>`, set env vars in `$HERMES_HOME/.env`, and restart Hermes. Fill the `TODO` handlers before enabling.

## Setup
None (the user needs a Hermes Agent install to use the result).

## Limits
- The generated plugin only runs inside Hermes Agent; nothing here makes Claude load it.
- The exact `register_tool` keyword set (`check_fn`, `emoji`, `is_async`) is copied from the plugin templates, not verified against the current Hermes plugin API.
- The emoji guesser and the French bundled skill text are not reproduced beyond the upstream copy in `references/`.

## Source
- Catalog entry (reviewed commit): https://github.com/iruzen-dono/hermes-plugin-gen/tree/75899f960d8358731255172add8232344c9084b8
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-plugin-gen.yaml
