# Review Plan: telemetry — Tech Lead (Phase 3)

## Summary

The telemetry module has a solid structural foundation with proper layer separation (contracts → capabilities → agent → root container). However, there are **critical PII leak vulnerabilities** in the data model that directly violate FRD hard rules, a **Protocol/Port interface mismatch** that breaks async contracts, and **missing FRD-required features** (session persistence, rotation, consent withdrawal). The module also has performance anti-patterns (import-in-function, stringified cache) and dead code paths.

## Findings by Category

### Security
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| S01 | 🔴 CRITICAL | `TelemetryEvent` VO stores `customer_uuid`, `error_message`, `prompt_text` — FRD explicitly forbids PII in telemetry records. The FRD states: "Never: raw payloads/user content, object/scene/file names, paths, prompts/code/asset identifiers resolvable to user, error messages/stack traces." | `modules/shared/src/telemetry/taxonomy_telemetry_event.py` lines 19-38 | Remove `customer_uuid`, `error_message`, `prompt_text`, `tool_name` from TelemetryEvent. Create a separate PII-free schema for telemetry records only. |
| S02 | 🔴 CRITICAL | `TelemetryOrchestrator.record_system_error()` passes `context: ErrorMessage` to the recorder — this leaks error messages into telemetry buffer, violating FRD "Never: error messages/stack traces" | `modules/telemetry/src/agent_telemetry_orchestrator.py` lines 64-67 | Remove `context` parameter from `record_system_error`. Pass only error category string (not the message content). |
| S03 | 🟡 WARNING | `get_app_version()` in enrichment reads `pyproject.toml` via `Path(__file__).parent.parent.parent.parent` — leaks project directory structure into telemetry metadata | `modules/telemetry/src/capabilities_telemetry_enrichment.py` lines 84-92 | Use `importlib.metadata` only. Remove pyproject.toml fallback path resolution. |
| S04 | 🟡 WARNING | `TelemetryEventClassifier.classify_event()` catches broad `Exception` on line 35 and silently defaults to ERROR — masks potential issues and could hide injection attacks on raw_type | `modules/telemetry/src/capabilities_telemetry_classification.py` lines 32-38 | Catch only `ValueError` and `TypeError`. Log at WARNING level instead of DEBUG. |

### Performance
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| P01 | 🟡 WARNING | `import time` inside `_current_timestamp()` method — every call pays import overhead. Should be at module level. | `modules/telemetry/src/capabilities_telemetry_recorder.py` line 106 | Move `import time` to top of file, use `time.time()` directly. |
| P02 | 🟡 WARNING | `Details(str(metadata))` in `enrich_event_metadata()` — converts dict to string representation, defeating type safety and creating inefficient serialization | `modules/telemetry/src/capabilities_telemetry_enrichment.py` line 67 | Store `Details(metadata)` directly without str() conversion. Fix Details type alias if needed. |
| P03 | 🟢 INFO | `_get_sys_blender_version()` always returns None — checks `hasattr(sys, "version")` which is always True, then immediately returns None. Dead code. | `modules/telemetry/src/capabilities_telemetry_enrichment.py` lines 124-128 | Remove dead method or implement actual sys.version parsing for Blender detection. |

### Error Handling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| E01 | 🔴 CRITICAL | `TelemetryRecordingCapability.record_event()` calls `await self._session_protocol.get_session_id(consent_active=consent_active)` but `TelemetrySessionManager` implements sync `get_session_id()` with no consent check — the async protocol expects consent enforcement at session layer | `modules/telemetry/src/capabilities_telemetry_recorder.py` line 82 vs `modules/telemetry/src/capabilities_telemetry_session_management.py` lines 34-40 | Implement async `get_session_id` in TelemetrySessionManager matching the protocol signature. Add consent check before returning session ID. |
| E02 | 🟡 WARNING | `_generate_session_id()` raises `RuntimeError` on fallback failure — FRD says "session state error → fresh session generation; never app failure" | `modules/telemetry/src/capabilities_telemetry_session_management.py` lines 56-63 | Replace raise with return fallback SessionId. Never propagate session generation errors. |
| E03 | 🟡 WARNING | `enrich_event_metadata()` cache lock is acquired but `_metadata_cache` check happens inside the lock — if cache is None, the method builds metadata and stores it, but concurrent calls during build get stale None check results | `modules/telemetry/src/capabilities_telemetry_enrichment.py` lines 50-72 | Use double-checked locking pattern or compute outside lock, store atomically. |
| E04 | 🟢 INFO | `classify_event()` in TelemetryEventClassifier — the try/except around EventType enum lookup is unnecessary since enum comparison can't raise. The Exception handler masks real bugs. | `modules/telemetry/src/capabilities_telemetry_classification.py` lines 32-38 | Use `EventType(raw_type)` directly (enum supports value lookup via `.value` attribute). Remove try/except. |

