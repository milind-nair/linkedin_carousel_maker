#!/usr/bin/env bash
set -euo pipefail

FONTS_DIR="$(dirname "$0")/../assets/fonts"
mkdir -p "$FONTS_DIR"

declare -a URLS=(
  "https://github.com/IBM/plex/raw/master/packages/plex-serif/fonts/complete/ttf/IBMPlexSerif-Regular.ttf"
  "https://github.com/IBM/plex/raw/master/packages/plex-serif/fonts/complete/ttf/IBMPlexSerif-Bold.ttf"
  "https://github.com/IBM/plex/raw/master/packages/plex-mono/fonts/complete/ttf/IBMPlexMono-Regular.ttf"
  "https://github.com/adobe-fonts/source-serif/raw/release/TTF/SourceSerif4-Regular.ttf"
  "https://github.com/googlefonts/caveat/raw/main/fonts/ttf/Caveat-Regular.ttf"
)

for url in "${URLS[@]}"; do
  filename="$(basename "$url")"
  out="$FONTS_DIR/$filename"
  if [[ -f "$out" ]]; then
    echo "exists: $filename"
    continue
  fi
  echo "downloading: $filename"
  curl -fsSL "$url" -o "$out"
done

echo "done. fonts in $FONTS_DIR"
ls -la "$FONTS_DIR"
