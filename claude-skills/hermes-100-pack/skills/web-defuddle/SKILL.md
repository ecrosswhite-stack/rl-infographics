---
name: web-defuddle
description: Extract clean article markdown and metadata (title, description, domain, author, published date, word count, language) from a URL with the local, free defuddle CLI, exactly as the Hermes web-defuddle extract provider did. Use it when a user asks to "read this article", "get the text of this page as markdown", "strip the boilerplate from this URL", "extract content from these links", or when a plain fetch returns navigation clutter and a reader-mode result is wanted. Extract only; it does not search the web.
---
# Defuddle web extraction

**Hermes original:** https://github.com/annalinneajohansson82/hermes-defuddle @ d28bd52 · tier: community · category: web · license: no LICENSE file found (README states MIT, but no license file is in the checkout)
**Port class:** B · the provider only shells out to the `defuddle` npm CLI and parses its JSON; Claude Code can run the same command.

## What the Hermes plugin does
Per plugin.yaml (`kind: backend`, `provides_web_providers: [defuddle]`) and `provider.py`, `register()` calls `ctx.register_web_search_provider(DefuddleWebExtractProvider())`. The provider reports `supports_search() == False`, `supports_extract() == True`, checks `shutil.which("defuddle")`, and for each URL runs `defuddle parse --json <url>` with a 60 second timeout, in parallel across URLs. It reads `contentMarkdown` as the content, prefixes the `description` as a blockquote when it differs from the title, and builds metadata from `domain`, `site`, `language`, `wordCount`, `author`, `published`. Errors (binary missing, non-zero exit, timeout, empty or invalid JSON, no `contentMarkdown`) are returned as error records. No env vars, no API key.

## Equivalent in Claude
1. Check the binary: `command -v defuddle`. If missing, see Setup.
2. Extract: `defuddle parse --json '<url>' </dev/null` (the plugin passes `stdin=DEVNULL`; keep a 60 second timeout, for example `timeout 60 defuddle parse --json '<url>'`).
3. Parse the JSON: use `.contentMarkdown` as the article body; if it is empty, report "defuddle did not produce markdown content" rather than showing raw `.content` HTML. Collect `.title`, `.description`, `.domain`, `.site`, `.language`, `.wordCount`, `.author`, `.published`.
4. Present the result as `> <description>` (if different from the title) followed by the markdown, plus a short metadata line.
5. Several URLs: run them in parallel with `&` and `wait`, or sequentially, and report per-URL errors without aborting the batch.

| Hermes capability | How Claude does it |
|---|---|
| `web_extract` with `extract_backend: defuddle` | `defuddle parse --json <url>` and the parsing rules above |
| Pairing with a search provider | Use the Claude web search tool or another search skill first, then defuddle on the chosen URLs |

## Setup
1. Node.js with npm.
2. `npm i -g defuddle` (verified with `npm view defuddle name version description`: `name = 'defuddle'`, `version = '0.19.13'`, "Extract article content and metadata from web pages.").
3. No env vars.

## Limits
- The checkout has no LICENSE file, so no upstream text was copied; this skill summarizes the source.
- Redirect gap carried over from the README: defuddle follows redirects itself and its JSON exposes no final URL, so a redirect to an internal host is not re-checked. Do not point it at URLs you have not vetted.
- Extract only; no search.
- `defuddle` was not executed during this port; the command and JSON field names are quoted from `provider.py`.

## Source
- Catalog entry (reviewed commit): https://github.com/annalinneajohansson82/hermes-defuddle/tree/d28bd52eed30c397a45f0b2aba869a28ca4789c4
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/web-defuddle.yaml