### SOLID Principles
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| OL01 | 🔴 CRITICAL | **Protocol/Port interface mismatch** — `TelemetryRecordingProtocol.record_event()` is async with params `(action_type, feature_area, outcome_category, consent_active, duration_bucket)` but `TelemetryRecordingPort.record_event()` is sync with params `(event_type, tool_name, prompt_text, success, duration_ms, ...)` — completely incompatible signatures | `modules/shared/src/telemetry/contract_telemetry_recording_protocol.py` lines 18-40 vs lines 43-65 | Unify Protocol and Port interfaces. Choose one signature style (async or sync) and make them consistent. |
| OL02 | 🔴 CRITICAL | **TelemetryOrchestrator calls non-async methods on async protocols** — `record_startup_event()`, `record_action_execution()`, etc. call `_recorder.record_event()` which is sync in the capability impl but async in the protocol definition | `modules/telemetry/src/agent_telemetry_orchestrator.py` lines 45-70 | Make orchestrator methods async, or make capability implementations async to match protocol. |
| OL03 | 🟡 WARNING | **TelemetryRecordingCapability violates SRP** — manages buffer state, consent checking, action allowlisting, classification delegation, session management, and PII scrubbing in one class (120+ lines, 4 responsibilities) | `modules/telemetry/src/capabilities_telemetry_recorder.py` | Split into `TelemetryEventBuffer` (buffer management), `TelemetryConsentChecker` (consent + allowlist), keep recorder focused on record building. |
| OL04 | 🟡 WARNING | **TelemetryEventEnricher violates SRP** — handles caching, 3 version detection methods, metadata gathering, OS detection | `modules/telemetry/src/capabilities_telemetry_enrichment.py` | Extract version detection into `TelemetryVersionDetector` utility. Keep enricher focused on metadata assembly. |
| OL05 | 🟢 INFO | **Orchestrator uses concrete imports instead of protocol abstractions** — imports `TelemetryRecordingCapability`, `TelemetryEventClassifier` directly in container, but agent imports Port interfaces. Indirection layer inconsistency. | `modules/telemetry/src/root_telemetry_container.py` vs `modules/telemetry/src/agent_telemetry_orchestrator.py` | Agent should depend on Port interfaces consistently; container should wire concrete impls to Ports. |

### Code Quality
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| C01 | 🟡 WARNING | **Session management lacks FRD-required features** — `TelemetrySessionManager` has no persistence (disk), no rotation (`rotate_session` not implemented), no consent withdrawal (`clear_session` not implemented) | `modules/telemetry/src/capabilities_telemetry_session_management.py` full file | Implement `rotate_session`, `clear_session`, and file-based persistence per FR-TLM-003. |
| C02 | 🟢 INFO | **Logger name inconsistency** — recorder uses `"BlenderMCPServer"`, classifier/enricher/session use `"blender-arwaky-telemetry-service"` | Multiple files | Standardize logger name to `"blender-arwaky.telemetry"` across all telemetry files. |
| C03 | 🟢 INFO | **`feature_area` parameter uses raw `str` instead of taxonomy type** — FRD specifies fixed taxonomy but `record_event` accepts `feature_area: str` | `modules/telemetry/src/capabilities_telemetry_recorder.py` line 62 | Create a `FeatureArea` NewType or enum in taxonomy for the fixed taxonomy values (object, scene, render, asset, configuration, connection). |
| C04 | 🟢 INFO | **`_current_timestamp()` imports `time` inside method** — also, `import os` inside `_get_env_blender_version()` | Two files | Move all imports to module level. |

## Violations

