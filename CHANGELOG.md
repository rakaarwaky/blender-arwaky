# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2026-07-XX

### ⚠ BREAKING

- Removed legacy `BLENDER_MCP_` environment prefix (settings overrides) — use `BLENDERMCP_`.
- Removed `BLENDER_MCP_ROOT` workspace variable — use `BLENDERMCP_ROOT`.

### Added

- Built-in defaults tier; the settings file is now optional/override-only. A missing
  settings file is never fatal in any policy mode (falls back to defaults).
- Runtime overrides via `load(path, overrides=...)` (flag-gated behind `BLENDERMCP_CONFIG_V2`).
- Schema validation (`SETTINGS_SCHEMA`), 1 MiB size limit (`MAX_CONFIG_SIZE_BYTES`),
  `\.` path escaping, and strict `ConfigTypeError` — all flag-gated via
  `BLENDERMCP_CONFIG_V2` (default OFF; flips ON in v1.8.0, flag removed in v1.9.0).
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
