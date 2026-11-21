#!/usr/bin/env bash
# Copy pack skills into ~/.claude/skills (Claude Code personal skills).
# Usage: install-claude-code.sh [--only A,B,C,D]
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
ONLY=""
[ "${1:-}" = "--only" ] && ONLY="${2:-}"
mkdir -p "$DEST"
n=0
while IFS= read -r line; do
  name=$(printf '%s' "$line" | python3 -c 'import sys,json;print(json.loads(sys.stdin.read())["name"])')
  cls=$(printf '%s' "$line" | python3 -c 'import sys,json;print(json.loads(sys.stdin.read())["port_class"])')
  if [ -n "$ONLY" ] && ! printf '%s' "$ONLY" | tr ',' '\n' | grep -qx "$cls"; then continue; fi
  src="$HERE/skills/$name"
  [ -f "$src/SKILL.md" ] || { echo "skip $name (no SKILL.md)"; continue; }
  rm -rf "$DEST/hermes-$name"; cp -R "$src" "$DEST/hermes-$name"
  # the directory name becomes the /slash-command; keep the frontmatter name in sync
  python3 - "$DEST/hermes-$name/SKILL.md" "hermes-$name" <<'PY'
import sys,re
p,new=sys.argv[1],sys.argv[2]; s=open(p).read()
s=re.sub(r'^name:.*$', 'name: '+new, s, count=1, flags=re.M); open(p,'w').write(s)
PY
  n=$((n+1))
done < "$HERE/data/port_status.jsonl"
echo "installed $n skills into $DEST (prefixed hermes-)"
