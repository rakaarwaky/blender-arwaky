#!/usr/bin/env bash
# scripts/install/install.sh — XDG compliant installer for blender-arwaky
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APP_ID="blender-arwaky"

# XDG Base Directory paths (consistent with lint, qwen-web, vision)
XDG_BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
XDG_DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/$APP_ID"
XDG_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/$APP_ID"
XDG_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/$APP_ID"
XDG_STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/$APP_ID"
VENV_DIR="$XDG_DATA_DIR/venv"

cmds=(blender-arwaky ba blender-mcp)

ensure_venv() {
  if [[ -d "${VENV_DIR}" && ! -x "${VENV_DIR}/bin/python3" ]]; then
    echo "[!] Detected broken venv at ${VENV_DIR}; recreating..."
    rm -rf "${VENV_DIR}"
  fi

  if [[ ! -d "${VENV_DIR}" ]]; then
    echo "[*] Creating virtual environment at ${VENV_DIR} ..."
    mkdir -p "${VENV_DIR}"
    python3 -m venv "${VENV_DIR}"
  fi

  if command -v uv >/dev/null 2>&1; then
    echo "[*] Using uv for install from ${PROJECT_ROOT}"
    (cd "${PROJECT_ROOT}" && uv pip install --python "${VENV_DIR}/bin/python3" -e .)
    return
  fi
  if [[ -x "${VENV_DIR}/bin/pip" ]]; then
    echo "[*] Using venv pip for install from ${PROJECT_ROOT}"
    "${VENV_DIR}/bin/pip" install -e "${PROJECT_ROOT}"
    return
  fi
  echo "[!] No usable installer found."
  return 1
}

ensure_xdg_dirs() {
  mkdir -p "${XDG_BIN_DIR}"
  mkdir -p "${XDG_CONFIG_DIR}"
  mkdir -p "${XDG_CACHE_DIR}"
  mkdir -p "${XDG_STATE_DIR}/log"
}

write_wrapper() {
  local name="$1"
  local target="${VENV_DIR}/bin/${name}"
  local wrapper="${XDG_BIN_DIR}/${name}"

  if [[ ! -x "${target}" ]]; then
    echo "[!] Missing entrypoint: ${target}"
    return 1
  fi

  cat > "${wrapper}" <<EOF
#!/usr/bin/env bash
exec "${target}" "\$@"
EOF
  chmod +x "${wrapper}"
  echo "[+] Installed ${wrapper} -> ${target}"
}

warn_path() {
  case ":${PATH}:" in
    *:${XDG_BIN_DIR}:*)
      ;;
    *)
      echo "[!] ${XDG_BIN_DIR} is not on PATH."
      echo "    Add this to ~/.bashrc or ~/.zshrc:"
      echo "    export PATH=\"${XDG_BIN_DIR}:\$PATH\""
      ;;
  esac
}

main() {
  echo "=== Blender Arwaky Installer (XDG) ==="
  echo "Project Root: ${PROJECT_ROOT}"
  echo "Bin Dir:      ${XDG_BIN_DIR}"
  echo "Data Dir:     ${XDG_DATA_DIR}"
  echo "Config Dir:   ${XDG_CONFIG_DIR}"
  echo "Cache Dir:    ${XDG_CACHE_DIR}"
  echo "State Dir:    ${XDG_STATE_DIR}"
  echo "Venv Dir:     ${VENV_DIR}"
  echo

  ensure_venv
  ensure_xdg_dirs

  for cmd in "${cmds[@]}"; do
    write_wrapper "${cmd}"
  done

  echo
  echo "=== Installation Complete ==="
  echo "You can now run:"
  printf '  %s --help\n' "${cmds[@]}"
  echo
  echo "Run 'blender-arwaky init' to setup workspace symlinks."
  warn_path
}

main "$@"
