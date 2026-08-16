# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2026-08-15

### Added

- Wave 2 core capability modules for Geometry Nodes, animation/keyframes, and mesh topology/UV operations, exposed through canonical dispatcher actions and verified in Blender 4.0.2 background smoke tests.
- Wave 3 core capability modules for compositor graphs, VSE strips/sequence rendering, and rigid body/cloth physics, including bounded handlers and shared job metadata for long-running operations.
- Wave 4 advanced simulation controls for particle systems, effector-based force fields, fluid domain baseline configuration, and bounded simulation cache inspection.
- Wave 5 rigging and deformation foundations for armature inspection, pose-bone transforms, allow-listed constraints, shape keys, and deformation state.
- CI coverage for `develop` and `main` with Ruff, Python syntax compilation, multi-version pytest, cross-feature integration tests, and distributable artifact verification.
- Local `scripts/ci.sh` gates for linting, tests, addon packaging, and Python distribution builds with runtime-state cleanup.

### Changed

- Full migration removes the duplicate `execute_code` command vocabulary; `execute_blender_code` is now the sole canonical action and addon wire command.
- Gateway connection errors use canonical `BlenderConnectionExhaustedError` and `BlenderConnectionFailureError` names without compatibility aliases.
- MCP/CLI onboarding points to the embedded `help` surface instead of the removed `read_skill_context` path.
- Pytest discovery and coverage now target the actual `modules/` and `blender_mcp_addon/` source layout.
- Release and contributor workflows now use the current `develop` branch and repository paths.

### Fixed

- Removed test lint violations without changing HTTP adapter keyword contracts or pytest fixture discovery.
- Removed the obsolete pytest.ini shadow so pyproject pytest-cov settings and coverage artifacts are applied consistently in local and remote CI.

## [1.7.0] - 2026-07-XX

### ⚠ BREAKING

- Removed legacy `BLENDER_MCP_` environment prefix (settings overrides) — use `BLENDERMCP_`.
- Removed `BLENDER_MCP_ROOT` workspace variable — use `BLENDERMCP_ROOT`.

### Added

- Built-in defaults tier; the settings file is now optional/override-only. A missing
  settings file is never fatal in any policy mode (falls back to defaults).
- Runtime overrides via `load(path, overrides=...)`, always validated and applied after file and environment sources.
- Schema validation (`SETTINGS_SCHEMA`), 1 MiB size limit (`MAX_CONFIG_SIZE_BYTES`),
  `\\.` path escaping, and strict `ConfigTypeError` are always enforced. The
  `BLENDERMCP_STRICT` feature flag was removed; policy mode only controls whether
  validation failures raise or become explicit warnings.
- Settings metadata is now populated (`ConfigMetadata`: source, exists, override count,
  parse/validation warnings). Domain events are emitted (`SettingsLoadedEvent`,
  `SettingsReloadEvent`, `SettingsValidationWarningEvent`, `WorkspaceResolvedEvent`)
  and exposed via `recent_events()` (50-event ring buffer).
- Workspace resolver: added `settings-file-location` strategy, result caching for process
  lifetime, and manifest-before-VCS project markers.
- Thread-safe singleton initialization with double-checked locking.

### Changed

- Environment override values are scalar-only (lists/mappings remain strings).
- Redaction rules: substring-based matching (e.g. `auth` also matches `author` — an
  accepted false positive); full-only redaction; extension via composition-root
  `extra_redaction_patterns` (not from settings).
- Workspace resolution no longer honors the legacy `BLENDER_MCP_ROOT` signal.

## [1.6.5] - 2026-07-XX

- Previous release baseline.