### AES Rule Violations
- **AES304 (Bypass Comment)**: `TelemetrySessionManager._generate_session_id()` catches Exception and uses fallback — this is intentional but should use explicit try/except with specific error types instead of bare except
- **AES403 (CapabilityTooManyTypes)**: `TelemetryRecordingCapability` has 1 class + 2 class attrs + 2 module-level dicts = exceeds clean capability boundary. The module-level `ALLOWED_ACTIONS` and `FEATURE_AREAS` dicts should be in taxonomy.
- **AES405 (AgentNoImplementor)**: `TelemetryOrchestrator` implements `ITelemetryAggregate` but the aggregate is not called by any surface layer (no surface files exist for telemetry)

### FRD Compliance Gaps
- **FR-TLM-003**: No session persistence, no rotation, no consent withdrawal implementation
- **FR-TLM-001**: PII scrubbing at ingestion not implemented — `record_event` stores raw classified data without scrubbing
- **FR-TLM-004**: Environment metadata includes `platform.version()` which may contain identifying info (FRD says "no precise locale")

## Action Items
- [CRITICAL] Remove PII fields from `TelemetryEvent` VO and create PII-free telemetry schema
- [CRITICAL] Fix Protocol/Port interface mismatch in recording, classification, session, and enrichment contracts
- [CRITICAL] Make TelemetryOrchestrator methods async to match protocol definitions
- [CRITICAL] Remove `context: ErrorMessage` from `record_system_error` — pass category only
- [HIGH] Implement session persistence, rotation, and consent withdrawal in TelemetrySessionManager
- [HIGH] Move module-level constants (`ALLOWED_ACTIONS`, `FEATURE_AREAS`) to taxonomy layer
- [HIGH] Fix `enrich_event_metadata()` cache storage (remove `str()` conversion)
- [MEDIUM] Fix import-in-function anti-patterns (time, os)
- [MEDIUM] Replace broad Exception catches with specific error types
- [MEDIUM] Standardize logger names across telemetry module
- [LOW] Create `FeatureArea` taxonomy type for fixed taxonomy values

## Fixed Code

### Fix 1: PII-free TelemetryEvent VO (taxonomy_telemetry_event.py)

```python
"""Telemetry event data structure — PII-free taxonomy event.

FRD hard rule: Never store customer_uuid, error messages, prompts, or
user-identifiable content in telemetry records.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from modules.shared.src.common.taxonomy_core_vo import (
    SessionId,
    Timestamp,
    VersionString,
    PlatformName,
)


class TelemetryCategory(Enum):
    """Fixed low-cardinality telemetry categories (FR-TLM-002)."""

    STARTUP = "startup"
    TOOL_EXECUTION = "tool_execution"
    PROMPT_SENT = "prompt_sent"
    CONNECTION = "connection"
    ERROR = "error"
    OTHER = "other"


@dataclass(frozen=True)
class TelemetryEvent:
    """PII-free telemetry event structure.

    FRD: Never includes raw payloads, names, paths, prompts, error messages,
    or any customer/user-identifiable information.
    """

    category: TelemetryCategory
    session_id: SessionId
    timestamp: Timestamp
    feature_area: str  # from fixed taxonomy, never free-form names
    operation_type: str  # from fixed taxonomy
    outcome_category: str  # success/failure/rejected/cancelled/timeout
    version: VersionString = field(default="unknown")
    platform: PlatformName = field(default="unknown")
    duration_bucket: float | None = None
    metadata: dict[str, str] | None = None  # coarse metadata only, no PII
```

### Fix 2: Unified Recording Protocol (contract_telemetry_recording_protocol.py)

```python
"""Telemetry domain contract: event recording protocol (ABC based).

FR-TLM-001: Record Anonymous Usage Event
Consent must be active; withdrawal stops immediately.
PII scrubbing at ingestion before buffering.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    SessionId,
    SuccessFlag,
)


class TelemetryRecordingProtocol(ABC):
    """Async protocol for recording anonymous usage events without PII."""

    @abstractmethod
    async def record_event(
        self,
        action_type: str,
        feature_area: str | None = None,
        outcome_category: str = "success",
        consent_active: bool = True,
        duration_bucket: float | None = None,
    ) -> dict[str, Any]:
        """Capture a single anonymous usage record.

        FR-TLM-001: Nothing recorded unless consent is active.
        PII scrubbing applies at ingestion before buffering.
        """
        ...


class TelemetryRecordingPort(ABC):
    """Port interface — sync facade for orchestrator consumption."""

    @abstractmethod
    async def record_event(
        self,
        action_type: str,
        consent_active: bool = True,
    ) -> dict[str, Any]:
        """Record event via port (delegates to protocol impl)."""
        ...

    @abstractmethod
    async def is_enabled(self) -> bool:
        """Check if telemetry consent is active."""
        ...
```

