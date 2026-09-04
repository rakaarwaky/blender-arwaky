#!/usr/bin/env bash
# scripts/install.sh — Standard install entrypoint for blender-arwaky
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/install/install_cli_wrappers.py" "$@"
