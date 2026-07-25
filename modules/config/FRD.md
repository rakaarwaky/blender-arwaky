# FRD — Config Feature Module

## System Overview

The config module provides centralized application configuration management. It loads settings from `config.yaml`, supports dot-notation access, and provides the `contract_config_protocol` for dependency inversion.

## Functional Requirements

### FR-CFG-001: Load Configuration from YAML

- **Description**: Load and parse `config.yaml` from the project root
- **Input**: None (reads from filesystem)
- **Output**: dict[str, ConfigValue] (parsed config)
- **Business Rules**: Returns empty dict if file missing or malformed; caches after first load
- **Edge Cases**: File not found, invalid YAML, permission denied
- **Error Handling**: Returns empty dict on any parse error

### FR-CFG-002: Dot-notation Config Access

- **Description**: Retrieve nested config values using dot-separated paths
- **Input**: ConfigPath (e.g., "server.port"), ConfigValue (default)
- **Output**: ConfigValue (resolved value or default)
- **Business Rules**: Split path by "."; traverse nested dicts; return default if key missing
- **Edge Cases**: Empty path returns full config, missing intermediate key
- **Error Handling**: Returns default value for any missing key

### FR-CFG-003: Project Root Detection

- **Description**: Resolve the project root directory using multiple strategies
- **Input**: None (reads environment variables and filesystem)
- **Output**: Path (resolved project root)
- **Business Rules**: Resolution order: BLENDERMCP_CONFIG_PATH → BLENDER_MCP_ROOT → file proximity → XDG_CONFIG_HOME → CWD
- **Edge Cases**: Multiple root candidates, symlinks, non-existent paths
- **Error Handling**: Falls through to next strategy on failure

### FR-CFG-004: Thread-safe Singleton Access

- **Description**: Ensure config is loaded once and thread-safe for concurrent reads
- **Input**: None
- **Output**: dict[str, ConfigValue] (cached config)
- **Business Rules**: Uses threading.Lock for initialization; subsequent reads are lock-free
- **Edge Cases**: Concurrent first access, lock contention
- **Error Handling**: Standard locking behavior

### FR-CFG-005: contract_config_protocol

- **Description**: Abstract protocol for config access, enabling DI and testing
- **Input**: ConfigPath, ConfigValue (default)
- **Output**: ConfigValue
- **Business Rules**: Implementations must be stateless or thread-safe
- **Edge Cases**: Implementation not registered
- **Error Handling**: Delegated to implementation

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `load_config` | — | dict[str, ConfigValue] | Load config from YAML |
| `get_config` | ConfigPath, ConfigValue? | ConfigValue | Dot-notation access |
| `get_project_root` | — | Path | Resolve project root |
| `contract_config_protocol.get` | ConfigPath, ConfigValue? | ConfigValue | Contract protocol |

## Integration Points

- **Internal**: shared (taxonomy VOs: ConfigPath, ConfigValue, FilePath)
- **External**: Filesystem (config.yaml), Environment variables

## Non-functional Requirements

- Performance: Config access within 1ms (cached); first load within 100ms
- Reliability: Graceful fallback on missing/malformed config
- Thread Safety: Lock-protected singleton initialization

## Test Scenarios / QA Checklist

- [ ] Load config from valid YAML returns parsed dict
- [ ] Load config from missing file returns empty dict
- [ ] Load config from malformed YAML returns empty dict
- [ ] Get nested value with valid path returns correct value
- [ ] Get missing key returns default value
- [ ] Get empty path returns full config dict
- [ ] Project root detection resolves via BLENDER_MCP_ROOT
- [ ] Project root detection falls back to CWD
- [ ] Concurrent access is thread-safe

## Assumptions & Constraints

- Config file is YAML format
- Single config file per application instance
- Environment variables override file-based config

## Glossary

- **contract_config_protocol**: Contract (protocol) for configuration access
- **ConfigPath**: Dot-notation string for nested config keys (e.g., "server.port")
- **ConfigValue**: Union type for config values (str, int, dict, list, None)

## Reference

- PRD: [../PRD.md](../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
