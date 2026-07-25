
# FRD — Config Feature Module

## System Overview

The config module provides centralized application configuration management for **blender-arwaky**. It loads settings from a primary YAML-based configuration source, supports dot-notation access, environment-based overrides, project root detection, cached singleton access, and provides a configuration access contract for dependency inversion.

This module is responsible for resolving configuration from deterministic sources, applying safe parsing rules, validating basic schema expectations, and exposing immutable configuration snapshots to other modules. It is used by server, MCP layer, asset providers, diagnostics tooling, and adapter components to resolve runtime settings such as network endpoints, timeouts, retry policies, provider credentials, logging behavior, and feature flags.

The module follows these principles:

- Safe YAML parsing that does not instantiate arbitrary objects
- Deterministic configuration precedence
- Graceful handling for missing configuration
- Explicit error handling for malformed or invalid configuration
- Thread-safe singleton initialization
- Immutable cached configuration snapshots
- Secret redaction in logs and diagnostic output
- Compatibility with legacy environment conventions where reasonable

## Functional Requirements

### FR-CFG-001: Load Configuration from YAML

- **Description**: Load and parse the primary YAML-based configuration source from the resolved configuration location
- **Input**: Optional explicit configuration location override; otherwise reads from filesystem and environment
- **Output**: Mapping of configuration keys to configuration values
- **Business Rules**:

  - Configuration loading follows this precedence order:

    1. Explicit runtime location override, if provided
    2. Product-specific configuration location environment override
    3. Primary configuration source inside resolved project root
    4. Platform-standard user configuration location
  - If no configuration source is found, built-in default configuration
  - Missing configuration source is not treated as fatal by default
  - YAML parsing must use a safe parsing mode only
  - Configuration snapshot must be immutable after loading
  - Configuration is cached after first successful load
  - Environment-based overrides are applied after file-based configuration is loaded
  - Environment variable values are parsed as typed scalars when possible:

    - boolean-like values become boolean
    - integer-like values become integer
    - float-like values become float
    - null-like values become empty value
    - list-like or mapping-like values may be parsed when safely detectable
    - otherwise value remains string
  - If a schema is registered, loaded configuration must be validated against schema
  - Secrets such as tokens, API keys, passwords, and credentials must be redacted in logs
  - Configuration load metadata should be available internally:

    - loaded source location
    - whether source existed
    - whether environment overrides were applied
    - parse warnings
    - validation warnings
  - Strict mode:

    - Malformed YAML raises a configuration parse error
    - Schema violation raises a configuration validation error
  - Permissive mode:

    - Malformed YAML logs a warning and returns default configuration
    - Schema violation logs a warning and continues where safe
  - Default mode is strict unless explicitly configured otherwise
  - Maximum configuration source size should be enforced
- **Edge Cases**: Source not found, invalid YAML, permission denied, empty source, duplicate mapping keys, unsupported YAML tags, oversized source, symlinked source, location pointing to directory instead of source, non-UTF-8 source, partially readable source, environment override conflict, schema unavailable, secret values present in configuration
- **Error Handling**:

  - Missing source: return empty or default configuration and log informational message
  - Permission denied: raise configuration load error in strict mode; log warning and return empty/default in permissive mode
  - Invalid YAML: raise configuration parse error in strict mode; return empty/default in permissive mode
  - Schema violation: raise configuration validation error in strict mode; log warning in permissive mode
  - Unsupported YAML tag: reject safely without executing constructor
  - Oversized source: raise configuration load error

### FR-CFG-002: Dot-notation Config Access

- **Description**: Retrieve nested configuration values using dot-separated paths
- **Input**: Dot-separated configuration path, optional default configuration value, optional expected type
- **Output**: Resolved configuration value or default
- **Business Rules**:
  - Split path by dot separator and traverse nested configuration mapping
  - Return default if key is missing
  - Return default if intermediate value is not a container where traversal expects container access
  - Empty path returns full configuration snapshot
  - Full configuration snapshot returned must be immutable or copied to prevent mutation
  - Numeric path segments may access list indexes when current node is a list
  - Out-of-range list index returns default
  - Escaped dot notation may be supported for keys containing literal dots
  - Path traversal must not mutate configuration state
  - Path traversal must be thread-safe
  - If expected type is provided and resolved value does not match, return default or raise configuration type error in strict mode
  - Explicit empty value stored in configuration is distinguishable from missing key only when implementation provides existence checking
  - Default value should not be mutated by configuration accessor
