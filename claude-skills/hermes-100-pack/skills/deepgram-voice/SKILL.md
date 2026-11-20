---
name: deepgram-voice
description: Text-to-speech with Deepgram Aura 2 and speech-to-text with Deepgram Nova by calling the Deepgram REST API (/v1/speak, /v1/listen) directly with curl or Python. Use when the user asks to "read this aloud", "turn this text into an mp3/wav", "make a voiceover", "transcribe this audio/recording/meeting", "what does this voice memo say", mentions Deepgram, Aura, Nova, or has a DEEPGRAM_API_KEY.
---
# Deepgram Voice (Aura TTS + Nova STT)

**Hermes original:** https://github.com/jaysonsantos/hermes-deepgram-voice-plugin @ c1d8ef2 · tier: community · category: voice · license: MIT
**Port class:** B · the plugin calls two documented Deepgram REST endpoints with `requests`; Claude can make the same calls.

## What the Hermes plugin does
Registers a Hermes `TTSProvider` ("deepgram", Aura 2 voices) and a `TranscriptionProvider` ("deepgram", Nova models). It lists no tools of its own; Hermes voice features route through it. Per the plugin source TTS is `POST {base}/speak` returning raw audio (mp3, ogg/opus, wav, flac), STT is `POST {base}/listen` with the audio file as the request body, and the transcript is read from `results.channels[].alternatives[0]` (preferring `paragraphs.transcript`). Language is auto-detected unless a language is forced.

## Equivalent in Claude
Env vars (same names): `DEEPGRAM_API_KEY` (required), `DEEPGRAM_TTS_BASE_URL`, `DEEPGRAM_STT_BASE_URL` (optional overrides). Default base URL copied from the source: `https://api.deepgram.com/v1`. Auth header: `Authorization: Token $DEEPGRAM_API_KEY`.

TTS (default voice `aura-2-thalia-en`; others in the source: `aura-2-asteria-en`, `aura-2-luna-en`, `aura-2-orion-en`, `aura-2-arcas-en`, `aura-2-zeus-en`; max text length 4000):
```bash
curl -s -X POST "https://api.deepgram.com/v1/speak?model=aura-2-thalia-en&encoding=mp3" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" -H "Content-Type: application/json" \
  -d '{"text":"Hello from Claude."}' -o out.mp3
```
Format query params from the source: mp3 -> `encoding=mp3`; ogg/opus -> `encoding=opus&container=ogg`; wav -> `encoding=linear16&container=wav`; flac -> `encoding=flac`. Optional: `speed`, `sample_rate`, `bit_rate`. A non-200 status carries `err_msg` / `message` in the JSON body.

STT (default model `nova-3`; also `nova-2`, `enhanced`, `base`):
```bash
curl -s -X POST "https://api.deepgram.com/v1/listen?model=nova-3&smart_format=true&punctuate=true&detect_language=true" \
  -H "Authorization: Token $DEEPGRAM_API_KEY" -H "Content-Type: audio/mpeg" \
  --data-binary @recording.mp3
```
Set `Content-Type` to the file's MIME type (`audio/wav`, `audio/mpeg`, `application/octet-stream` as fallback). To force a language, replace `detect_language=true` with `language=<code>` (e.g. `en`, `de`, `pt-BR`). Optional booleans the plugin passes through: `diarize`, `paragraphs`, `utterances`, `numerals`, `dictation`. Extract the text with `jq -r '.results.channels[].alternatives[0] | (.paragraphs.transcript // .transcript)'` and join channels with a space.

| Hermes capability | How Claude does it |
|---|---|
| `tts` provider synthesize | `/speak` call above, write response body to the requested file |
| `stt` transcribe | `/listen` call above, parse JSON |
| list voices / models | Static lists above (from the plugin source) |

## Setup
1. Create an API key at `https://console.deepgram.com/`.
2. `export DEEPGRAM_API_KEY=...`
3. `curl` and `jq` (or Python `requests`) available.

## Limits
- Hermes `config.yaml` sections (`tts.deepgram`, `stt.deepgram`) are replaced by passing query params explicitly.
- Hermes voice-mode wiring (live voice sessions, platform voice replies) is not part of this port.
- Deepgram is a paid service; audio and text are sent to Deepgram.
- Timeouts in the plugin (60 s TTS, 120 s STT) are advisory; use `curl --max-time` for large files.
- Not verified in this port: current Aura/Nova model names on Deepgram's side.

## Source
- Catalog entry (reviewed commit): https://github.com/jaysonsantos/hermes-deepgram-voice-plugin/tree/c1d8ef24ffe3606976ba52d635e684f5566ed04c
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/deepgram-voice.yaml
