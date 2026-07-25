# FRD — Config Feature Module

## System Overview

The settings feature manages how the application reads, validates, and provides access to its operational parameters. It ensures that configuration data is loaded safely from files or external sources, applies the correct precedence rules, and provides a secure, read-only view of these settings to the rest of the application.

The feature treats all external configuration files as potentially unsafe. It applies strict parsing rules to prevent malicious code execution from configuration files. It also ensures that sensitive data (like passwords or API keys) is never exposed in logs or diagnostic outputs. Because the application may request settings simultaneously from multiple components, the feature guarantees that all access is safe, consistent, and immutable during runtime.

## Functional Requirements

### FR-CFG-001: Load and Apply Settings

- **Use Case:** The application starts up and needs to load its operational settings to know how to behave (e.g., network ports, timeouts, feature flags).
- **User Action:** Provide a specific settings file path, or rely on the system to automatically find the file using default locations and external system environment settings.
- **System Response:** Safely read, parse, validate, and store the settings in memory for the application to use.
- **Business Rules:**
  - Settings are loaded based on a strict precedence order:
    1. Explicit file path provided at runtime.
    2. External system environment overrides.
    3. Settings file found in the resolved project workspace.
    4. Standard user-level settings directory.
    5. Built-in application defaults.
  - If no settings file is found, the system uses built-in defaults without failing (unless strict validation requires it).
  - The system must parse the settings file safely, ensuring no arbitrary code or malicious objects are executed from the file.
  - External system environment settings always override values found in the file.
  - Environment values must be automatically converted to the correct data types (e.g., text "true" becomes a boolean, "8080" becomes a number).
  - If a validation schema is defined, the loaded settings must be checked against it.
  - Sensitive values (tokens, passwords, API keys) must be automatically detected and hidden (redacted) in all logs and diagnostic outputs.
  - The system must enforce a maximum file size for settings files to prevent memory exhaustion.
  - **Strict Mode (Default for production):** Malformed files or validation failures cause the application to fail startup with a clear error.
  - **Permissive Mode (Default for development):** Malformed files or validation failures log a warning, and the system falls back to safe defaults where possible.
- **Edge Cases:** Settings file is missing, file is malformed/corrupted, permission denied when reading the file, file is empty, file contains duplicate keys, file contains unsafe/malicious tags, file is too large, external environment settings conflict with file settings.
- **Error Handling:**
  - Return `SettingsParseError` for malformed files (in strict mode).
  - Return `SettingsValidationError` for schema violations (in strict mode).
  - Return `SettingsLoadError` for permission denied or oversized files.
  - Log warnings and use defaults for the above errors (in permissive mode).

### FR-CFG-002: Retrieve Settings Values

- **Use Case:** A component of the application needs to know a specific setting (e.g., "what is the network port?" or "what is the timeout limit?") to perform its task.
- **User Action:** Request a specific setting by providing its structured hierarchical path (e.g., "server.network.port"), optionally providing a fallback default value and the expected data type.
- **System Response:** Return the configured value, the fallback default value, or an error if the data type is incorrect.
- **Business Rules:**
  - The system traverses the hierarchical path to find the exact setting value.
  - If the setting is missing, the system returns the provided fallback default value.
  - If an expected data type is specified (e.g., integer) and the stored value does not match, the system returns the default value (in permissive mode) or raises an error (in strict mode).
  - Requesting an empty path returns a complete, read-only snapshot of all current settings.
  - The returned settings snapshot must be strictly read-only (immutable) to prevent accidental modification of the application's core configuration.
  - The retrieval process must be safe for concurrent access (multiple components can read settings at the exact same time without causing errors or delays).
  - Reading a setting must never trigger a reload from the disk; it must only read from the in-memory store.
- **Edge Cases:** Requesting a missing key, requesting a key with the wrong data type, providing an invalid path format, requesting an empty path, path points to a list index that is out of bounds, path contains special characters.
- **Error Handling:**
  - Return the default value for missing keys or out-of-bounds indexes.
  - Return `SettingsTypeError` for data type mismatches (in strict mode).
  - Return `SettingsPathError` for invalid path formats (in strict mode).

### FR-CFG-003: Resolve Project Workspace Directory

