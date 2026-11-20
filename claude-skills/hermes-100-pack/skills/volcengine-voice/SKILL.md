---
name: volcengine-voice
description: Chinese text-to-speech and speech-to-text through Volcengine (火山引擎) Doubao (豆包) speech APIs, ported from the Hermes volcengine-voice provider. Use it when the user has a VOLCENGINE_VOICE_API_KEY and asks to "read this aloud in Chinese", "generate an mp3 with the Doubao voice", "use the 爽快思思 or Vivi voice", "[开心] style TTS", "transcribe this Chinese audio with Volcengine", or wants a script for openspeech.bytedance.com. Not for Hermes voice-channel routing, which was the plugin's integration point.
---
# Volcengine Voice

**Hermes original:** https://github.com/linxichen/hermes-volcengine-voice @ e3f8a30 · tier: community · category: voice · license: no LICENSE file found (README states MIT, no LICENSE file in the checkout)
**Port class:** B - the plugin wraps two documented Volcengine HTTP/WebSocket endpoints with a single API key; Claude can call the TTS endpoint with curl or Python and the STT endpoint with a short Python websockets script.

## What the Hermes plugin does
A `kind: provider` plugin that monkey-patches Hermes' `text_to_speech_tool` and `transcribe_audio` so that `tts.provider: volcengine` / `stt.provider: volcengine` route to Doubao. TTS uses HTTP chunked streaming at `POST https://openspeech.bytedance.com/api/v3/tts/unidirectional`; STT uses the binary WebSocket protocol at `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async`. It maps short voice names to voice types, supports `[情绪]` emotion prefixes passed as non-billed `context_texts` for 2.0 voices, truncates TTS text to 5000 characters, and registers a `pre_llm_call` hook that injects voice-friendly response instructions. It registers no tools of its own.

## Equivalent in Claude
TTS, per `tts.py`:

```bash
curl -s -N -X POST https://openspeech.bytedance.com/api/v3/tts/unidirectional \
  -H "X-Api-Key: $VOLCENGINE_VOICE_API_KEY" -H "X-Api-Resource-Id: seed-tts-2.0" \
  -H "X-Api-Request-Id: $(uuidgen)" -H "Content-Type: application/json" \
  -d '{"user":{"uid":"claude"},"req_params":{"text":"今天天气真好","speaker":"zh_female_shuangkuaisisi_uranus_bigtts","audio_params":{"format":"mp3","sample_rate":24000}}}'
```

The response is a stream of JSON lines; concatenate the base64-decoded `data` field of each line into the output file. A line with `code` 20000000 marks a normal end of stream; any other non-zero code is an error. For emotion control strip leading `[tag]` markers from the text and send `"additions": "{\"context_texts\": [\"用开心的语气说\"]}"` (a JSON string, not an object) inside `req_params`; this only takes effect with `seed-tts-2.0` voices. Use `"format": "ogg_opus"` for non-mp3 output.

Voice presets (short name, voice type, resource id):
- `zh_female_conversation` = `zh_female_shuangkuaisisi_uranus_bigtts`, seed-tts-2.0 (default, 爽快思思 2.0)
- `zh_female_gentle` = `zh_female_vv_uranus_bigtts`, seed-tts-2.0 (Vivi 2.0)
- `zh_female_sweet` = `zh_female_tianmeixiaoyuan_uranus_bigtts`, seed-tts-2.0 (甜美小源 2.0)
- `zh_male_ruya` = `zh_male_ruyayichen_uranus_bigtts`, seed-tts-2.0 (儒雅逸辰 2.0)
- `zh_male_conversation` = `zh_male_M392_conversation_wvae_bigtts`, seed-tts-1.0
Full list: https://www.volcengine.com/docs/6561/1257544

STT, per `stt.py`: connect with the Python `websockets` package to `wss://openspeech.bytedance.com/api/v3/sauc/bigmodel_async` with headers `X-Api-Key`, `X-Api-Resource-Id: volc.seedasr.sauc.duration`, `X-Api-Request-Id` (uuid), `X-Api-Sequence: -1`. Send a full client request frame (4-byte header, 4-byte size, gzip JSON payload `{"user":{"uid":"..."},"audio":{"format":"mp3|wav|ogg|mp4|aac|flac","rate":16000,"language":...},"request":{"model_name":"bigmodel","enable_itn":true,"enable_punc":true,"enable_nonstream":true}}`), then one audio-only frame with the file bytes, then an empty last-packet frame, and read the JSON server response for the transcript. Copy the header constants from `stt.py` in the checkout; do not reconstruct them from memory. Docs: https://www.volcengine.com/docs/6561/1354869

| Hermes behavior | How Claude does it |
|---|---|
| `text_to_speech_tool` with provider volcengine | curl call above; save mp3 to the requested path |
| `transcribe_audio` with provider volcengine | Python websockets script following `stt.py` |
| `pre_llm_call` voice instruction | when the output will be spoken, keep replies to 2 to 4 sentences, no tables or code blocks |

## Setup
1. Create a Speech API key in the Volcengine speech console (https://console.volcengine.com/speech, "API Key 管理"). An Ark LLM key (prefix `ark-`) is rejected with error 45000010 "Invalid X-Api-Key" per the README.
2. Export `VOLCENGINE_VOICE_API_KEY`.
3. For STT, `pip install websockets` (the plugin uses `websockets.connect` with `additional_headers`).

## Limits
- Paid third-party service; TTS is billed on the `text` characters and STT on audio duration (`volc.seedasr.sauc.duration`). Text and audio are sent to ByteDance/Volcengine servers.
- Hermes-specific routing (Discord voice messages, `/voice` commands, provider dispatch) is not applicable to Claude.
- The STT binary framing is summarized, not reproduced in full; the plugin source is the reference.
- Emotion tags work only with 2.0 voices and vary by voice per the README.
- No LICENSE file in the checkout; no upstream text copied (no `skills/` directory exists). Endpoints and payloads are stated per the plugin source and were not executed here.

## Source
- Catalog entry (reviewed commit): https://github.com/linxichen/hermes-volcengine-voice/tree/e3f8a305f95e133c0524b632207384d3a644e291
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/volcengine-voice.yaml