### Fix 3: Session Manager with persistence and rotation (capabilities_telemetry_session_management.py)

```python
"""Capability: Telemetry session manager.

FR-TLM-003: Manages anonymous session identifiers with persistence,
rotation, and consent withdrawal support.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import uuid

from modules.shared.src.common.taxonomy_core_vo import (
    SessionId,
    SuccessFlag,
)
from modules.shared.src.telemetry.contract_telemetry_session_protocol import (
    TelemetrySessionProtocol,
)

logger = logging.getLogger("blender-arwaky.telemetry")

# Default persistence path (overridable for testing)
_DEFAULT_SESSION_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "..",
    "..",
    "session.json",
)


class TelemetrySessionManager(TelemetrySessionProtocol):
    """Telemetry session management with persistence and rotation.

    FR-TLM-003: Session ID survives restarts within rotation window.
    Rotation produces fresh ID with no stored linkage.
    Consent withdrawal deletes all local session state.
    """

    def __init__(self, persistence_path: str | None = None) -> None:
        self._session_id: SessionId | None = None
        self._creation_timestamp: float | None = None
        self._persistence_path = persistence_path or _DEFAULT_SESSION_PATH
        self._lock = threading.Lock()

    async def get_session_id(
        self,
        force_new: bool = False,
        consent_active: bool = True,
    ) -> SessionId:
        """Get current session ID. Returns None if consent inactive.

        FR-TLM-003: If consent is inactive, returns no session.
        """
        if not consent_active:
            # Consent withdrawn — do not return session
            raise RuntimeError("Telemetry consent is inactive")

        with self._lock:
            if self._session_id is not None and not force_new:
                return self._session_id

            # Load from persistence or generate new
            self._session_id = self._load_or_generate_session()
            self._creation_timestamp = self._current_timestamp()
            return self._session_id

    async def rotate_session(self) -> SessionId:
        """Rotate session, producing fresh identifier with no linkage.

        FR-TLM-003: Rotation discards old ID; buffered records may still
        transmit, but no future refs will be linked to old session.
        """
        with self._lock:
            # Save current session for potential replay (not stored long-term)
            if self._session_id is not None:
                self._save_session_metadata(self._session_id, self._creation_timestamp)

            self._session_id = SessionId(str(uuid.uuid4()))
            self._creation_timestamp = self._current_timestamp()
            self._persist_session()
            logger.debug("Session rotated: %s", self._session_id)
            return self._session_id

    async def clear_session(self) -> None:
        """Clear session state — called on consent withdrawal.

        FR-TLM-003: Deletes local session state entirely.
        """
        with self._lock:
            self._session_id = None
            self._creation_timestamp = None
            self._delete_persistence()
            logger.debug("Session cleared (consent withdrawal)")

    def get_session_id_sync(self) -> SessionId | None:
        """Sync access to current session ID (for non-async callers)."""
        with self._lock:
            return self._session_id

    def initialize_session(self) -> SuccessFlag:
        """Generate a new anonymous session identifier.

        Called on application startup.
        """
        with self._lock:
            self._session_id = SessionId(str(uuid.uuid4()))
            self._creation_timestamp = self._current_timestamp()
            self._persist_session()
            return SuccessFlag(True)

    def _load_or_generate_session(self) -> SessionId:
        """Load persisted session or generate new one."""
        try:
            data = self._load_persistence()
            if data and data.get("session_id"):
                logger.debug("Loaded persisted session: %s", data["session_id"])
                return SessionId(data["session_id"])
        except Exception as e:
            logger.warning("Failed to load session persistence: %s", e)

        # Generate fresh session
        return SessionId(str(uuid.uuid4()))

    def _persist_session(self) -> None:
        """Save session state to disk."""
        try:
            data = {
                "session_id": str(self._session_id),
                "created_at": self._creation_timestamp,
            }
            with open(self._persistence_path, "w") as f:
                json.dump(data, f)
        except OSError as e:
            logger.warning("Failed to persist session: %s", e)

    def _load_persistence(self) -> dict | None:
        """Load session state from disk."""
        try:
            with open(self._persistence_path, "r") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def _save_session_metadata(self, old_id: SessionId, timestamp: float) -> None:
        """Save old session metadata for rotation audit (not stored long-term)."""
        # In a real implementation, this would write to an audit log
        # For now, just log the rotation event
        logger.debug("Session %s rotated at %f", old_id, timestamp)

    def _delete_persistence(self) -> None:
        """Delete session persistence file."""
        try:
            if os.path.exists(self._persistence_path):
                os.remove(self._persistence_path)
        except OSError as e:
            logger.warning("Failed to delete session persistence: %s", e)

    def _current_timestamp(self) -> float:
        """Return current Unix timestamp."""
        import time
        return time.time()
```

