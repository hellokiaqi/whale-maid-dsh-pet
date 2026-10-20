#!/usr/bin/env bash
# Install the whale-maid DSH pet into $DSH_HOME/pets/whale-maid.
# The pet plugin scans that directory once at host startup; restart DSH after.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PET_SOURCE="$REPO_ROOT/pet"
MANIFEST="$PET_SOURCE/pet.json"

if [ ! -f "$MANIFEST" ]; then
  echo "pet/pet.json not found under $REPO_ROOT" >&2
  exit 1
fi

if [ -z "${DSH_HOME:-}" ]; then
  if [ -d "$HOME/.dsh-beta" ]; then
    DSH_HOME="$HOME/.dsh-beta"
  elif [ -d "$HOME/.dsh" ]; then
    DSH_HOME="$HOME/.dsh"
  else
    echo "Cannot find DSH_HOME. Set DSH_HOME=/path/to/dsh-home and retry." >&2
    exit 1
  fi
fi

if [ ! -d "$DSH_HOME" ]; then
  echo "DSH home does not exist: $DSH_HOME" >&2
  exit 1
fi

DEST="$DSH_HOME/pets/whale-maid"
mkdir -p "$DEST"
cp -R "$PET_SOURCE/." "$DEST/"

IDLE_COUNT=$(find "$DEST/idle" -maxdepth 1 -name '*.webp' | wc -l | tr -d ' ')
HOP_COUNT=$(find "$DEST/hop" -maxdepth 1 -name '*.webp' | wc -l | tr -d ' ')
TRACK_COUNT=$(find "$DEST" -mindepth 1 -maxdepth 1 -type d ! -name previews | wc -l | tr -d ' ')
FRAME_COUNT=$(find "$DEST" -name '*.webp' | wc -l | tr -d ' ')
SIZE_MB=$(du -sm "$DEST" | awk '{print $1}')

echo ""
echo "Installed: $DEST"
echo "  tracks: $TRACK_COUNT  (idle $IDLE_COUNT frames, hop $HOP_COUNT frames)"
echo "  frames: $FRAME_COUNT"
echo "  size:   ${SIZE_MB} MB"
echo ""
echo "Next steps:"
echo "  1. Restart DSH (desktop tray -> Restart DSH Desktop, or restart your dsh web host)."
echo "  2. Open Settings -> Pet and choose the pet (or set petId: whale-maid in the profile patch)."
echo ""