- **Edge Cases**: Empty path, missing intermediate key, path ending with separator, path starting with separator, repeated separators, whitespace in path, non-text path, list index out of range, list index on non-list, key containing dot, expected type mismatch, mutable default value, deeply nested path
- **Error Handling**:
  - Missing key: return default value
  - Invalid path format: return default in permissive mode; raise configuration path error in strict mode
  - Type mismatch: return default in permissive mode; raise configuration type error in strict mode
  - Mutating access: disallowed by returning immutable snapshot or copy

### FR-CFG-003: Project Root Detection

- **Description**: Resolve the project root directory using multiple deterministic strategies
- **Input**: None; reads environment and filesystem
- **Output**: Filesystem path representing resolved project root
- **Business Rules**:
  - Resolution order:
    1. Product-specific configuration location override
       - If value points to a configuration source, use its parent directory
       - If value points to a directory, use that directory
    2. Legacy configuration location override with same behavior as above
    3. Product-specific root override
    4. Legacy root override
    5. Upward proximity search from current working directory or module location
    6. Platform-standard user configuration location
    7. Current working directory
  - Upward proximity search looks for the first directory containing any recognized project marker concept:
    - primary configuration source
    - product-specific configuration source
    - project manifest
    - version control metadata
  - Marker priority should be:
    1. Primary configuration source
    2. Product-specific configuration source
    3. Project manifest
    4. Version control metadata
  - Resolved paths must be normalized
  - Symbolic links should be resolved safely without failing unnecessarily
  - Candidate directory must exist and be readable to be accepted
  - If an environment-provided path is invalid, log warning and fall through to next strategy
  - If multiple root candidates exist, first valid candidate according to resolution order wins
  - Project root detection should not create directories by default
  - If no valid candidate found, fallback to current working directory
  - If current working directory is inaccessible, raise configuration root resolution error
- **Edge Cases**: Multiple root candidates, symbolic links, non-existent paths, permission denied, network-mounted filesystem, case-insensitive filesystem, configuration location pointing to source versus directory, circular symbolic link, empty environment value, relative path, platform-specific remote path, deleted working directory
- **Error Handling**:
  - Invalid environment path: warn and fall through
  - Non-existent candidate: fall through
  - Permission denied: fall through if not final fallback
  - All strategies fail: return current working directory if accessible
  - Current working directory inaccessible: raise configuration root resolution error

### FR-CFG-004: Thread-safe Singleton Access

- **Description**: Ensure configuration is loaded once and thread-safe for concurrent reads
- **Input**: None
- **Output**: Cached immutable configuration snapshot
- **Business Rules**:
  - Uses internal synchronization mechanism for initialization
  - Initialization uses double-checked initialization pattern to avoid unnecessary contention after configuration is loaded
  - Subsequent reads should be lock-free or use immutable snapshot access
  - Cached configuration must be immutable or protected from mutation
  - Configuration snapshot replacement during reload must be atomic
  - Failed configuration load must not cache partial or invalid state
  - In strict mode, failed load may propagate error to caller
  - In permissive mode, failed load may cache empty or default snapshot if safe
  - Reload operation must acquire initialization synchronization
  - Reload operation must replace old snapshot atomically
  - Concurrent reads during reload must continue using previous valid snapshot until replacement completes
  - Singleton instance must be safe across threads
- **Edge Cases**: Concurrent first access, synchronization contention, reload during read, initialization failure, repeated reload, configuration source changed externally, memory pressure, long-running load, exception during parsing
- **Error Handling**:
  - Standard synchronization behavior for thread coordination
  - Configuration parse error, configuration load error, or configuration validation error propagated according to strict or permissive mode
  - Failed reload retains previous valid snapshot unless strict mode requires failure propagation

### FR-CFG-005: Configuration Access Contract

- **Description**: Abstract contract for configuration access, enabling dependency inversion and testing
- **Input**: Dot-separated configuration path, optional default configuration value
- **Output**: Configuration value
- **Business Rules**:
  - Contract must expose at minimum a configuration retrieval operation
  - Contract may optionally expose:
    - existence check operation
    - typed retrieval helpers for string, integer, boolean, and float values
    - snapshot retrieval operation
  - Implementations must be stateless or thread-safe
  - Implementations must not expose mutable internal configuration state
  - Default implementation delegates to singleton configuration service
  - Test implementations may return in-memory mappings
  - If no implementation is explicitly registered, system should fall back to default configuration implementation
  - If explicit dependency injection mode is enabled and no implementation is registered, raise configuration provider registration error
  - Contract responses should follow same missing-key behavior as standard configuration access
  - Contract must not perform input/output operations on every retrieval unless explicitly implemented as remote configuration provider
  - Contract should support deterministic behavior for unit testing
