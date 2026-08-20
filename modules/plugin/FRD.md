# FRD — Plugin & External Provider Feature

## System Overview
The Plugin module is the single authority for managing external Blender addon lifecycles (specifically MPFB2 and generic plugins) and provider-specific asset packs. It isolates external dependencies, handles secure downloading/verification, and manages Blender extension enablement.

## Functional Requirements

### FR-001: Plugin Discovery, Download, and Installation
- **Description**: List known plugins, download archives with SHA256 verification, and install to Blender extensions path.
- **Input**: `plugin_id`, `source_url`, `sha256`, `cache_path`, `blender_path`.
- **Output**: `UnifiedEnvelope` with lifecycle state and installation path.
- **Business Rules**: Archives MUST match provided SHA256 hash before extraction. Installation respects Blender extension path policies.
- **Edge Cases**: SHA256 mismatch; disk full during extraction; invalid plugin ID.
- **Error Handling**: `security_violation` for hash mismatch; `validation_error` for missing URL; `execution_error` for Blender-side failures.

### FR-002: Plugin Enablement and Provider Actions
- **Description**: Activate/deactivate plugins via Blender API and invoke provider-specific character generators.
- **Input**: `plugin_id`, `extension_id`, `character_name`, `seed`.
- **Output**: `UnifiedEnvelope` confirming state change or character creation.
- **Business Rules**: Enablement verifies compatibility. Provider actions (e.g., `create_character`) strictly mapped to explicit catalog entries. Arbitrary Python source never accepted.
- **Edge Cases**: Blender version incompatibility; external addon API changes; attempting to enable already enabled plugin.
- **Error Handling**: `state_error` for duplicate enablement; `execution_error` for addon crashes; `unsupported` for incompatible plugins.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `list_plugins` | None | `UnifiedEnvelope` | List known plugins and states |
| `download_plugin` | `plugin_id`, `source_url`, `sha256` | `UnifiedEnvelope` | Download and verify archive |
| `install_plugin` | `plugin_id`, `cache_path`, `blender_path` | `UnifiedEnvelope` | Extract and register extension |
| `enable_plugin` | `plugin_id`, `extension_id` | `UnifiedEnvelope` | Activate via Blender API |
| `disable_plugin` | `plugin_id`, `extension_id` | `UnifiedEnvelope` | Deactivate via Blender API |
| `create_character` | `plugin_id`, `name` | `UnifiedEnvelope` | Invoke provider character generator |
| `randomize_character` | `plugin_id`, `name`, `seed` | `UnifiedEnvelope` | Invoke provider randomization |

## Integration Points

- **3rd Party**: External Addon APIs (e.g., MPFB2 Python API).
- **Internal**: `config` (cache paths), `security` (archive extraction), `gateway` (Blender-side enablement), `launcher` (process state).

## Non-functional Requirements (Detailed)

- **Performance**: SHA256 verification streams data to avoid memory exhaustion on large archives.
- **Security**: Strict SHA256 enforcement. Archive extraction delegated to `security` to prevent traversal.
- **Scalability**: Incompatible plugins hidden from MCP/CLI discovery to prevent agent hallucination.

## Test Scenarios / QA Checklist

- [ ] Verify download rejects archives with SHA256 mismatch (`security_violation`).
- [ ] Verify installation respects Blender extension path policies.
- [ ] Verify enablement gracefully handles Blender version incompatibility.
- [ ] Verify provider actions map to explicit catalog entries, not raw code.

## Assumptions & Constraints

- Plugin execution relies on the external addon's API; if the addon crashes, Gateway returns `execution_error`.
- Core Blender operations remain owned by Object/Scene modules.

## Glossary

- **MPFB2**: MakeHuman/MakeHuman Proxy for Blender 2, a specific external character generation addon.
- **Extension Path**: Blender's designated directory for installed addons and extensions.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `config`, `security`, `gateway`, `launcher`