- **Use Case:** The application needs to determine the root directory of the current project to correctly locate relative files, assets, or local settings.
- **User Action:** (Implicit) The system automatically attempts to find the project root directory based on explicit overrides, known project markers, or standard directories.
- **System Response:** Return the absolute, normalized file path representing the resolved project root directory.
- **Business Rules:**
  - The system resolves the directory using a strict precedence order:
    1. Explicit directory path provided via external environment settings.
    2. Upward directory search looking for recognized "project markers" (e.g., the primary settings file, a project manifest file, or version control metadata).
    3. Standard user-level configuration directory.
    4. The current working directory where the application was launched.
  - When searching upward for project markers, the system checks parent directories one by one until it finds a marker.
  - Marker priority during upward search: Primary settings file > Project manifest > Version control metadata.
  - All resolved paths must be normalized (cleaned of redundant slashes or relative dots like `../`).
  - Symbolic links in the path must be resolved safely to their actual physical locations without causing the system to crash.
  - The system must never automatically create directories during this resolution process.
  - If an environment-provided path is invalid or inaccessible, the system logs a warning and moves to the next resolution strategy.
- **Edge Cases:** Multiple project markers found in different parent directories, symbolic links creating circular loops, permission denied when checking parent directories, network-mounted drives, case-insensitive file systems, current working directory has been deleted.
- **Error Handling:**
  - Return `SettingsResolutionError` if all strategies fail and the current working directory is completely inaccessible.
  - Fall back to the current working directory if no project markers are found but the directory is accessible.

## System Capabilities (User-Facing Operations)


| Operation               | User Action (Input)              | System Response (Output)               | Description                                   |
| ------------------------- | ---------------------------------- | ---------------------------------------- | ----------------------------------------------- |
| `load_settings`         | Optional explicit file path      | Settings Metadata (status, warnings)   | Load and validate settings from sources       |
| `reload_settings`       | Optional explicit file path      | Settings Metadata (status, warnings)   | Clear cache and reload settings               |
| `get_setting`           | Hierarchical path, default, type | Setting Value                          | Retrieve a specific setting value             |
| `get_all_settings`      | —                               | Read-only Settings Snapshot            | Retrieve a complete snapshot of all settings  |
| `resolve_project_root`  | —                               | Absolute Directory Path                | Determine the root directory of the project   |
| `get_settings_metadata` | —                               | Metadata (source, overrides, warnings) | Get diagnostic info about how settings loaded |

**Additional Capability Behaviors:**

- `load_settings` and `reload_settings` must ensure that sensitive values are never included in the returned metadata or logs.
- `get_setting` must guarantee that the returned value cannot be used to mutate the underlying in-memory settings.
- `get_all_settings` must return a deep copy or strictly immutable view of the settings.
- `resolve_project_root` must handle operating system differences (Windows, macOS, Linux) gracefully.

## External Boundaries

- **External Consumers:**
  - All other application modules (Server, Asset Providers, Diagnostics) that need to read operational parameters.
- **Target Environment:**
  - Local Filesystem: For reading settings files and detecting project markers.
  - Operating System Environment: For reading external environment variable overrides.
- **External Dependencies:**
  - None. This feature is foundational and does not depend on other complex application modules.

## Non-functional Requirements

- **Performance:**
  - Retrieving a setting from memory must be extremely fast (ideally < 1 millisecond).
  - Loading or reloading the settings file must complete within 100 milliseconds under normal disk conditions.
  - Path resolution must not perform unnecessary disk reads (it should cache the resolved root directory).
- **Reliability:**
  - The system must gracefully fall back to defaults if the settings file is missing.
  - A failed reload must not corrupt the current settings; the previous valid settings must remain active.
  - The system must remain stable and responsive even if multiple components request settings simultaneously.
- **Security:**
  - Settings file parsing must be strictly sandboxed to prevent code execution.
  - Secrets (passwords, tokens, keys) must be automatically detected and redacted from all logs, diagnostics, and metadata outputs.
  - The system should warn the user if the settings file has overly permissive access rights (e.g., writable by everyone).
  - Maximum file size limits must be enforced to prevent denial-of-service via memory exhaustion.
