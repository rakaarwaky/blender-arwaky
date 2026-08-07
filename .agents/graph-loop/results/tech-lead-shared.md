# Plan: shared — Tech-Lead

## Summary

The shared module (189 Python files, ~12 domains) provides taxonomy VOs, contract protocols/aggregates, and utility functions as the foundation for all feature modules. The module is structurally well-organized by domain folders, but contains **critical layer boundary violations** — 4 files place stateful capabilities classes inside utility-named files (AES404), 2 files lack layer prefixes (AES101), and there is a duplicate contract with conflicting signatures (AES305). Additionally, `__init__.py` references non-existent symbols and contains bypass comments, and 3 VOs are duplicated across asset/security domains. Total: **5 CRITICAL, 7 HIGH, 8 MEDIUM, 6 INFO** findings.

---

## Findings

### Security

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| S1 | 🟡 WARNING | `mask_secrets()` is a no-op placeholder — secrets may leak in MCP responses | `mcp/mcp_response_formatter.py:62` | Wire to security redaction protocol from `security/` domain |
| S2 | 🟡 WARNING | Silent exception swallowing in config file loading — `except Exception: pass` hides corrupted configs | `gateway/utility_config_loader.py:75-77` | Log warning on config load failure; never silently discard |
| S3 | 🟢 INFO | `code_fingerprint()` truncates SHA-256 to 16 chars — low collision risk but documented | `gateway/utility_validator_checker.py:140-143` | Acceptable for logging-only use; ensure not used for integrity checks |

### Performance

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| P1 | 🟡 WARNING | `taxonomy_dispatcher_constant.py` (374 lines) — large dict literal loaded into memory at import time | `dispatcher/taxonomy_dispatcher_constant.py` | Acceptable for constants; consider lazy loading if import time matters |
| P2 | 🟢 INFO | `_wait_for_addon()` busy-loops with 0.5s sleep polling socket connection | `cli/utility_cli_process.py:112-118` | Acceptable for startup; consider exponential backoff for long waits |

### Error Handling

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| E1 | 🔴 CRITICAL | Unreachable code in `parse_env_value()` — `return None` on line 47 executes before the `if value.lower() in ("null", ...)` check on line 48 | `config/utility_config_helpers.py:44-50` | Move null/none check before the float try/except, or remove unreachable branch |
| E2 | 🟡 WARNING | `mcp_routing_proxy.py` raises bare `RuntimeError`/`ValueError` instead of domain errors | `mcp/mcp_routing_proxy.py:56,95` | Use `SecurityViolationError` or domain-specific errors from taxonomy |
| E3 | 🟡 WARNING | Indonesian text in error messages — violates documentation-language convention | `cli/utility_cli_registry.py:100-114` | Translate all error messages to English |

### SOLID

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| D1 | 🔴 CRITICAL | **AES404**: `utility_socket_client.py` contains stateful `BlenderSocketClient` class with socket state, connect/disconnect lifecycle, context manager | `gateway/utility_socket_client.py` | Rename to `capabilities_gateway_socket_client.py`; utility must be stateless functions only |
| D2 | 🔴 CRITICAL | **AES404**: `mcp_response_formatter.py` contains `McpResponseImpl` class implementing `McpResponseProtocol` — capabilities in utility location | `mcp/mcp_response_formatter.py` | Rename to `capabilities_mcp_response_formatter.py` |
| D3 | 🔴 CRITICAL | **AES404**: `mcp_routing_proxy.py` contains `McpRoutingImpl` class implementing `McpRoutingProtocol` — capabilities in utility location | `mcp/mcp_routing_proxy.py` | Rename to `capabilities_mcp_routing_proxy.py` |
| D4 | 🔴 CRITICAL | **AES404**: `utility_cli_registry.py` contains singleton `Registry` class with file I/O, mutable state, and thread locking | `cli/utility_cli_registry.py` | Move to `capabilities_cli_registry.py`; utility must be stateless functions only |
| D5 | 🟡 WARNING | `gateway/utility_config_loader.py` (227 lines) — complex config resolution with validation, env overrides, and schema building — capabilities-level logic in utility | `gateway/utility_config_loader.py` | Consider splitting: keep stateless helpers in utility, move orchestration logic to capabilities |