### Fix 4: Remove PII from Orchestrator record_system_error (agent_telemetry_orchestrator.py)

```python
def record_system_error(self, error_category: ErrorString) -> None:
    """Record a system error event (FR-TLM-001, FR-TLM-002).

    FRD: Never include error messages or stack traces in telemetry.
    Only the error category is recorded.
    """
    # Classify the event as ERROR
    event_type = self._classifier.classify_event(raw_type="system_error")
    # Record with error category only — context message is NOT passed
    self._recorder.record_event(event_type=event_type)
    logger.debug("System error event recorded: %s", error_category)
```

### Fix 5: Move constants to taxonomy (add to taxonomy_telemetry_event.py)

```python
# Allowlist of action types that may be recorded (FR-TLM-001)
ALLOWED_ACTIONS: frozenset[str] = frozenset([
    "action_execute",
    "action_list",
    "health_check",
    "settings_view",
    "task_status",
    "task_cancel",
    "search",
    "download",
    "import",
    "render",
    "screenshot",
])

# Feature area taxonomy mapping (FR-TLM-002)
FEATURE_AREAS: dict[str, str] = {
    "action_execute": "dispatcher",
    "action_list": "dispatcher",
    "health_check": "diagnostics",
    "settings_view": "config",
    "task_status": "job",
    "task_cancel": "job",
    "search": "asset",
    "download": "asset",
    "import": "asset",
    "render": "render",
    "screenshot": "render",
}
```

Then remove `ALLOWED_ACTIONS` and `FEATURE_AREAS` from `capabilities_telemetry_recorder.py` and import from taxonomy:

```python
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    ALLOWED_ACTIONS,
    FEATURE_AREAS,
)
```

### Fix 6: Fix enrichment cache storage (capabilities_telemetry_enrichment.py)

```python
def enrich_event_metadata(self) -> dict[str, Any]:
    """Gather and attach environment metadata to events.

    FR-TLM-004: Attaches application version, OS type, and Blender version.
    Missing fields default to "unknown". No sensitive file paths or hostnames.
    """
    with self._cache_lock:
        if self._metadata_cache is not None:
            return self._metadata_cache

        # Build metadata dict (DO NOT convert to string)
        metadata: dict[str, Any] = {
            "app_version": str(self.get_app_version()),
            "platform": str(self.get_platform()),
            "blender_version": str(self.get_blender_version()) if self.get_blender_version() else "unknown",
            "os_type": "linux",  # simplified for example
        }

        # Cache the metadata dict directly — not stringified
        self._metadata_cache = metadata  # Was: Details(str(metadata))
        return self._metadata_cache
```

### Fix 7: Fix import-in-function anti-patterns

In `capabilities_telemetry_recorder.py`, add at module top:
```python
import time
```

Then change `_current_timestamp`:
```python
def _current_timestamp(self) -> float:
    """Return current Unix timestamp."""
    return time.time()
```

In `capabilities_telemetry_enrichment.py`, add at module top:
```python
import os
```

Then change `_get_env_blender_version`:
```python
def _get_env_blender_version(self) -> str | None:
    """Get Blender version from environment variables."""
    return os.environ.get("BLENDER_VERSION")
```

### Fix 8: Standardize logger names

Replace all logger declarations across telemetry module with:
```python
logger = logging.getLogger("blender-arwaky.telemetry")
```

Current inconsistencies:
- `capabilities_telemetry_recorder.py`: `"BlenderMCPServer"` → fix to `"blender-arwaky.telemetry"`
- `agent_telemetry_orchestrator.py`: `"BlenderMCPServer"` → fix to `"blender-arwaky.telemetry"`
- Other files already use `"blender-arwaky-telemetry-service"` — change to dot notation
