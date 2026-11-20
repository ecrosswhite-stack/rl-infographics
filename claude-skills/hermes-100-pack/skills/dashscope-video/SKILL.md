---
name: dashscope-video
description: Generate short videos with Alibaba Cloud DashScope (Qwen Cloud / Model Studio) HappyHorse 1.1 models by calling the DashScope async task API directly with curl or Python. Use when the user asks to "make a video from this prompt", "turn this image into a video", "animate this picture", "text-to-video", "image-to-video", "reference-to-video", mentions DashScope, Qwen Cloud, Model Studio, HappyHorse, or has a QWEN_API_KEY / DASHSCOPE_API_KEY and wants a clip generated.
---
# DashScope Video (HappyHorse 1.1)

**Hermes original:** https://github.com/rriggs/hermes-plugin-dashscope-video @ 229b5c9 · tier: community · category: tools · license: MIT
**Port class:** B — the plugin is a thin REST client over the public DashScope async task API, which Claude can call from bash or Python.

## What the Hermes plugin does
Registers a `VideoGenProvider` named `dashscope` behind Hermes's generic `video_generate` tool (no tools of its own are listed in the catalog). Per the plugin source it submits an async video-synthesis task, polls the task until it reaches a terminal state, then downloads the resulting video because DashScope output URLs expire. It auto-routes to `happyhorse-1.1-t2v` (prompt only), `happyhorse-1.1-i2v` (prompt + `image_url`), or `happyhorse-1.1-r2v` (prompt + one reference image). Local image paths are inlined as base64 data URIs (max 10 MB).

## Equivalent in Claude
Env vars (same names as the plugin): `QWEN_API_KEY` (token plan keys, `sk-sp-*`), or `DASHSCOPE_API_KEY` for pay-as-you-go keys (`sk-ws-*`).

API base URLs copied from the plugin source:
- Token plan (default): `https://token-plan.ap-southeast-1.maas.aliyuncs.com`
- PAYG: `https://dashscope-intl.aliyuncs.com`

Steps:
1. Pick the model ID from the inputs: text only -> `happyhorse-1.1-t2v`; `image_url` -> `happyhorse-1.1-i2v`; reference image -> `happyhorse-1.1-r2v`.
2. Map aspect ratio to `size`: `16:9` -> `1280*720`, `9:16` -> `720*1280`, `1:1` -> `960*960`, `4:3` -> `1024*768`, `3:4` -> `768*1024`. Clamp `duration` to 3..10 seconds (default 5).
3. For a local image, build `data:<mime>;base64,<...>` (skip files over 10 MB; use a URL instead).
4. Submit the task:
   ```bash
   API=https://token-plan.ap-southeast-1.maas.aliyuncs.com
   curl -s -X POST "$API/api/v1/services/aigc/video-generation/video-synthesis" \
     -H "Authorization: Bearer $QWEN_API_KEY" -H "Content-Type: application/json" \
     -H "X-DashScope-Async: enable" \
     -d '{"model":"happyhorse-1.1-t2v","input":{"prompt":"<prompt>"},"parameters":{"duration":5,"size":"1280*720"}}'
   ```
   For i2v add `"image_url"` to `input`; for r2v add `"ref_image_url"`. The response carries `output.task_id`; a top-level `code` field means an error.
5. Poll `GET $API/api/v1/tasks/<task_id>` with the same `Authorization` header every 5 seconds until `output.task_status` is `SUCCEEDED`, `FAILED`, `CANCELED` or `UNKNOWN`. The plugin gives up after 600 seconds.
6. On `SUCCEEDED`, read `output.video_url` (fallbacks the plugin checks: `output.results[].url`, then `output.choices[].message.content[].video`). Download it immediately with `curl -L -o <file>.mp4 "<url>"`; the URL is ephemeral.
7. Report the local file path, model, duration and task_id.

| Hermes tool | How Claude does it |
|---|---|
| `video_generate` (provider dashscope) | Steps 4 to 6 above with curl or Python `requests` |
| model listing / capabilities | Static: family `happyhorse-1.1`, modes t2v/i2v/r2v, 720p, 3..10 s, no audio, no negative prompt, 1 reference image |

## Setup
1. Create an API key in Alibaba Cloud Model Studio (`https://modelstudio.console.alibabacloud.com/`).
2. `export QWEN_API_KEY=sk-sp-...` (token plan) or `export DASHSCOPE_API_KEY=sk-ws-...` and use the PAYG base URL.
3. Make sure `curl` or Python with `requests` is available.

## Limits
- Hermes config keys (`video_gen.dashscope.*`, per-mode model overrides) are replaced by choosing the model ID yourself.
- The local cache under `$HERMES_HOME/cache/videos/` is not replicated; save the download wherever the user asks.
- Generation spends Alibaba Cloud quota or money; prompts and images are sent to Alibaba Cloud.
- Generation takes several minutes per the README; keep the poll loop running in the background if needed.
- Not verified in this port: current availability of the HappyHorse models or the token-plan endpoint.

## Source
- Catalog entry (reviewed commit): https://github.com/rriggs/hermes-plugin-dashscope-video/tree/229b5c93d498dfa25aab31f0bef47f32fccde69f
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/dashscope-video.yaml
