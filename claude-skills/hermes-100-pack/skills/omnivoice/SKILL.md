---
name: omnivoice
description: "Synthesize speech locally with Xiaomi's OmniVoice zero-shot TTS model (k2-fsa/OmniVoice) from Claude Code: multilingual text to speech, voice design from a description (\"female, low pitch, british accent\"), and voice cloning from a reference WAV plus transcript, written to wav/flac/ogg (mp3 via ffmpeg). Use when the user says \"read this aloud with OmniVoice\", \"generate a voiceover\", \"clone this voice\", \"make a TTS clip in Thai/Chinese/Japanese\", \"narrate this script locally\", or wants an offline TTS pipeline instead of a cloud API. Honors the same OMNIVOICE_* environment variables the Hermes plugin used."
---
# OmniVoice Local TTS

**Hermes original:** https://github.com/ThaungThanHan/hermes-omnivoice @ 21d2900 · tier: community · category: voice · license: no LICENSE file found (pyproject.toml declares Apache-2.0)
**Port class:** B · the plugin wraps the `omnivoice` Python package and a CLI wrapper; Claude can install the package and run the same `OmniVoice.from_pretrained(...).generate(...)` call in a script.

## What the Hermes plugin does
Registers a Hermes TTS provider named `omnivoice` (`provides_tts: [omnivoice]`) so Hermes' `text_to_speech` flow renders through OmniVoice. It reads `tts.omnivoice` from `~/.hermes/config.yaml` with `OMNIVOICE_*` env overrides, loads `k2-fsa/OmniVoice` once per session on `device: auto` / `dtype: float16`, maps a `voice` value to auto, `instruct:<description>`, `ref:<path>` or an existing audio path, and writes wav/flac/ogg with `soundfile` or mp3 through `ffmpeg`. It also installs an `omnivoice-hermes-tts` command-provider wrapper. No tools or hooks.

## Equivalent in Claude
1. Install into a virtualenv (heavy: torch, model download on first run). The plugin's extra pins `omnivoice @ git+https://github.com/k2-fsa/OmniVoice.git`; a PyPI release also exists, verified with `pip index versions omnivoice`: output `omnivoice (0.2.1)`. Prefer the git source the plugin used unless the user prefers PyPI.

```bash
python3 -m venv ~/.venvs/omnivoice && . ~/.venvs/omnivoice/bin/activate
pip install torch torchaudio soundfile "omnivoice @ git+https://github.com/k2-fsa/OmniVoice.git"
```

2. Resolve inputs the way `provider.py` does: `voice` of `auto`/`default`/`random`/empty means no instruct and no reference; `instruct:<text>` sets `instruct`; `ref:<path>` or an existing audio path sets `ref_audio` (with `ref_text` from `OMNIVOICE_REF_TEXT`, else the model's ASR, `OMNIVOICE_ASR_MODEL` default `openai/whisper-large-v3-turbo`); any other string is an `instruct`.
3. Run a script with the same call the plugin makes (argument names copied from `provider.py`; not run here, so verify against the installed package version):

```python
import os, soundfile as sf
from omnivoice import OmniVoice
ov = OmniVoice.from_pretrained(os.environ.get("OMNIVOICE_MODEL", "k2-fsa/OmniVoice"))
kw = {"text": TEXT, "num_step": int(os.environ.get("OMNIVOICE_NUM_STEP", 32)),
      "guidance_scale": float(os.environ.get("OMNIVOICE_GUIDANCE_SCALE", 2.0)),
      "speed": float(os.environ.get("OMNIVOICE_SPEED", 1.0))}
for k, e in [("language","OMNIVOICE_LANGUAGE"),("instruct","OMNIVOICE_INSTRUCT"),
             ("ref_audio","OMNIVOICE_REF_AUDIO"),("ref_text","OMNIVOICE_REF_TEXT")]:
    if os.environ.get(e): kw[k] = os.environ[e]
audio = ov.generate(**kw)
sf.write("out.wav", audio[0], ov.sampling_rate)
```

4. For mp3, run `ffmpeg -y -hide_banner -loglevel error -i out.wav out.mp3` (the plugin falls back to wav when ffmpeg is missing). Other generation knobs the plugin passes: `duration`, `t_shift` (0.1), `denoise` (true), `postprocess_output` (true), `layer_penalty_factor` (5.0), `position_temperature` (5.0), `class_temperature` (0.0), each with an `OMNIVOICE_<UPPER>` env name.

| Hermes piece | How Claude does it |
|---|---|
| `tts.provider: omnivoice` + `text_to_speech` | Run the script above with Bash |
| `omnivoice-hermes-tts --text-file --output --voice --speed --format` | Same script with CLI args |
| Model kept loaded for the session | Reloaded per script run unless the user keeps a Python REPL |

## Setup
1. Python 3.11+, a GPU recommended (CPU works but is slow per README). Install as in step 1.
2. Optional env: `OMNIVOICE_MODEL`, `OMNIVOICE_DEVICE`, `OMNIVOICE_DTYPE`, `OMNIVOICE_VOICE`, `OMNIVOICE_REF_AUDIO`, `OMNIVOICE_REF_TEXT`, `OMNIVOICE_INSTRUCT`, `OMNIVOICE_LANGUAGE`, `OMNIVOICE_NUM_STEP`, `OMNIVOICE_GUIDANCE_SCALE`, `OMNIVOICE_SPEED`, `OMNIVOICE_DURATION`, `OMNIVOICE_LOAD_ASR`, `OMNIVOICE_ASR_MODEL`.
3. Install `ffmpeg` for mp3 output.

## Limits
- Integration into a chat voice reply pipeline (Hermes `text_to_speech`, Telegram voice bubbles) is not replicated; the output is a file.
- `device`/`dtype` handling uses `omnivoice.utils.common.get_best_device` in the plugin; mirror only if that helper exists in the installed version.
- Not executed here; the `generate` signature is quoted from the plugin source and may differ across OmniVoice releases.
- Voice cloning: only clone voices the user has the right to use; do not impersonate people (README safety note). Follow the OmniVoice model license.
- No LICENSE file in the checkout, so no upstream text is copied.

## Source
- Catalog entry (reviewed commit): https://github.com/ThaungThanHan/hermes-omnivoice/tree/21d2900c392247dc52d706fee956f08dbfc3c5ea
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/omnivoice.yaml
