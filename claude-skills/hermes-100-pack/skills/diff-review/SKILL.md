---
name: diff-review
description: Scan a git diff for the Hermes diff-review plugin's six lint checks (debug print() and console.log calls, possible hardcoded secrets, bare except clauses, broad except Exception catches, unresolved TODO/FIXME/HACK/XXX) and report per-file added/removed counts. Use it whenever the user says "review my diff", "check my changes before I commit", "scan this diff for debug prints or secrets", "run diff_review against origin/main", "what did I leave in this branch", or pastes a unified diff and asks what is wrong with it. Works from Claude Code with git in PATH; also accepts raw diff text.
---
# Diff Review

**Hermes original:** https://github.com/sprmn24/hermes-plugin-diff-review @ f238271 · tier: community · category: tools · license: no LICENSE file found (README text says MIT)
**Port class:** B · the tool is `git diff` plus six regexes over added lines; Claude runs the same commands itself.

## What the Hermes plugin does
Registers one tool, `diff_review` (toolset `diff_review`), with optional arguments `base` (default `HEAD`), `target` (e.g. `origin/main`) and `diff_text` (raw unified diff; skips git). It runs `git diff <base> [<target>]` with a 30 s timeout, parses `diff --git` / `+++ b/` / `@@` headers to track file paths and line numbers, counts added and removed lines per file, and flags each added line matching one of six patterns. Output is JSON: `status`, `files_changed`, `total_added`, `total_removed`, `files[]`, `warnings[] {file,line,issue}`, `warning_count`. Requires only git; no env vars.

## Equivalent in Claude
1. Get the diff exactly as the plugin does: `git diff HEAD` (working tree vs HEAD), or `git diff HEAD origin/main` when the user names a target. If the user pasted a diff, save it to a temp file and skip git.
2. Scan added lines with the same patterns (copied from `tools.py`):

| Regex (applied to the line without its leading `+`) | Issue label |
|---|---|
| `print\s*\(` | debug print statement |
| `console\.log\s*\(` | console.log statement |
| `(?i)(password|secret|api_key|token)\s*=\s*['"][^'"]+['"]` | possible hardcoded secret |
| `except\s*:` | bare except clause |
| `except\s+Exception\s*:` | broad Exception catch |
| `TODO|FIXME|HACK|XXX` | unresolved TODO/FIXME |

Reference implementation (stdlib only; reads a diff from stdin):

```bash
git diff HEAD | python3 -I - <<'PY'
import re, sys, json
P=[(r"print\s*\(","debug print statement"),(r"console\.log\s*\(","console.log statement"),
   (r"(?i)(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]","possible hardcoded secret"),
   (r"except\s*:","bare except clause"),(r"except\s+Exception\s*:","broad Exception catch"),
   (r"TODO|FIXME|HACK|XXX","unresolved TODO/FIXME")]
files=[];cur=None;warn=[];ln=0
for raw in sys.stdin.read().splitlines():
    if raw.startswith("diff --git"):
        if cur: files.append(cur)
        cur={"path":"","added":0,"removed":0}; continue
    if raw.startswith("+++ b/") and cur is not None: cur["path"]=raw[6:]; continue
    if raw.startswith("@@"):
        m=re.search(r"\+(\d+)",raw); ln=int(m.group(1))-1 if m else ln; continue
    if cur is None: continue
    if raw.startswith("+") and not raw.startswith("+++"):
        ln+=1; cur["added"]+=1
        for pat,label in P:
            if re.search(pat,raw[1:]): warn.append({"file":cur["path"],"line":ln,"issue":label})
    elif raw.startswith("-") and not raw.startswith("---"): cur["removed"]+=1
    elif not raw.startswith(("---","+++")): ln+=1
if cur: files.append(cur)
print(json.dumps({"status":"ok" if files else "no_diff","files_changed":len(files),
  "total_added":sum(f["added"] for f in files),"total_removed":sum(f["removed"] for f in files),
  "files":files,"warnings":warn,"warning_count":len(warn)},indent=2))
PY
```

| Hermes tool call | How Claude does it |
|---|---|
| `diff_review()` | `git diff HEAD` piped to the script |
| `diff_review(target="origin/main")` | `git diff HEAD origin/main` piped to the script |
| `diff_review(base="main", target="feature")` | `git diff main feature` piped to the script |
| `diff_review(diff_text=...)` | write text to a file, `cat FILE` piped to the script |

3. Summarize warnings grouped by file, then offer to fix them. Treat "possible hardcoded secret" hits as needing a human look; the regex is naive (per source) and matches test fixtures too.

## Setup
None (git must be in PATH, as the plugin requires).

## Limits
- The plugin only reads; it never edits files. Keep that default and ask before fixing.
- Pattern set is fixed and shallow (no language awareness, no entropy check for secrets). Claude may add its own review on top, but label it as beyond the plugin.
- The repository has no LICENSE file at the reviewed commit, so no upstream text is copied; the regexes above are quoted as facts of behaviour.
- Line numbers follow the plugin's hunk arithmetic and can drift on multi-hunk files exactly as the original does.

## Source
- Catalog entry (reviewed commit): https://github.com/sprmn24/hermes-plugin-diff-review/tree/f238271c1f63ac59b43b99290ec6143f50b780f3
- Catalog YAML: https://github.com/NousResearch/hermes-agent/blob/bb0c2303664edc01960fdbbb148b47acdbe553ce/plugin-catalog/diff-review.yaml