- **Edge Cases**: Implementation not registered, invalid implementation, recursive delegation, missing key, type mismatch, immutable snapshot access, concurrent access, test double replacement, remote configuration latency if future provider is added
- **Error Handling**:
  - Delegated to implementation
  - Default implementation follows configuration module error policy
  - Missing implementation falls back to default unless explicit dependency injection mode requires error
  - Invalid implementation raises configuration provider error

## API Contract


| Operation                       | Input                                          | Output                                  | Description                                             |
| --------------------------------- | ------------------------------------------------ | ----------------------------------------- | --------------------------------------------------------- |
| Load configuration              | Optional explicit location                     | Mapping of configuration keys to values | Load configuration from YAML source and apply overrides |
| Reload configuration            | Optional explicit location                     | Mapping of configuration keys to values | Invalidate cache and reload configuration               |
| Retrieve configuration value    | Path, optional default, optional expected type | Configuration value                     | Dot-notation access                                     |
| Resolve project root            | —                                             | Filesystem path                         | Resolve project root                                    |
| Retrieve configuration metadata | —                                             | Configuration metadata                  | Return load source, override info, warnings             |
| Contract retrieval              | Path, optional default                         | Configuration value                     | Configuration access contract retrieval                 |
| Contract existence check        | Path                                           | Boolean                                 | Optional contract method to check key existence         |

## Integration Points

- **Internal**:

  - **blender-arwaky/modules/shared** for sharing vo,entity,error,event,utility,contract,constant
  - Logging subsystem: structured warnings, redaction, configuration load events
  - Server module: network endpoint, timeout, retry policy, authentication settings
  - Asset provider module: provider enablement, credentials, rate limit settings
  - Diagnostics tooling: configuration validation and status reporting
- **External**:

  - Filesystem: primary configuration source, optional local overrides, project marker concepts
  - Platform-standard user configuration location
  - Operating system path semantics across supported platforms

## Non-functional Requirements

- **Performance**:

  - Cached configuration access within one millisecond for typical in-memory lookups
  - First load within one hundred milliseconds for typical configuration source under normal storage conditions
  - Reload within one hundred milliseconds for typical configuration source under normal storage conditions
  - Dot-notation access should avoid repeated filesystem input/output
- **Reliability**:

  - Graceful fallback on missing configuration source
  - Deterministic behavior for missing keys
  - No partial configuration snapshot should be exposed after failed load
  - Reload failure should retain previous valid snapshot unless strict mode requires propagation
  - Configuration access should remain stable under concurrent reads
- **Thread Safety**:

  - Synchronization-protected singleton initialization
  - Atomic snapshot replacement during reload
  - Immutable or copy-protected configuration snapshots
  - Safe concurrent reads after initialization
- **Security**:

  - Use safe YAML parsing only
  - Do not execute arbitrary objects from YAML
  - Do not log secrets, tokens, passwords, API keys, or credentials
  - Warn if configuration source has overly permissive access permissions where detectable
  - Environment-based secrets must be handled carefully and redacted in diagnostics
  - Limit configuration source size to prevent memory exhaustion
  - Reject unsafe YAML tags
- **Observability**:

  - Log resolved configuration source concept
  - Log whether configuration source was found or missing
  - Log number of environment overrides applied, without printing secret values
  - Log validation warnings
  - Log parse warnings in permissive mode
  - Provide configuration metadata for diagnostics without exposing secrets
- **Portability**:

  - Support common desktop operating system path behavior
  - Support platform-standard user configuration location where applicable
  - Handle case-insensitive filesystems gracefully
  - Handle symbolic links and relative paths safely

## Test Scenarios / QA Checklist

