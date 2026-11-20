---
name: minimax-video
description: Generate videos with MiniMax Hailuo models (text-to-video, image-to-video, subject-reference-to-video) through the MiniMax async video API, replicating the Hermes minimax-video backend with the user's MINIMAX_PAYG_KEY. Use when the user says "make a video with MiniMax", "Hailuo", "generate a clip from this prompt/image", "animate this character", asks for 6 or 10 second AI video with camera moves like [Push in] or [Pan left], or has a MiniMax key and wants video output. Also covers the verified minimax-mcp PyPI server.
---
# MiniMax (Hailuo) Video Generation

**Hermes original:** https://github.com/rriggs/hermes-plugin-minimax-video @ 759bec0 · tier: community · category: tools · license: MIT
**Port class:** B · the plugin wraps three MiniMax REST endpoints (submit, poll, retrieve) that Claude can drive from bash or Python.

## What the Hermes plugin does
Registers a `VideoGenProvider` named `minimax` (`kind: backend`) behind Hermes's `video_generate` tool. Per `__init__.py` it POSTs `{api}/v1/video_generation` with `{model, prompt, duration, resolution, prompt_optimizer?, first_frame_image?, subject_reference?}`, polls `GET {api}/v1/query/video_generation?task_id=` every 5 s for up to 600 s until `status` is `Success` or `Fail`, then calls `GET {api}/v1/files/retrieve?file_id=` to obtain `file.download_url` and downloads the MP4. Default `api` is `https://api.minimax.io`; the key is read from the env var named by `key_env` (plugin.yaml requires `MINIMAX_PAYG_KEY`; the code default is `MINIMAX_API_KEY`). Models listed: `MiniMax-Hailuo-2.3` (T2V, I2V), `MiniMax-Hailuo-2.3-Fast` (I2V), `MiniMax-Hailuo-02` (T2V, I2V), `S2V-01` (subject reference), plus older `T2V-01`, `T2V-01-Director`, `I2V-01`, `I2V-01-Director`, `I2V-01-live`.

## Equivalent in Claude
1. Read the key: `KEY="${MINIMAX_PAYG_KEY:-$MINIMAX_API_KEY}"`; stop if empty.
2. Pick the mode from inputs exactly as the plugin does: `image_url` given -> I2V (`first_frame_image`); reference images given -> S2V with model `S2V-01` and `subject_reference: [{"type":"character","image":["<url or data URI>"]}]`; otherwise T2V. Default model `MiniMax-Hailuo-2.3`.
3. Duration: 6 or 10 only (10 when the user asks for more than 6). Resolution: `768P` default for Hailuo models (`1080P` allowed; Hailuo-02 also `512P`), `720P` for the older models. Local image files: base64 data URI `data:image/png;base64,...`, max 10 MB per the plugin.
4. Submit:
   ```bash
   curl -sS -X POST "https://api.minimax.io/v1/video_generation" \
     -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
     -d '{"model":"MiniMax-Hailuo-2.3","prompt":"<prompt>","duration":6,"resolution":"768P"}'
   ```
   Check `base_resp.status_code == 0`, else report `base_resp.status_msg`. Keep `task_id`.
5. Poll every 5 s, at most 10 minutes: `curl -sS "https://api.minimax.io/v1/query/video_generation?task_id=$TASK" -H "Authorization: Bearer $KEY"`; stop on `status` `Success` or `Fail`.
6. On Success take `file_id`, then `curl -sS "https://api.minimax.io/v1/files/retrieve?file_id=$FILE" -H "Authorization: Bearer $KEY"`; download `.file.download_url` promptly (the plugin notes URLs are ephemeral) and save it locally.
7. Camera control per the README: embed `[Push in]`, `[Pan left]`, `[Pedestal up]`, `[Static shot]` etc. in the prompt; combine with commas inside one bracket, sequence with "then".

| Hermes capability | How Claude does it |
|---|---|
| `video_generate(prompt)` | steps 4-6, T2V |
| `video_generate(prompt, image_url)` | add `first_frame_image` |
| `video_generate(prompt, reference_image_urls)` | model `S2V-01`, `subject_reference` array |

Verified MCP alternative (`pip index versions minimax-mcp` on 2026-11-20: `minimax-mcp (0.0.20)`). Its wheel contains `generate_video` and `query_video_generation` tools and reads `MINIMAX_API_KEY` and `MINIMAX_API_HOST` (seen by inspecting `minimax_mcp/server.py` and `const.py`, not by running it). Note the env var name differs from the plugin's `MINIMAX_PAYG_KEY`.

## Setup
1. Create a key at https://platform.minimax.io/user-center/basic-information/interface-key (URL from the plugin's setup schema).
2. `export MINIMAX_PAYG_KEY="..."` (and `export MINIMAX_API_KEY="$MINIMAX_PAYG_KEY"` if using minimax-mcp).
3. Optional Claude Desktop MCP: `{"mcpServers":{"minimax":{"command":"uvx","args":["minimax-mcp"],"env":{"MINIMAX_API_KEY":"<key>","MINIMAX_API_HOST":"https://api.minimax.io"}}}}`. Tool behavior of that server was not tested here.

## Limits
- Spends money: MiniMax bills per generated video on the PAYG plan. Confirm with the user before each submission.
- Prompts and images are uploaded to MiniMax, a third party.
- Hermes's `$HERMES_HOME/cache/videos/` caching, `config.yaml` `video_gen.minimax` section and `hermes tools` setup UI are not replicated; save the file where the user asks.
- Aspect ratio, negative prompt, audio and seed are accepted by Hermes's tool layer but the plugin never sends them to MiniMax; same here.
- Response field names were taken from the plugin source, not re-verified against MiniMax docs.

## Source
- Catalog entry (reviewed commit): https://github.com/rriggs/hermes-plugin-minimax-video/tree/759bec0f124c50e868facc8da5e6cf054403d761
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/minimax-video.yaml
