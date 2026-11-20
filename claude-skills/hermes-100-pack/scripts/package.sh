#!/usr/bin/env bash
# Build dist/skill-zips/<name>.zip (one per skill, folder at ZIP root — the shape claude.ai expects)
# and dist/hermes-100-pack.zip (everything).
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
rm -rf "$HERE/dist"; mkdir -p "$HERE/dist/skill-zips"
cd "$HERE/skills"
for d in */; do d=${d%/}; [ -f "$d/SKILL.md" ] || continue; (zip -qr "$HERE/dist/skill-zips/$d.zip" "$d" -x '*.DS_Store'); done
cd "$HERE/.." && zip -qr "$HERE/dist/hermes-100-pack.zip" "$(basename "$HERE")" -x "*/dist/*" '*.DS_Store'
ls "$HERE/dist/skill-zips" | wc -l; du -sh "$HERE/dist"
