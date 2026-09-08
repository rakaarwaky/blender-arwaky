#!/usr/bin/env bash
# scripts/uninstall.sh — Clean uninstaller for blender-arwaky (XDG Base Directory)
set -euo pipefail

BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/blender-arwaky"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/blender-arwaky"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/blender-arwaky"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Uninstalling blender-arwaky ==="

# Remove bin wrappers (full name + short alias + extras yang dibuat installer)
COMMANDS=("blender-arwaky" "ba" "blender-mcp")
for cmd in "${COMMANDS[@]}"; do
    if [ -L "$BIN_DIR/$cmd" ] || [ -f "$BIN_DIR/$cmd" ]; then
        rm -f "$BIN_DIR/$cmd"
        echo "✓ Removed $BIN_DIR/$cmd"
    fi
done

# Remove in-tree .venv symlink if it points to XDG
for name in ".venv" "venv"; do
    if [ -L "$PROJECT_DIR/$name" ]; then
        rm -f "$PROJECT_DIR/$name"
        echo "✓ Removed $PROJECT_DIR/$name symlink"
    fi
done

# Hapus data, config, dan cache (XDG) — config/cache selalu dibersihkan,
# data hanya saat --purge agar tidak menghapus data pengguna tanpa konfirmasi.
if [ -d "$CONFIG_DIR" ]; then
    rm -rf "$CONFIG_DIR"
    echo "✓ Removed $CONFIG_DIR"
fi
if [ -d "$CACHE_DIR" ]; then
    rm -rf "$CACHE_DIR"
    echo "✓ Removed $CACHE_DIR"
fi
if [[ "${1:-}" == "--purge" ]]; then
    if [ -d "$DATA_DIR" ]; then
        rm -rf "$DATA_DIR"
        echo "✓ Purged $DATA_DIR"
    fi
fi

echo "Uninstall complete."