- [ ]  Load configuration from valid YAML source returns parsed mapping
- [ ]  Load configuration from missing source returns empty or default configuration
- [ ]  Load configuration from malformed YAML raises parse error in strict mode
- [ ]  Load configuration from malformed YAML returns empty/default in permissive mode
- [ ]  Load configuration with unsafe YAML tag is rejected safely
- [ ]  Load configuration with duplicate keys behaves deterministically
- [ ]  Load configuration with empty source returns empty or default configuration
- [ ]  Load configuration with non-UTF-8 encoding raises or logs clear error
- [ ]  Load configuration larger than maximum size raises load error
- [ ]  Load configuration from explicit location override takes precedence
- [ ]  Load configuration from product-specific location override works
- [ ]  Load configuration from legacy location override works
- [ ]  Environment override overrides file-based value
- [ ]  Nested environment key convention maps correctly
- [ ]  Legacy environment prefix fallback works
- [ ]  Boolean, integer, float, null, list, and mapping environment values parse correctly
- [ ]  Secrets in configuration are redacted from logs
- [ ]  Secrets in environment overrides are not printed in diagnostics
- [ ]  Get nested value with valid path returns correct value
- [ ]  Get missing key returns default value
- [ ]  Get empty path returns full configuration snapshot
- [ ]  Full configuration snapshot returned is immutable or copied
- [ ]  Get with missing intermediate key returns default
- [ ]  Get with intermediate non-container returns default
- [ ]  Get with list index returns correct list item
- [ ]  Get with out-of-range list index returns default
- [ ]  Get with escaped dot key resolves literal dotted key if supported
- [ ]  Get with expected type returns value when type matches
- [ ]  Get with expected type returns default or raises in strict mode when type mismatches
- [ ]  Project root detection resolves via product-specific configuration location override
- [ ]  Project root detection resolves via legacy configuration location override
- [ ]  Project root detection resolves via product-specific root override
- [ ]  Project root detection resolves via legacy root override
- [ ]  Project root detection resolves via proximity markers
- [ ]  Project root detection prefers primary configuration source over version control metadata
- [ ]  Project root detection resolves via platform-standard user configuration location
- [ ]  Project root detection falls back to current working directory
- [ ]  Project root detection handles symlinked directories
- [ ]  Project root detection handles invalid environment path gracefully
- [ ]  Project root detection handles permission-denied candidate gracefully
- [ ]  Concurrent first access loads configuration only once
- [ ]  Concurrent access is thread-safe
- [ ]  Reload replaces configuration snapshot atomically
- [ ]  Reload failure retains previous valid snapshot in permissive or non-fatal mode
- [ ]  Reload failure propagates error in strict mode
- [ ]  Schema validation passes for valid configuration
- [ ]  Schema validation raises validation error for invalid configuration in strict mode
- [ ]  Schema validation logs warning for invalid configuration in permissive mode
- [ ]  Configuration access contract retrieval returns expected values
- [ ]  Configuration access contract existence check returns true/false correctly if implemented
- [ ]  Missing registered configuration provider falls back to default implementation
- [ ]  Explicit dependency injection mode raises provider registration error when provider missing
- [ ]  Configuration metadata reports loaded source and override status
- [ ]  Configuration metadata does not expose secret values

## Assumptions & Constraints

- Configuration source is YAML format
- YAML parsing uses safe loading concept only
- Single primary configuration source per application instance
- Environment-based overrides override file-based configuration
- Runtime overrides, if provided, override environment and file configuration
- Product-specific environment prefix is used for configuration overrides
- Legacy environment prefix may be supported for backward compatibility
- Configuration values must be JSON/YAML-compatible primitive types, lists, or mappings
- Configuration module does not fetch remote configuration by default
- Configuration module is not a secret manager, but may hold secrets provided by environment or source
- Secrets must be redacted from logs and diagnostic output
- Project root detection is best-effort and deterministic based on defined precedence
- Strict mode is recommended for production; permissive mode is intended for development or fallback scenarios

## Glossary

- **Configuration access contract**: Abstract contract for configuration access, enabling dependency inversion and test doubles
- **Configuration path**: Dot-notation string for nested configuration keys, for example "server.port"
- **Configuration value**: Union concept for configuration values: string, integer, float, boolean, mapping, list, empty value
- **Configuration snapshot**: Immutable configuration state after loading and override application
- **Configuration metadata**: Diagnostic information about configuration loading, source location, override application, and warnings
- **Strict mode**: Configuration mode where parse and validation errors are fatal
- **Permissive mode**: Configuration mode where parse and validation errors produce warnings and fallback behavior
- **Legacy environment prefix**: Backward-compatible environment prefix accepted as fallback
- **Platform-standard user configuration location**: Conventional user configuration directory provided by the operating environment
- **Redaction**: Masking or omitting sensitive values from logs and diagnostics
- **Project marker**: Recognized filesystem concept used to infer project root, such as configuration source, product-specific configuration source, project manifest, or version control metadata

## Reference

- Product Requirements Document for blender-arwaky
- Shared feature requirements documentation
