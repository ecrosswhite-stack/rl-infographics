---
name: dashscope-image
description: Generate or edit images with Alibaba Cloud DashScope (Qwen Cloud / Model Studio) Wan 2.7 models by calling the native DashScope multimodal-generation API with curl or Python. Use when the user says "generate an image with Qwen", "DashScope image", "wan2.7-image", "Alibaba Model Studio image", "use my QWEN_API_KEY", or asks for text-to-image or image-to-image on a token-plan (sk-sp-*) or pay-as-you-go (sk-ws-*) Alibaba key.
---
# DashScope (Qwen Cloud) image generation

**Hermes original:** https://github.com/rriggs/hermes-plugin-dashscope-image @ f13665c · tier: community · category: tools · license: MIT
**Port class:** B — the plugin is a thin HTTP client for one DashScope endpoint; Claude can issue the same request from Claude Code or Cowork.

## What the Hermes plugin does
Registers a `DashScopeImageGenProvider` (kind `backend`) so Hermes's `image_generate` tool routes to Alibaba Cloud DashScope. It supports `wan2.7-image` (fast text-to-image) and `wan2.7-image-pro` (image-to-image; auto-selected when a source image is given), maps aspect ratios to sizes `1280*720`, `1024*1024`, `720*1280`, converts local image files to base64 data URIs (max 10 MB), and caches the returned image because DashScope OSS URLs expire after about 24 hours. It registers no standalone tools.

## Equivalent in Claude
Per the plugin source, the request is:

```
POST {API_BASE}/api/v1/services/aigc/multimodal-generation/generation
Authorization: Bearer $QWEN_API_KEY
Content-Type: application/json
```

Defaults copied from the source: `API_BASE=https://token-plan.ap-southeast-1.maas.aliyuncs.com` and key env var `QWEN_API_KEY` (token plan). PAYG users use `API_BASE=https://dashscope-intl.aliyuncs.com` and `DASHSCOPE_API_KEY`.

1. Confirm the key is set: `test -n "$QWEN_API_KEY"` (or `$DASHSCOPE_API_KEY`). Never print it.
2. Build the payload. Text-to-image:
   ```json
   {"model":"wan2.7-image","input":{"messages":[{"role":"user","content":[{"text":"PROMPT"}]}]},"parameters":{"size":"1024*1024"}}
   ```
   Image-to-image: use `"model":"wan2.7-image-pro"` and prepend `{"image":"https://... or data:image/png;base64,..."}` to `content` (one reference image).
3. Send it: `curl -sS -X POST "$API_BASE/api/v1/services/aigc/multimodal-generation/generation" -H "Authorization: Bearer $QWEN_API_KEY" -H "Content-Type: application/json" -d @payload.json`.
4. Check `code` in the response; if present, report `code` and `message`. Otherwise read the URL from `output.choices[0].message.content[*].image` (fallback key `url`).
5. Download the image immediately (`curl -o out.png "$URL"`) and hand the file to the user; the URL expires.

| Hermes tool | How Claude does it |
|---|---|
| `image_generate` (text) via dashscope | curl POST with `wan2.7-image`, text-only content |
| `image_generate` with `image_url` | curl POST with `wan2.7-image-pro`, image item first, local file base64-encoded (`base64 -w0`) |
| Local cache under `$HERMES_HOME/cache/images/` | save the downloaded file in the working directory |

## Setup
1. Create an API key in Alibaba Cloud Model Studio (console URL named in the plugin: https://modelstudio.console.alibabacloud.com/).
2. Export it: `export QWEN_API_KEY=sk-sp-...` (token plan) or `export DASHSCOPE_API_KEY=sk-ws-...` (PAYG, with the `dashscope-intl` base URL).
3. No install needed; `curl` or Python `requests` suffices.

## Limits
- Each call consumes token-plan quota or PAYG credit on the user's Alibaba Cloud account; say so before generating in bulk.
- Prompts and reference images are sent to Alibaba Cloud.
- Only the sizes and models listed in the source were ported; other Wan models or sizes are not verified.
- The OpenAI-compatible `/images/generations` path is not used because the token-plan endpoint does not serve image models there (per the plugin README).
- Hermes `config.yaml` keys (`image_gen.dashscope.*`) have no Claude counterpart; pass the base URL and model explicitly.

## Source
- Catalog entry (reviewed commit): https://github.com/rriggs/hermes-plugin-dashscope-image/tree/f13665c97eb852b3ef90e30e020dbdcf0c9dc38b
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/dashscope-image.yaml
