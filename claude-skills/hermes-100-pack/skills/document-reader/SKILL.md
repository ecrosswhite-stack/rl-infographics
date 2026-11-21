---
name: document-reader
description: Reference card for the Hermes document-reader plugin, a Windows-only, profile-scoped watched-folder OCR service with a Hermes Desktop reader and HUD attachment action. Not a working port. Consult it only when someone asks what the Hermes "Document Reader" plugin did, why it has no Claude equivalent, or how to get similar document text extraction from Claude. For actual PDF or image reading in Claude, use the built-in file reading tools instead of this skill.
---
# Hermes Document Reader (reference card)

**Hermes original:** https://github.com/lEWFkRAD/hermes-document-reader @ f3a0bed · tier: community · category: desktop · license: MIT
**Port class:** D · it is a Hermes Desktop/HUD renderer component plus a per-profile Windows background service managed by a Hermes CLI command; it registers no agent tools.

## What the Hermes plugin does
Per plugin.yaml (`kind: standalone`, `platforms: [windows]`) and `__init__.py`, the plugin registers one Hermes CLI command, `hermes document-reader` (configure, install, status, recover, rollback, uninstall), and no tools or hooks. The lifecycle installs a loopback-only FastAPI OCR service as a current-user Windows scheduled task under `<HERMES_HOME>\document-reader`, watches `data\inbox`, sends page images to a user-configured OpenAI-compatible multimodal OCR endpoint (`--api-base`, `--model`, token prompted interactively), and exports `.txt` plus `.xlsx` (one sheet per detected table). A Hermes Desktop sidebar reader shows live previews; a HUD composer action queues up to ten files and inserts only a `[Document Reader queued N files]` marker. The source tree also holds a source-only, profile-bound MCP server (`mcp/anydoc-mcp.py`) that is not installed or registered by the plugin.

## Equivalent in Claude
None identified as a port: the Desktop reader, HUD action, Windows scheduled task and profile ownership checks are Hermes-specific. Nearest Claude-native behavior: Claude Code's Read tool reads PDF pages and image files directly, so ask Claude to read the document and extract text or tables itself. A watched-folder or background OCR service is not provided.

## Setup
None.

## Limits
- Nothing from the plugin runs outside Hermes on Windows; the service requires Hermes 0.20+, 64-bit CPython 3.11/3.14 and `hermes -p <profile>` ownership.
- The plugin sends page images to whatever OCR endpoint the user configured (possibly a third party); Claude's built-in reading keeps the file within the Claude session instead.
- The source-only `anydoc-mcp.py` MCP server depends on the plugin's profile layout (`inbox`/`processed` roots) and pinned packages (`firecrawl-anydoc`, `mcp`, `chandra-ocr`); it was not verified as runnable standalone and is not recommended here.
- Table-to-`.xlsx` export is not replicated; ask Claude to produce a spreadsheet separately if needed.

## Source
- Catalog entry (reviewed commit): https://github.com/lEWFkRAD/hermes-document-reader/tree/f3a0bed28e6c289942b899924d9e7cf8b93045e8
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/document-reader.yaml
