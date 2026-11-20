---
name: cjk_sanitizer
description: Strip stray Chinese (CJK unified ideographs, extension A, radicals, compatibility ideographs) and Cyrillic characters from text or files while preserving Korean Hangul and Japanese Kana, replicating the Hermes cjk_sanitizer output filter as an on-demand cleanup. Use it when the user says "remove the Chinese characters that leaked into this file", "clean CJK/Cyrillic glitches from this model output", "sanitize this transcript", "strip Russian letters from these logs", or complains that a Chinese-trained model (MiniMax, DeepSeek, GLM, Qwen) mixed scripts into English output. Also apply it to text Claude is about to save when the user has asked for this filter. Not a translation or language-detection tool.
---
# CJK Sanitizer

**Hermes original:** https://github.com/evanyudis/cjk_sanitizer @ 47d2a95 · tier: community · category: general · license: MIT
**Port class:** C · the regex cleanup is reproducible on any text or file, but the automatic `transform_llm_output` hook that rewrote every model reply has no Claude equivalent.

## What the Hermes plugin does
Registers one hook, `transform_llm_output`, that runs on every LLM response. It removes runs of characters in the ranges U+2E80-2EFF, U+3400-4DBF, U+4E00-9FFF, U+F900-FAFF (CJK) and U+0400-04FF (Cyrillic), collapses doubled spaces and 3+ newlines, and returns the cleaned text (or `None` when nothing changed). Hangul and Kana ranges are deliberately left alone. It registers no tools and reads no env vars. The README notes the hook always runs; prompt-based skipping was planned, not implemented.

## Equivalent in Claude
Apply the same regex with Python's standard library. Run it on a file the user names, or on text piped to stdin.

```bash
python3 -I - "$FILE" <<'PY'
import re, sys, pathlib
pat = re.compile(r'[⺀-⻿㐀-䶿一-鿿豈-﫿Ѐ-ӿ]+')
p = pathlib.Path(sys.argv[1]); t = p.read_text(encoding='utf-8')
c = pat.sub('', t); c = re.sub(r'  +', ' ', c); c = re.sub(r'\n{3,}', '\n\n', c)
if c != t:
    p.write_text(c.strip() + '\n', encoding='utf-8'); print('cleaned', p)
else:
    print('no change', p)
PY
```

| Hermes behaviour | How Claude does it |
|---|---|
| Hook on every model reply | Not available; run the script on request, or on files Claude writes when the user asked for the filter |
| Strip CJK + Cyrillic runs | same regex as above (copied from `__init__.py`) |
| Preserve Hangul / Kana | same, those ranges are not in the pattern |
| Collapse whitespace | same two `re.sub` calls |
| No-op when clean | script prints `no change` |

Before running on a file, confirm with the user if the file legitimately contains Chinese or Russian text (language study, bilingual docs); the plugin had no such guard.

## Setup
None.

## Limits
- No automatic post-processing of Claude's own replies: Claude Code hooks (PreToolUse, PostToolUse, Stop and others) do not rewrite assistant text, so the "silent on every response" behaviour is not replicated. Instead Claude can avoid emitting those scripts when asked.
- The plugin strips characters blindly; so does this script. Chinese or Russian content the user wanted is destroyed. Back up the file first (`cp FILE FILE.bak`).
- Japanese Kanji share the CJK unified block and are removed, as in the plugin (README states this).
- No upstream skills/ directory exists to copy; MIT license permits quoting the regex, which is done above.

## Source
- Catalog entry (reviewed commit): https://github.com/evanyudis/cjk_sanitizer/tree/47d2a95c89e827fef6ea0bacbff433c6dc980351
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/cjk_sanitizer.yaml
