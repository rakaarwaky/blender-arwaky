# Changelog

All notable changes to **Blender Arwaky** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `tests/addon/` test suite with mock `bpy` for testing the Blender addon
  without requiring an actual Blender installation
- `CHANGELOG.md` for tracking notable changes between releases
- `SECURITY.md` vulnerability disclosure policy
- `.pre-commit-config.yaml` for local lint/format/type/security enforcement
- `.editorconfig` for cross-IDE consistency
- `bandit.yaml` for project-specific security scan configuration
- `MANIFEST.in` to ensure `py.typed`, YAML, and config files are included
  in the sdist
- `Dockerfile` for containerized MCP server deployment
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, issue & PR templates
- GitHub Actions CI testing on Python 3.10, 3.11, 3.12, 3.13
- Coverage configuration in `pyproject.toml` with per-layer thresholds
- Pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`,
  `@pytest.mark.functional`, `@pytest.mark.addon`, `@pytest.mark.slow`)
  applied to existing test classes
- `scripts/README.md` index documenting helper scripts and naming
  conventions
- `scripts/install/install_cli_wrappers.py` — cross-platform Python
  replacement for the previous `install_cli.sh` Bash script; generates
  `blender-cli` and `blender-arwaky` wrappers in `~/.local/bin` on
  Windows, macOS, and Linux
- `scripts/blender/launch_blender_runtime.py` — cross-platform Python
  replacement for the previous `launch_blender.sh` Bash script

### Changed
- Renamed project from `blender-mcp` to `blender-arwaky`
- Author updated to **Raka Arwaky** (originally by Siddharth Ahuja)
- Telemetry data directory changed from `BlenderMCP` to `BlenderArwaky`
- Default XDG config path changed from `~/.config/blender-mcp` to
  `~/.config/blender-arwaky`
- Display labels in the Blender addon UI now show "Blender Arwaky"
- Reorganized `scripts/` into purpose-grouped subdirectories
  (`build/`, `blender/`, `install/`) and applied 3-word naming; see
  `scripts/README.md` for the new layout

### Removed
- `src/patched.py` — contained a hardcoded developer path and mutated
  source files at runtime. This is a security blocker and is replaced by
  the proper release/deployment process.
- `scripts/run-blender-mcp.js` — platform-specific Windows launcher; use
  `scripts/install/install_cli_wrappers.py` or the cross-platform
  `uv run blender-arwaky` command instead.
- `scripts/keep_alive.py` — duplicate of `run_headless.py`; the unified
  `scripts/blender/run_server_headless.py` is now the single entry point.
- `scripts/install_cli.sh` and `scripts/launch_blender.sh` — replaced by
  cross-platform Python equivalents.

### Fixed
- Test markers are now applied so `pytest -m unit` correctly runs only
  unit tests, `pytest -m "not slow"` properly skips slow tests, etc.

### Security
- Removed hardcoded `/home/raka/...` paths from `src/patched.py`
- Added `SECURITY.md` with vulnerability disclosure policy

---

## [1.6.5] - 2026-06-02

### Added
- Blender addon with TCP server (auto-start, UI panel, API key management)
- 5 universal MCP tools (execute_command, list_commands, read_skill_context,
  check_status, health_check)
- 20+ actions across scene, object, render, viewport, I/O, asset, generation
  domains
- 4 asset providers: Poly Haven, Sketchfab, Hyper3D Rodin, Hunyuan3D
- AI 3D generation with async job management
- Clean AES 6-layer architecture (surfaces → agent → capabilities →
  infrastructure → contract → taxonomy) with full dependency inversion
- Architecture enforcement via `auto_linter.config.python.yaml`
- Privacy-focused, opt-in anonymous telemetry (UUID-based, local JSONL)
- Cross-platform installer (`scripts/install_cli.sh`)
- Auto-discovery addon install for Blender 5.x extensions
- CI/CD pipeline with multi-Python testing, signed releases, and PyPI publish

### Notes
- Originally based on BlenderMCP by Siddharth Ahuja
- Extended and rebranded to **Blender Arwaky** by Raka Arwaky
- MIT License

[Unreleased]: https://github.com/rakaarwaky/blender-arwaky/compare/v1.6.5...HEAD
[1.6.5]: https://github.com/rakaarwaky/blender-arwaky/releases/tag/v1.6.5