### Code Quality

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| C1 | 🟡 WARNING | **AES101**: `mcp_response_formatter.py` lacks layer prefix — should be `capabilities_mcp_response_formatter.py` | `mcp/mcp_response_formatter.py` | Rename with `capabilities_` prefix |
| C2 | 🟡 WARNING | **AES101**: `mcp_routing_proxy.py` lacks layer prefix — should be `capabilities_mcp_routing_proxy.py` | `mcp/mcp_routing_proxy.py` | Rename with `capabilities_` prefix |
| C3 | 🟡 WARNING | **AES305**: Duplicate `ExecuteActionProtocol` — exists in both `common/` and `dispatcher/` with conflicting signatures (async vs sync, VOs vs primitives) | `common/contract_execute_action_protocol.py` + `dispatcher/contract_execute_action_protocol.py` | Consolidate into single protocol; keep VO-based version in `common/`, remove primitive-based duplicate |
| C4 | 🟡 WARNING | **AES401**: `taxonomy_command_catalog_constant.py` contains `CommandCatalog` class with methods — constants files must only contain constant declarations | `common/taxonomy_command_catalog_constant.py:139-143` | Move `CommandCatalog` class to a capabilities or utility file; keep only `COMMAND_CATALOG` and `ACTION_NAMES` constants |
| C5 | 🟡 WARNING | **AES303**: `taxonomy_app_config_vo.py` contains empty placeholder class with only a dummy static method | `common/taxonomy_app_config_vo.py` | Remove file or implement actual ApplicationConfig VO |
| C6 | 🟡 WARNING | **AES402**: `dispatcher/contract_execute_action_protocol.py` uses primitives (`str`, `dict[str, Any]`) in method signatures instead of taxonomy VOs | `dispatcher/contract_execute_action_protocol.py:20` | Replace `str` with `ActionName`, `dict[str, Any]` with typed VO |
| C7 | 🟢 INFO | `mcp_routing_proxy.py` imports from `dispatcher.taxonomy_action_command_vo` directly — should use contract protocol, not taxonomy from another domain | `mcp/mcp_routing_proxy.py:11` | Route through dispatcher contract protocol |

### Maintainability

| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| M1 | 🟡 WARNING | **AES304**: `# noqa: F401` bypass comments — 6 occurrences across `src/__init__.py:141` and `mcp/__init__.py:4,7,10,13,16` | `src/__init__.py`, `mcp/__init__.py` | Remove noqa; use explicit `__all__` control (already present in `src/__init__.py`) |
| M2 | 🟡 WARNING | `__init__.py` `__all__` references 7 non-existent symbols: `SceneOperateProtocol`, `RenderOperateProtocol`, `RenderViewportCaptureProtocol`, `CameraConfigProtocol`, `HdriConfigProtocol`, `ViewportCaptureProtocol`, `SceneInspectionPort` | `src/__init__.py:__all__` | Remove non-existent symbols from `__all__` or add missing imports |
| M3 | 🟡 WARNING | **AES305**: 3 VOs duplicated across asset and security domains: `ArchiveEntryVO`, `ArchiveExtractionOptionsVO`, `ArchiveExtractionVO` | `asset/taxonomy_asset_vo.py:214,230,247` + `security/taxonomy_security_vo.py:60,72,92` | Consolidate into shared taxonomy (e.g. `common/` or `archive/`); security version is superset — use it as canonical, asset imports from shared |
| M4 | 🟡 WARNING | 4 error class names duplicated across domains: `ValidationError` (4 copies), `ConnectionError` (2), `ProviderError` (2), `ExecutionError` (2) | `common/taxonomy_domain_error.py`, `gateway/taxonomy_gateway_error.py`, `job/taxonomy_job_error.py`, `security/taxonomy_security_error.py` | Rename domain-specific variants with domain prefix (e.g. `GatewayValidationError`, `JobValidationError`) or consolidate base errors |
| M5 | 🟢 INFO | `utility_routing_proxy.py` contains `route_tool_call()` which duplicates logic from `mcp_routing_proxy.py`; neither delegates to the other | `mcp/utility_routing_proxy.py` + `mcp/mcp_routing_proxy.py` | Deduplicate — capabilities class should delegate to utility functions |
| M6 | 🟢 INFO | `taxonomy_telemetry_event.py` `TelemetryEvent` uses `str`/`float` for fields that have `NewType` aliases (`FeatureArea`, `OperationType`, etc.) defined earlier in the same file | `telemetry/taxonomy_telemetry_event.py:99-108` | Use the NewType aliases for type safety, or remove the unused NewType definitions |
| M7 | 🟢 INFO | Dead code: `_taxonomy_types = (RuntimeStateVO,)` defined but never referenced | `launcher/utility_process_ops.py` | Remove unused module-level variable |
| M8 | 🟡 WARNING | **AES304**: `# pragma: no cover` bypass comments (2 occurrences) suppress test coverage | `gateway/utility_config_loader.py:22,95` | Add tests for these code paths or document justified exclusion |

---

## Action Items