- **Observability:**
  - The system must log which settings source was successfully loaded.
  - The system must log how many external environment overrides were applied (without revealing the values).
  - The system must log validation and parsing warnings clearly.
  - Diagnostic metadata must be available for troubleshooting without exposing sensitive data.
- **Portability:**
  - The system must correctly handle file paths across different operating systems (Windows, macOS, Linux).
  - The system must respect standard user configuration directories for each operating system.

## Test Scenarios / QA Checklist

**Settings Loading & Validation:**

- [ ]  Load settings from a valid file returns the correct parsed values.
- [ ]  Load settings from a missing file returns built-in defaults without crashing.
- [ ]  Load settings from a malformed file raises a parse error (in strict mode).
- [ ]  Load settings from a malformed file logs a warning and uses defaults (in permissive mode).
- [ ]  Load settings containing malicious/unsafe tags is rejected safely.
- [ ]  Load settings from an explicit file path overrides all other sources.
- [ ]  External environment settings correctly override file-based settings.
- [ ]  Environment values are correctly converted to booleans, numbers, and lists.
- [ ]  Secrets in the settings file are redacted from all logs and metadata.
- [ ]  Loading a file larger than the maximum size limit raises a load error.

**Settings Retrieval:**

- [ ]  Retrieve an existing setting returns the correct value.
- [ ]  Retrieve a missing setting returns the provided default value.
- [ ]  Retrieve an empty path returns a complete, read-only snapshot of all settings.
- [ ]  The returned settings snapshot cannot be modified (immutability check).
- [ ]  Retrieve a setting with an expected type returns the value if the type matches.
- [ ]  Retrieve a setting with an expected type returns the default or raises an error if the type mismatches.
- [ ]  Retrieve a setting using an out-of-bounds list index returns the default value.
- [ ]  Concurrent retrieval of settings by multiple components does not cause errors or delays.

**Project Workspace Resolution:**

- [ ]  Resolve root directory via explicit environment override succeeds.
- [ ]  Resolve root directory by finding the primary settings file in a parent directory.
- [ ]  Resolve root directory prefers the settings file over version control metadata.
- [ ]  Resolve root directory falls back to the standard user configuration directory.
- [ ]  Resolve root directory falls back to the current working directory if no markers are found.
- [ ]  Resolve root directory handles symbolic links safely without infinite loops.
- [ ]  Resolve root directory handles permission-denied parent directories gracefully.
- [ ]  Resolve root directory raises an error if the current working directory is completely inaccessible.

**Reloading & Metadata:**

- [ ]  Reload settings clears the cache and loads fresh data.
- [ ]  Reload failure retains the previous valid settings in memory.
- [ ]  Settings metadata correctly reports the loaded source and number of overrides.
- [ ]  Settings metadata does not expose any secret values.

## Assumptions & Constraints

- The settings file format is a structured, text-based format (e.g., YAML, JSON, TOML). *Note: The specific format is an implementation choice, but it must support safe parsing.*
- Safe parsing is strictly enforced; no code execution from the settings file is allowed under any circumstances.
- Only one primary settings file is loaded per application instance.
- External environment settings always take precedence over file-based settings.
- The settings module does not fetch remote configuration over the network by default.
- The settings module is not a dedicated secret manager, but it must handle secrets safely if they are provided.
- Strict mode is the default for production environments; permissive mode is for development/fallback.
- Project root detection is a best-effort process based on deterministic precedence rules.

## Glossary

- **Hierarchical Path:** A structured string used to locate a nested setting (e.g., "server.network.port").
- **Settings Snapshot:** A complete, read-only view of all currently loaded settings.
- **Settings Metadata:** Diagnostic information about how the settings were loaded, including the source file and applied overrides.
- **Strict Mode:** An operational mode where parsing or validation errors cause the application to fail safely.
- **Permissive Mode:** An operational mode where parsing or validation errors produce warnings and the system falls back to safe defaults.
- **Project Marker:** A recognized file or directory (like a settings file or version control folder) used to identify the root of a project workspace.
- **Redaction:** The process of masking or completely omitting sensitive values from logs and diagnostic outputs.
- **External Environment Settings:** Configuration values provided by the operating system's environment variables, which override file-based settings.
