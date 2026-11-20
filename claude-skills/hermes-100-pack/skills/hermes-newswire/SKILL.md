---
name: hermes-newswire
description: Fetch, discover and summarize RSS, Atom and JSON Feed sources with no API keys, replicating the feed engine behind the Hermes Desktop newswire ticker. Use it when the user says "what are the latest headlines from these feeds", "find the RSS feed for theverge.com", "give me a news digest from my OPML file", "check Hacker News / my blogroll for new posts", "import or export my feed list as OPML", or wants a quick scrolling-ticker style briefing from sites they follow. Claude fetches feeds with curl and parses them with Python's standard library. Not for paid news APIs or for building the Hermes Desktop ticker UI itself.
---
# Hermes Newswire (feed engine)

**Hermes original:** https://github.com/tony-simons-aiowa/hermes-newswire @ deccdc4 · tier: community · category: desktop · license: MIT
**Port class:** C · the keyless feed fetch, parse, discovery and OPML handling are reproducible; the Hermes Desktop ticker strip, `/newswire` page, SQLite cache and refresh loop are not.

## What the Hermes plugin does
A unified Hermes Desktop plugin: `dashboard/plugin_api.py` is a FastAPI router mounted at `/api/plugins/hermes-newswire/` that fetches RSS 2.0, RSS 1.0/RDF, Atom and JSON Feed sources, discovers feeds from a site URL, searches feeds, stores articles in SQLite, and serves routes such as `/sources`, `/articles`, `/refresh-all`, `/discover`, `/search`, `/preview`, `/opml/import`, `/opml/export`. `desktop/plugin.js` renders a scrolling headline strip above the statusbar plus a Newswire page. It registers no agent tools or hooks (`register()` is a no-op) and uses no API keys or model tokens.

## Equivalent in Claude
Facts below are copied from `dashboard/plugin_api.py` and the README.

1. Fetch a feed: `curl -sL --max-redirs 3 --connect-timeout 5 --max-time 15 --max-filesize 5242880 -H 'Accept: application/rss+xml, application/atom+xml, application/feed+json, application/json' "$URL" -o feed.bin`. The plugin allows only `http`/`https`, blocks loopback, private, link-local, CGNAT and metadata addresses (before and after DNS resolution), caps bodies at 5 MB and allows at most 3 redirects. Apply the same checks before fetching a user-supplied URL.
2. Parse with `python3 -I`: `xml.etree.ElementTree` for RSS/RDF/Atom (namespaces: `http://purl.org/rss/1.0/` for RSS 1.0, `http://purl.org/rss/1.0/modules/content/` for `content:encoded`), `json` for JSON Feed. Extract title, link, published date (`email.utils.parsedate_to_datetime` for RFC 822 dates), source name. Strip all HTML from summaries before showing them, as the plugin does.
3. Discover a feed from a site URL: fetch the page, read `<link rel="alternate" type="...">` tags whose type is one of `application/rss+xml`, `application/atom+xml`, `application/feed+json`, `application/json`; if none, try the well-known paths `/feed`, `/feed.xml`, `/rss`, `/rss.xml`, `/atom.xml`, `/index.xml`, `/feed.json`, `/blog/feed`, `/blog/rss.xml`. A URL that already parses as a feed skips discovery.
4. Search feeds by keyword: the plugin queries `https://cloud.feedly.com/v3/search/feeds` (constant `FEEDLY_SEARCH`); the exact query parameters are not verified here, so read the response shape before relying on it or ask the user for a site URL instead.
5. Deduplicate by link, sort newest first, and present `Source: Title · age` lines, mirroring the ticker format `NEWSWIRE ◆ Source: Title · 56m`.
6. OPML: read `<outline xmlUrl="...">` entries from the user's file for import; write the same structure for export. Validate every URL with the rules in step 1.

| Hermes surface | How Claude does it |
|---|---|
| Sources list / add / remove | keep a local `feeds.opml` or a JSON list the user owns |
| `/refresh-all`, `/articles` | re-fetch each feed, merge, show unread since last run |
| `/discover` | step 3 |
| `/search` | step 4, or ask for the site URL |
| `/preview` | fetch and parse once, show first items |
| mark read / read-all | track seen links in a local JSON file if the user wants state |
| Ticker strip, Newswire page, settings | not replicated; offer a text digest instead |

## Setup
None. No API keys; `curl` and `python3` are enough.

## Limits
- No background refresh, no persistent SQLite cache, no offline mode, no conditional GET (ETag/Last-Modified) unless Claude implements it per run.
- No Hermes Desktop UI: ticker, hover-pause, favicons, grouping modes, keyboard shortcuts, sidebar entry are not replicated.
- Feedly search endpoint usage is "per the plugin source"; parameters and terms of use not verified.
- Fetching feeds sends requests to third-party sites; private-address blocking must be applied by Claude manually.
- No upstream skills/ directory exists to copy.

## Source
- Catalog entry (reviewed commit): https://github.com/tony-simons-aiowa/hermes-newswire/tree/deccdc4575ff45461fbf3f3c61e0945f188ef620
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/hermes-newswire.yaml
