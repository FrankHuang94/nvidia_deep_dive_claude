#!/usr/bin/env bash
# Render diagrams/src/*.{d2,dot,mmd} -> assets/diagrams/*.svg (explicit white background).
set -euo pipefail
cd "$(dirname "$0")/../.."
mkdir -p assets/diagrams
shopt -s nullglob
n=0
for f in diagrams/src/*.d2; do
  id=$(basename "$f" .d2)
  d2 --theme 0 --pad 24 --layout elk "$f" "assets/diagrams/$id.svg" >/dev/null 2>&1 || d2 --theme 0 --pad 24 "$f" "assets/diagrams/$id.svg"
  n=$((n+1))
done
for f in diagrams/src/*.dot; do
  id=$(basename "$f" .dot)
  dot -Tsvg -Gbgcolor=white "$f" -o "assets/diagrams/$id.svg"
  n=$((n+1))
done
PCFG=$(mktemp)
if [ -x /opt/pw-browsers/chromium ]; then
  echo '{"executablePath":"/opt/pw-browsers/chromium","args":["--no-sandbox","--disable-setuid-sandbox"]}' > "$PCFG"
else
  echo '{"args":["--no-sandbox","--disable-setuid-sandbox"]}' > "$PCFG"
fi
for f in diagrams/src/*.mmd; do
  id=$(basename "$f" .mmd)
  ./node_modules/.bin/mmdc -q -p "$PCFG" -b white -i "$f" -o "assets/diagrams/$id.svg"
  n=$((n+1))
done
rm -f "$PCFG"
echo "diagrams: rendered $n"
