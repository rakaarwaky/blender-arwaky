#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
XDG_BIN_HOME="${XDG_BIN_HOME:-${HOME}/.local/bin}"
INSTALL_DIR="${XDG_BIN_HOME}"
VENV_DIR="${PROJECT_ROOT}/.venv"

cmds=(blender-arwaky blender-mcp)

ensure_uv_or_pip() {
  if [[ -d "${VENV_DIR}" && ! -x "${VENV_DIR}/bin/python3" ]]; then
    echo "[!] Detected broken venv at ${VENV_DIR}; recreating..."
    rm -rf "${VENV_DIR}"
  fi

  if command -v uv >/dev/null 2>&1; then
    echo "[*] Using uv for install"
    (cd "${PROJECT_ROOT}" && uv pip install -e .)
    return
  fi
  if [[ -x "${VENV_DIR}/bin/pip" ]]; then
    echo "[*] Using venv pip for install"
    "${VENV_DIR}/bin/pip" install -e "${PROJECT_ROOT}"
    return
  fi
  echo "[!] No uv or project venv found; creating ${VENV_DIR} ..."
  python3 -m venv "${VENV_DIR}"
  "${VENV_DIR}/bin/pip" install -e "${PROJECT_ROOT}"
}

ensure_install_dir() {
  mkdir -p "${INSTALL_DIR}"
}

write_wrapper() {
  local name="$1"
  local target="${VENV_DIR}/bin/${name}"
  local wrapper="${INSTALL_DIR}/${name}"

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
    *:${INSTALL_DIR}:*)
      ;;
    *)
      echo "[!] ${INSTALL_DIR} is not on PATH."
      echo "    Add this to ~/.bashrc or ~/.zshrc:"
      echo "    export PATH=\"${INSTALL_DIR}:\$PATH\""
      ;;
  esac
}

main() {
  echo "=== Blender Arwaky Installer ==="
  echo "Project Root: ${PROJECT_ROOT}"
  echo "Install Dir:  ${INSTALL_DIR}"
  echo "Venv Dir:     ${VENV_DIR}"
  echo

  ensure_uv_or_pip
  ensure_install_dir

  for cmd in "${cmds[@]}"; do
    write_wrapper "${cmd}"
  done

  echo
  echo "=== Installation Complete ==="
  echo "You can now run:"
  printf '  %s --help\n' "${cmds[@]}"
  warn_path
}

main "$@"
