---
name: minimax-image
description: Generate images with MiniMax Image-01 models (text-to-image with image-01, image-to-image with a subject reference via image-01-live) by calling the MiniMax image generation API with MINIMAX_API_KEY. Use this when the user says "generate an image with MiniMax", "use image-01", "make a picture of ... with MiniMax", "put this character into a cyberpunk city" with a reference photo, or asks for MiniMax-hosted image generation from Claude Code or Cowork. Costs MiniMax credits per call.
---
# MiniMax Image Generation

**Hermes original:** https://github.com/rriggs/hermes-plugin-minimax-image @ 5a07a0f · tier: community · category: tools · license: MIT
**Port class:** B · the plugin is a single HTTP call to the MiniMax API that Claude can issue directly.

## What the Hermes plugin does
Registers a `minimax` image generation provider (`ctx.register_image_gen_provider`) behind Hermes' `image_generate` tool. It builds a `POST {api}/v1/image_generation` request with the prompt, an aspect ratio string, `response_format: "url"` and `n: 1`. When a source or reference image is given it switches to `image-01-live` and adds a `subject_reference` array of `{type: "character", image_file: <url or data URI>}`. The returned image URL is cached locally because MiniMax URLs expire after about 24 hours (per the plugin README).

## Equivalent in Claude
Per the plugin source (`__init__.py`):

1. Read `MINIMAX_API_KEY` from the environment (the plugin's default `key_env`). Base URL default: `https://api.minimax.io`.
2. Truncate the prompt to 1500 characters (MiniMax limit per the plugin).
3. Map the requested shape to a ratio: landscape -> `16:9`, square -> `1:1`, portrait -> `9:16`.
4. Choose the model: `image-01` for text-to-image; `image-01-live` whenever a reference image is supplied.
5. For a local reference image, base64-encode it into `data:<mime>;base64,...` (plugin cap: 10 MB); http(s) URLs and data URIs pass through unchanged. The plugin's capabilities declare `max_reference_images: 1`.
6. Send:

```bash
curl -sS -X POST "https://api.minimax.io/v1/image_generation" \
  -H "Authorization: Bearer $MINIMAX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"image-01","prompt":"<prompt>","aspect_ratio":"1:1","response_format":"url","n":1}'
```

For image-to-image add `"model":"image-01-live"` and `"subject_reference":[{"type":"character","image_file":"<url-or-data-uri>"}]`.

7. Check `base_resp.status_code`; non-zero means an API error (`base_resp.status_msg`). Read the image from `data.image_urls[0]`.
8. Download the URL immediately (for example `curl -o out.png <url>`) and give the user the local file; the URL expires.

| Hermes tool | How Claude does it |
|---|---|
| `image_generate(prompt, aspect_ratio)` | POST as above with `image-01` |
| `image_generate(prompt, image_url=...)` | POST with `image-01-live` and `subject_reference` |
| list models | `image-01` (~5 s, text-to-image), `image-01-live` (~10 s, subject reference), per the plugin table |

## Setup
1. Create a MiniMax API key at the MiniMax platform (the plugin links `https://platform.minimax.io/user-center/basic-information/interface-key`).
2. `export MINIMAX_API_KEY=<key>`
3. Optional: a PyPI package named `minimax-mcp` exists (`pip index versions minimax-mcp` -> 0.0.20). Its image-generation support was not verified in this port; configure it only after reading its own documentation.

## Limits
- Hermes config keys (`image_gen.minimax.api`, `key_env`, `model`) and the `hermes tools` setup wizard are not replicated; use the env var and defaults above.
- Local caching under `$HERMES_HOME/cache/images/` is replaced by downloading the file yourself.
- Each call spends MiniMax credits ("PAYG / token plan" per the plugin). Reference images are uploaded to MiniMax.
- Response field names beyond `base_resp` and `data.image_urls` were not verified.

## Source
- Catalog entry (reviewed commit): https://github.com/rriggs/hermes-plugin-minimax-image/tree/5a07a0f67d74a67ac426d7b901f8bfc60f28951c
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/minimax-image.yaml