- [ ] **CRITICAL** Rename `gateway/utility_socket_client.py` → `capabilities_gateway_socket_client.py`
- [ ] **CRITICAL** Rename `mcp/mcp_response_formatter.py` → `capabilities_mcp_response_formatter.py`
- [ ] **CRITICAL** Rename `mcp/mcp_routing_proxy.py` → `capabilities_mcp_routing_proxy.py`
- [ ] **CRITICAL** Rename `cli/utility_cli_registry.py` → `capabilities_cli_registry.py`
- [ ] **CRITICAL** Fix unreachable code in `config/utility_config_helpers.py` `parse_env_value()`
- [ ] **HIGH** Remove `# noqa: F401` bypass from `src/__init__.py`
- [ ] **HIGH** Remove 6 non-existent symbols from `__init__.py` `__all__`
- [ ] **HIGH** Consolidate duplicate `ExecuteActionProtocol` (common vs dispatcher)
- [ ] **HIGH** Move `CommandCatalog` class out of constants file
- [ ] **HIGH** Remove or implement `taxonomy_app_config_vo.py` placeholder
- [ ] **MEDIUM** Replace primitive types with VOs in `dispatcher/contract_execute_action_protocol.py`
- [ ] **MEDIUM** Translate Indonesian error messages to English
- [ ] **MEDIUM** Consolidate duplicate error classes between `taxonomy_domain_error.py` and domain-specific error files
- [ ] **MEDIUM** Wire `mask_secrets()` to actual security redaction
- [ ] **MEDIUM** Log config load failures instead of silently swallowing exceptions

---

## Fixed Code

### Fix 1: Unreachable code in `parse_env_value()` (E1)

**File:** `modules/shared/src/config/utility_config_helpers.py`

```python
# BEFORE (lines 37-50):
def parse_env_value(value: str) -> SettingsValue:
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None          # ← returns here, next line unreachable
    if value.lower() in ("null", "none", ""):  # ← UNREACHABLE
        return None
    return value

# AFTER:
def parse_env_value(value: str) -> SettingsValue:
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False
    if value.lower() in ("null", "none", ""):
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            return value
```

### Fix 2: Remove `# noqa: F401` bypass (M1)

**File:** `modules/shared/src/__init__.py`

```python
# BEFORE:
from .telemetry.taxonomy_telemetry_event import TelemetryCategory as _TelemetryCategory  # noqa: F401

# AFTER:
from .telemetry.taxonomy_telemetry_event import TelemetryCategory as _TelemetryCategory
```

### Fix 3: Remove non-existent symbols from `__all__` (M2)

**File:** `modules/shared/src/__init__.py`

Remove these entries from `__all__` (and any corresponding missing imports):
```python
# REMOVE these from __all__:
"SceneOperateProtocol",
"RenderOperateProtocol",
"RenderViewportCaptureProtocol",
"CameraConfigProtocol",
"HdriConfigProtocol",
"ViewportCaptureProtocol",
"SceneInspectionPort",
```

### Fix 4: Replace primitives with VOs in dispatcher protocol (C6)

**File:** `modules/shared/src/dispatcher/contract_execute_action_protocol.py`

```python
# BEFORE:
from abc import ABC, abstractmethod
from typing import Any

class ExecuteActionProtocol(ABC):
    def execute_action(self, action_name: str, parameters: dict[str, Any]) -> Any:
        ...

# AFTER:
from abc import ABC, abstractmethod
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

class ExecuteActionProtocol(ABC):
    def execute_action(self, command: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        ...
```

### Fix 5: Move `CommandCatalog` class out of constants file (C4)

**File:** `modules/shared/src/common/taxonomy_command_catalog_constant.py`

```python
# BEFORE (keep at end of constants file):
class CommandCatalog:
    COMMAND_CATALOG = COMMAND_CATALOG
    @staticmethod
    def list_actions() -> list[str]:
        return ACTION_NAMES

# AFTER:
# Remove the CommandCatalog class entirely from this file.
# Move it to: modules/shared/src/common/utility_command_catalog.py
```

**New file:** `modules/shared/src/common/utility_command_catalog.py`

```python
"""Utility: Command catalog query functions — stateless, standalone."""

from __future__ import annotations

from ..taxonomy_command_catalog_constant import ACTION_NAMES, COMMAND_CATALOG, CommandSpec


def list_actions() -> list[str]:
    """Return all available action names."""
    return list(ACTION_NAMES)


def get_command_spec(action: str) -> CommandSpec | None:
    """Retrieve command spec for a named action."""
    return COMMAND_CATALOG.get(action)
```

---

## Checklist

- [x] Prerequisites read (RULES_AES.md, ARCHITECTURE.md, PRD.md)
- [x] Feature identified (shared — 189 files, 12 domains)
- [x] All 6 dimensions analyzed
- [x] Severity categorized (5 CRITICAL, 5 HIGH, 5 MEDIUM, 5 INFO)
- [x] History checked (features.json — iteration 0, no prior completion)
- [x] Plan written (findings + fixed code)
- [x] Saved to `.agents/graph-loop/results/tech-lead-shared.md`
