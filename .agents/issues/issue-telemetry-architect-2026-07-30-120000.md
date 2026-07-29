Create file: `.agents/issues/issue-telemetry-architect-2026-07-30-120000.md`

```markdown
# Issue: telemetry — Architectural Review & Refactoring

## Summary
The `telemetry` feature has a broadly correct AES folder split — shared taxonomy/contract files, feature-level capabilities, one agent orchestrator, and one root container — but the current implementation contains critical contract/implementation mismatches that will cause runtime failures and AES role violations. The agent layer depends on `*Port` contracts that no capability implements, while capabilities implement separate `*Protocol` contracts with incompatible sync/async signatures. Contract signatures also use raw primitives and `dict[str, Any]`, violating AES402 and weakening the PII-safety guarantees required by the telemetry FRD. The orchestrator does not actually record events through the recorder capability, and the recorder capability performs classification/session composition that belongs to the agent. These issues must be fixed before the telemetry module can safely satisfy FR-TLM-001 through FR-TLM-004.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Recorder capability calls classification and session protocols directly. This makes one capability depend on behavior owned by other capabilities. Capabilities should be standalone execution units; pipeline composition belongs to the agent. | `modules/telemetry/src/capabilities_telemetry_recorder.py:record_event` | Remove `session_protocol` and `classification_protocol` from recorder. Recorder should receive a fully composed, PII-free draft/record from the agent and only validate/buffer it. |
| 2 | 🔴 CRITICAL | Agent depends on `*Port` contracts, but capabilities implement different `*Protocol` contracts. Container wires incompatible objects into the orchestrator. | `modules/telemetry/src/agent_telemetry_orchestrator.py:__init__`, `modules/telemetry/src/root_telemetry_container.py:wire` | Consolidate each capability contract into one protocol consumed by the agent. Capability classes must implement exactly that contract. |
| 3 | 🔴 CRITICAL | Async/sync contract mismatch. Classification protocol is `async`, but classifier implementation is sync and orchestrator calls it sync. Session protocol is `async`, but orchestrator expects sync `TelemetrySessionManagementPort`. Recorder awaits classifier result, which is not awaitable. | `modules/shared/src/telemetry/contract_telemetry_classification_protocol.py`, `modules/shared/src/telemetry/contract_telemetry_session_protocol.py`, `modules/telemetry/src/capabilities_telemetry_recorder.py:record_event` | Choose one concurrency model. Since `ITelemetryAggregate` is currently sync, make capability protocols sync or expose a sync facade implemented correctly. If async is required, make aggregate/surface async too. |
| 4 | 🟡 WARNING | `modules/shared/src/telemetry/__init__.py` imports `taxonomy_event_constant`, but that file is not present in the provided telemetry source list. This is a potential broken import. | `modules/shared/src/telemetry/__init__.py:3` | Add the missing `taxonomy_event_constant.py` or remove the import. If constants such as `ALLOWED_ACTIONS` and `FEATURE_AREAS` are moved there, update exports. |
| 5 | 🟡 WARNING | Session manager persists `session.json` relative to source file location. This bypasses config-owned workspace/storage paths and can write into package/source directories. | `modules/telemetry/src/capabilities_telemetry_session_management.py:_DEFAULT_SESSION_PATH` | Inject an explicit `FilePath`/`DirectoryPath` from config. Do not derive persistence location from `__file__`. |
| 6 | 🟡 WARNING | Aggregate uses `ErrorString` for telemetry error recording. `ErrorString` can imply free-form error text, while FRD forbids error messages/stack traces in telemetry. | `modules/shared/src/telemetry/contract_telemetry_aggregate.py:record_system_error` | Introduce a bounded telemetry error-category VO or enum, e.g. `TelemetryErrorCategory`, and use it instead of `ErrorString`. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | Capability file suffixes describe concepts, not roles: `classification`, `enrichment`, `session_management`. AES role naming prefers executor/role suffixes such as `classifier`, `enricher`, `manager`. | `modules/telemetry/src/capabilities_telemetry_classification.py`, `modules/telemetry/src/capabilities_telemetry_enrichment.py`, `modules/telemetry/src/capabilities_telemetry_session_management.py` | Rename to `capabilities_telemetry_classifier.py`, `capabilities_telemetry_enricher.py`, `capabilities_telemetry_session_manager.py` and update imports. |
| 2 | 🟢 INFO | Contract classes are split into `*Protocol` and `*Port` names. AES contract files use `_protocol` or `_aggregate`; the dual naming creates confusion and duplicate abstraction surfaces. | `modules/shared/src/telemetry/contract_telemetry_classification_protocol.py`, `contract_telemetry_enrichment_protocol.py`, `contract_telemetry_recording_protocol.py`, `contract_telemetry_session_protocol.py` | Remove `*Port` classes or merge them into the single `*Protocol` contract used by the agent. |
| 3 | 🟡 WARNING | Taxonomy constants `ALLOWED_ACTIONS` and `FEATURE_AREAS` live in `taxonomy_telemetry_event.py`. Constants should live in a `_constant` taxonomy file. | `modules/shared/src/telemetry/taxonomy_telemetry_event.py:ALLOWED_ACTIONS`, `FEATURE_AREAS` | Move constants to `taxonomy_event_constant.py` or `taxonomy_telemetry_constant.py`. Keep event/VO types in event/VO files. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `TelemetryRecordingPort` is used by the agent type signature but has no implementation. `TelemetryRecordingCapability` implements `TelemetryRecordingProtocol`, not the port. The recorder is wired but never invoked by the orchestrator. | `modules/shared/src/telemetry/contract_telemetry_recording_protocol.py:TelemetryRecordingPort`, `modules/telemetry/src/agent_telemetry_orchestrator.py:record_action_execution` | Remove the unused port or make recorder implement the contract consumed by the agent. Then make orchestrator call recorder. |
| 2 | 🔴 CRITICAL | `TelemetryEnrichmentPort` is used by the agent but has no implementation. `TelemetryEventEnricher` inherits `TelemetryEnrichmentProtocol` but does not implement its abstract methods; instantiation should fail. | `modules/shared/src/telemetry/contract_telemetry_enrichment_protocol.py:TelemetryEnrichmentPort`, `modules/telemetry/src/capabilities_telemetry_enrichment.py:TelemetryEventEnricher` | Consolidate contract and implement the actual contract methods. Return typed `EnvironmentMetadata`, not `dict[str, Any]`. |
| 3 | 🔴 CRITICAL | `TelemetrySessionManagementPort` is used by the agent but has no implementation. `TelemetrySessionManager` implements async `TelemetrySessionProtocol`, not the sync management port. | `modules/shared/src/telemetry/contract_telemetry_session_protocol.py:TelemetrySessionManagementPort`, `modules/telemetry/src/capabilities_telemetry_session_management.py:TelemetrySessionManager` | Remove port/protocol duality. Implement one session contract compatible with the orchestrator. |
| 4 | 🟡 WARNING | `TelemetryEvent` dataclass is defined but not used by recorder, contracts, or agent. | `modules/shared/src/telemetry/taxonomy_telemetry_event.py:TelemetryEvent` | Use it as the immutable buffered record or remove it. Prefer using a typed VO instead of mutable dicts. |
| 5 | 🟡 WARNING | Unused import `sys`. | `modules/telemetry/src/capabilities_telemetry_enrichment.py:import sys` | Remove unused import. |
| 6 | 🟡 WARNING | Orchestrator receives `success` and `duration_ms` in `record_action_execution`, but never uses them. | `modules/telemetry/src/agent_telemetry_orchestrator.py:record_action_execution` | Pass them into the recording flow as outcome/duration bucket, or remove them after contract correction. |
| 7 | 🟢 INFO | `TelemetryRecordingPort.is_enabled` is defined but not used by the orchestrator. | `modules/shared/src/telemetry/contract_telemetry_recording_protocol.py:TelemetryRecordingPort.is_enabled` | Use consent checking in the recording flow or remove the method. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Each telemetry capability has two overlapping contract abstractions: async `*Protocol` and sync `*Port`. This doubles the API surface, causes orphan contracts, and produces runtime type mismatches. | `modules/shared/src/telemetry/contract_telemetry_classification_protocol.py`, `contract_telemetry_enrichment_protocol.py`, `contract_telemetry_recording_protocol.py`, `contract_telemetry_session_protocol.py` | Keep one contract per capability. Align it with the agent’s concurrency model and use taxonomy VOs in signatures. |
| 2 | 🟡 WARNING | Container hardcodes construction parameters and does not inject consent, endpoint, buffer capacity, rotation interval, or persistence path from config. | `modules/telemetry/src/root_telemetry_container.py:wire` | Inject configuration VOs/provider. Telemetry behavior must be driven by config consent and storage settings. |
| 3 | 🟡 WARNING | Enricher collects full `os_version` via `platform.version()`. FRD permits coarse environment metadata only; full OS/build strings increase fingerprint surface. | `modules/telemetry/src/capabilities_telemetry_enrichment.py:enrich_event_metadata` | Collect only OS family and major/minor runtime/version fields. Return typed `EnvironmentMetadata`. |
| 4 | 🟡 WARNING | Recorder buffers mutable `dict[str, Any]` records. FRD requires immutable records once buffered. | `modules/telemetry/src/capabilities_telemetry_recorder.py:_buffer` | Buffer frozen taxonomy VOs such as `TelemetryRecord` or `TelemetryEvent`. |
| 5 | 🟢 INFO | Logger names are inconsistent: telemetry capabilities use `blender-arwaky.telemetry`, root container uses `BlenderMCPServer`. | `modules/telemetry/src/root_telemetry_container.py:logger` | Standardize logger name, e.g. `blender-arwaky.telemetry`. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Orchestrator does not record events. `record_startup_event`, `record_action_execution`, and `record_system_error` only classify/log and never call the recorder. This violates the telemetry recording flow required by FR-TLM-001. | `modules/telemetry/src/agent_telemetry_orchestrator.py:record_startup_event`, `record_action_execution`, `record_system_error` | Orchestrator should compose consent/session/classification/recording and call the recorder capability. Telemetry failures must remain non-blocking. |
| 2 | 🔴 CRITICAL | Recorder awaits `self._classification_protocol.classify_event(...)`, but the concrete classifier returns a plain dict, not an awaitable. This will raise `TypeError` at runtime. | `modules/telemetry/src/capabilities_telemetry_recorder.py:record_event` | Make contract and implementation concurrency-compatible. If classifier is sync, do not await it; preferably move classification out of recorder. |
| 3 | 🟡 WARNING | Recorder performs event classification and session retrieval. That is pipeline orchestration, not recording. | `modules/telemetry/src/capabilities_telemetry_recorder.py:record_event` | Agent should call classifier and session manager, then pass a composed draft/record to recorder. |
| 4 | 🟡 WARNING | Aggregate returns `dict[str, Any]` from `get_environment_metadata`, and orchestrator assembles ad-hoc dicts. This bypasses taxonomy VOs and weakens contract safety. | `modules/shared/src/telemetry/contract_telemetry_aggregate.py:get_environment_metadata`, `modules/telemetry/src/agent_telemetry_orchestrator.py:get_environment_metadata` | Return a frozen `EnvironmentMetadata` VO from contract to implementation. |

## Violations
- AES402 — Contract role violation: contract methods use primitive types such as `str`, `float`, and `dict[str, Any]` instead of taxonomy VOs.
  - `contract_telemetry_classification_protocol.py`
  - `contract_telemetry_enrichment_protocol.py`
  - `contract_telemetry_recording_protocol.py`
  - `contract_telemetry_aggregate.py`
- AES403 — Capabilities role violation / missing effective protocol implementation:
  - `TelemetryEventEnricher` does not implement the abstract methods of `TelemetryEnrichmentProtocol`.
  - Capabilities do not implement the `*Port` contracts consumed by the agent.
- AES203 — Unused import:
  - `modules/telemetry/src/capabilities_telemetry_enrichment.py` imports `sys` but does not use it.
- AES502 — Contract orphan:
  - `TelemetryRecordingPort`, `TelemetryEnrichmentPort`, `TelemetrySessionManagementPort`, and `TelemetryClassificationPort` are not implemented by capabilities in a usable way.
  - `TelemetryRecordingProtocol` is implemented but not called by the agent; it is called by another capability instead.
- AES503 — Capabilities orphan / unreachable execution:
  - `TelemetryRecordingCapability` is wired into the orchestrator but its recording method is never invoked.
- AES501 — Taxonomy orphan:
  - `TelemetryEvent` is defined but not consumed by contracts, capabilities, or agent.
- AES101/AES102 — Naming/role suffix deviations, lower severity:
  - `capabilities_telemetry_classification.py`, `capabilities_telemetry_enrichment.py`, and `capabilities_telemetry_session_management.py` use concept suffixes instead of role suffixes.

## Action Items (For Developer)
- [ ] P0 Remove `*Port` / `*Protocol` duality. Keep one contract per telemetry capability.
- [ ] P0 Make capability contracts and implementations concurrency-compatible with the orchestrator. Current aggregate is sync; either make all telemetry capability contracts sync or make aggregate/surface async consistently.
- [ ] P0 Replace primitive contract signatures with taxonomy VOs: `ActionName`, `FeatureArea`, `OperationType`, `OutcomeCategory`, `DurationBucket`, `EnvironmentMetadata`, `TelemetryRecord`, `RecordingResult`.
- [ ] P0 Make `TelemetryOrchestrator` actually record events through `TelemetryRecordingCapability`.
- [ ] P0 Move classification and session composition out of recorder into the agent.
- [ ] P0 Fix `TelemetryEventEnricher` so it implements the contract it inherits and can be instantiated.
- [ ] P1 Introduce immutable telemetry VOs and stop using `dict[str, Any]` for records, classification results, and environment metadata.
- [ ] P1 Inject consent and storage/configuration values into the container instead of hardcoding behavior.
- [ ] P1 Replace source-relative `session.json` path with an injected config-owned `FilePath`/`DirectoryPath`.
- [ ] P1 Replace `ErrorString` in telemetry aggregate with a bounded telemetry error-category VO.
- [ ] P2 Move `ALLOWED_ACTIONS` and `FEATURE_AREAS` into a taxonomy constant file.
- [ ] P2 Rename capability files/classes to role-based names: classifier, enricher, session manager.
- [ ] P2 Remove unused imports, unused methods, and unused taxonomy types after contract consolidation.

## Proposed Fixes / Reference Code

### 1. `modules/shared/src/telemetry/taxonomy_telemetry_event.py`

Add typed VOs for telemetry classification, environment metadata, recording draft, and recording result.

```python
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import NewType

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    PlatformName,
    SessionId,
    SuccessFlag,
    Timestamp,
    VersionString,
    BlenderVersion,
)

FeatureArea = NewType("FeatureArea", str)
OperationType = NewType("OperationType", str)
OutcomeCategory = NewType("OutcomeCategory", str)
DurationBucket = NewType("DurationBucket", float)
OsFamily = NewType("OsFamily", str)
RuntimeVersion = NewType("RuntimeVersion", str)
SchemaVersion = NewType("SchemaVersion", str)
TelemetryErrorCategory = NewType("TelemetryErrorCategory", str)


class TelemetryRejectionReason(Enum):
    CONSENT_INACTIVE = "consent_inactive"
    ACTION_NOT_ALLOWLISTED = "action_not_allowlisted"
    INVALID_RECORD = "invalid_record"


@dataclass(frozen=True)
class ClassificationResult:
    category: "TelemetryCategory"
    feature_area: FeatureArea
    operation_type: OperationType
    outcome_category: OutcomeCategory


@dataclass(frozen=True)
class EnvironmentMetadata:
    app_version: VersionString
    platform: PlatformName
    blender_version: BlenderVersion | None
    os_family: OsFamily
    runtime_version: RuntimeVersion
    schema_version: SchemaVersion


@dataclass(frozen=True)
class TelemetryDraft:
    action_type: ActionName
    classification: ClassificationResult
    session_id: SessionId
    outcome_category: OutcomeCategory
    duration_bucket: DurationBucket | None = None


@dataclass(frozen=True)
class TelemetryRecord:
    action_type: ActionName
    category: "TelemetryCategory"
    session_id: SessionId
    timestamp: Timestamp
    feature_area: FeatureArea
    operation_type: OperationType
    outcome_category: OutcomeCategory
    version: VersionString
    platform: PlatformName
    duration_bucket: DurationBucket | None = None


@dataclass(frozen=True)
class RecordingResult:
    recorded: SuccessFlag
    rejection_reason: TelemetryRejectionReason | None = None
```

### 2. `modules/shared/src/telemetry/contract_telemetry_classification_protocol.py`

Use one sync protocol and typed VOs.

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ActionName
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    ClassificationResult,
    FeatureArea,
)


class TelemetryClassificationProtocol(ABC):
    @abstractmethod
    def classify_event(
        self,
        action_type: ActionName,
        feature_area: FeatureArea | None = None,
    ) -> ClassificationResult: ...
```

Remove `TelemetryClassificationPort`.

### 3. `modules/shared/src/telemetry/contract_telemetry_enrichment_protocol.py`

Return typed metadata, not dict.

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.telemetry.taxonomy_telemetry_event import EnvironmentMetadata


class TelemetryEnrichmentProtocol(ABC):
    @abstractmethod
    def get_environment_metadata(self) -> EnvironmentMetadata: ...
```

Remove `TelemetryEnrichmentPort`, `enrich_event`, and dict-based signatures.

### 4. `modules/shared/src/telemetry/contract_telemetry_recording_protocol.py`

Recorder should accept a composed draft and consent flag.

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import EnabledFlag, SuccessFlag
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    RecordingResult,
    TelemetryDraft,
)


class TelemetryRecordingProtocol(ABC):
    @abstractmethod
    def record_event(
        self,
        draft: TelemetryDraft,
        consent_active: EnabledFlag,
    ) -> RecordingResult: ...

    @abstractmethod
    def is_enabled(self) -> SuccessFlag: ...
```

Remove `TelemetryRecordingPort`.

### 5. `modules/shared/src/telemetry/contract_telemetry_session_protocol.py`

Use one sync session protocol compatible with current aggregate.

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import (
    EnabledFlag,
    SessionId,
    SuccessFlag,
)


class TelemetrySessionProtocol(ABC):
    @abstractmethod
    def get_session_id(self, consent_active: EnabledFlag) -> SessionId | None: ...

    @abstractmethod
    def initialize_session(self) -> SuccessFlag: ...

    @abstractmethod
    def rotate_session(self) -> SessionId: ...

    @abstractmethod
    def clear_session(self) -> None: ...
```

Remove `TelemetrySessionManagementPort`.

### 6. `modules/shared/src/telemetry/contract_telemetry_aggregate.py`

Return typed metadata and use bounded error category.

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    DurationMs,
    SessionId,
    SuccessFlag,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    EnvironmentMetadata,
    TelemetryErrorCategory,
)


class ITelemetryAggregate(ABC):
    @abstractmethod
    def record_startup_event(self) -> None: ...

    @abstractmethod
    def record_action_execution(
        self,
        action_name: ActionName,
        success: SuccessFlag,
        duration_ms: DurationMs,
    ) -> None: ...

    @abstractmethod
    def record_system_error(
        self,
        error_category: TelemetryErrorCategory,
    ) -> None: ...

    @abstractmethod
    def get_session_id(self) -> SessionId | None: ...

    @abstractmethod
    def initialize_session(self) -> None: ...

    @abstractmethod
    def get_environment_metadata(self) -> EnvironmentMetadata: ...
```

### 7. `modules/telemetry/src/capabilities_telemetry_classifier.py`

Rename file from `capabilities_telemetry_classification.py` and implement the corrected sync protocol.

```python
from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import ActionName
from modules.shared.src.telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationProtocol,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    FEATURE_AREAS,
    ClassificationResult,
    FeatureArea,
    OperationType,
    OutcomeCategory,
    TelemetryCategory,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryEventClassifier(TelemetryClassificationProtocol):
    def classify_event(
        self,
        action_type: ActionName,
        feature_area: FeatureArea | None = None,
    ) -> ClassificationResult:
        resolved_feature = feature_area or FeatureArea(FEATURE_AREAS.get(str(action_type), "other"))

        category = TelemetryCategory.OTHER
        outcome = OutcomeCategory("success")

        if str(action_type) == "startup":
            category = TelemetryCategory.STARTUP
        elif str(action_type) == "error":
            category = TelemetryCategory.ERROR
            outcome = OutcomeCategory("error")
        elif str(action_type) in FEATURE_AREAS:
            category = TelemetryCategory.TOOL_EXECUTION

        return ClassificationResult(
            category=category,
            feature_area=resolved_feature,
            operation_type=OperationType("execute"),
            outcome_category=outcome,
        )
```

### 8. `modules/telemetry/src/capabilities_telemetry_enricher.py`

Rename file from `capabilities_telemetry_enrichment.py`, remove unused `sys`, and implement the corrected contract.

```python
from __future__ import annotations

import logging
import platform
import threading
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    BlenderVersion,
    PlatformName,
    VersionString,
)
from modules.shared.src.telemetry.contract_telemetry_enrichment_protocol import (
    TelemetryEnrichmentProtocol,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    EnvironmentMetadata,
    OsFamily,
    RuntimeVersion,
    SchemaVersion,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryEventEnricher(TelemetryEnrichmentProtocol):
    def __init__(self, app_version: VersionString | None = None) -> None:
        self._cache: EnvironmentMetadata | None = None
        self._lock = threading.Lock()
        self._app_version = app_version

    def get_environment_metadata(self) -> EnvironmentMetadata:
        with self._lock:
            if self._cache is not None:
                return self._cache

            metadata = EnvironmentMetadata(
                app_version=self._app_version or VersionString("unknown"),
                platform=self._get_platform(),
                blender_version=self._get_blender_version(),
                os_family=self._get_os_family(),
                runtime_version=self._get_runtime_version(),
                schema_version=SchemaVersion("1.0"),
            )
            self._cache = metadata
            return metadata

    def _get_platform(self) -> PlatformName:
        try:
            return PlatformName(platform.system().lower())
        except Exception:
            return PlatformName("unknown")

    def _get_os_family(self) -> OsFamily:
        try:
            return OsFamily(platform.system().lower())
        except Exception:
            return OsFamily("unknown")

    def _get_runtime_version(self) -> RuntimeVersion:
        try:
            major, minor, _ = platform.python_version_tuple()
            return RuntimeVersion(f"{major}.{minor}")
        except Exception:
            return RuntimeVersion("unknown")

    def _get_blender_version(self) -> BlenderVersion | None:
        return None
```

### 9. `modules/telemetry/src/capabilities_telemetry_recorder.py`

Remove dependency on classifier/session. Buffer immutable records.

```python
from __future__ import annotations

import logging
import time
from collections import deque

from modules.shared.src.common.taxonomy_core_vo import (
    EnabledFlag,
    SuccessFlag,
    Timestamp,
    VersionString,
    PlatformName,
)
from modules.shared.src.telemetry.contract_telemetry_recording_protocol import (
    TelemetryRecordingProtocol,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    ALLOWED_ACTIONS,
    RecordingResult,
    TelemetryDraft,
    TelemetryRecord,
    TelemetryRejectionReason,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryRecordingCapability(TelemetryRecordingProtocol):
    def __init__(self, buffer_capacity: int = 1000) -> None:
        self._buffer: deque[TelemetryRecord] = deque(maxlen=buffer_capacity)
        self._enabled = EnabledFlag(True)

    def is_enabled(self) -> SuccessFlag:
        return SuccessFlag(bool(self._enabled))

    def record_event(
        self,
        draft: TelemetryDraft,
        consent_active: EnabledFlag,
    ) -> RecordingResult:
        if not consent_active:
            return RecordingResult(
                recorded=SuccessFlag(False),
                rejection_reason=TelemetryRejectionReason.CONSENT_INACTIVE,
            )

        if str(draft.action_type) not in ALLOWED_ACTIONS:
            return RecordingResult(
                recorded=SuccessFlag(False),
                rejection_reason=TelemetryRejectionReason.ACTION_NOT_ALLOWLISTED,
            )

        record = TelemetryRecord(
            action_type=draft.action_type,
            category=draft.classification.category,
            session_id=draft.session_id,
            timestamp=Timestamp(time.time()),
            feature_area=draft.classification.feature_area,
            operation_type=draft.classification.operation_type,
            outcome_category=draft.outcome_category,
            version=VersionString("unknown"),
            platform=PlatformName("unknown"),
            duration_bucket=draft.duration_bucket,
        )

        self._buffer.append(record)
        return RecordingResult(recorded=SuccessFlag(True))
```

### 10. `modules/telemetry/src/capabilities_telemetry_session_manager.py`

Rename file from `capabilities_telemetry_session_management.py` and implement the corrected sync contract.

```python
from __future__ import annotations

import json
import logging
import threading
import uuid
from pathlib import Path

from modules.shared.src.common.taxonomy_core_vo import (
    EnabledFlag,
    FilePath,
    SessionId,
    SuccessFlag,
)
from modules.shared.src.telemetry.contract_telemetry_session_protocol import (
    TelemetrySessionProtocol,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetrySessionManager(TelemetrySessionProtocol):
    def __init__(self, persistence_path: FilePath) -> None:
        self._session_id: SessionId | None = None
        self._persistence_path = Path(str(persistence_path))
        self._lock = threading.Lock()

    def get_session_id(self, consent_active: EnabledFlag) -> SessionId | None:
        if not consent_active:
            return None

        with self._lock:
            if self._session_id is None:
                self._session_id = self._load_or_generate()
            return self._session_id

    def initialize_session(self) -> SuccessFlag:
        with self._lock:
            self._session_id = SessionId(str(uuid.uuid4()))
            self._persist()
            return SuccessFlag(True)

    def rotate_session(self) -> SessionId:
        with self._lock:
            self._session_id = SessionId(str(uuid.uuid4()))
            self._persist()
            return self._session_id

    def clear_session(self) -> None:
        with self._lock:
            self._session_id = None
            self._delete_persistence()

    def _load_or_generate(self) -> SessionId:
        try:
            if self._persistence_path.exists():
                data = json.loads(self._persistence_path.read_text())
                return SessionId(str(data["session_id"]))
        except Exception as exc:
            logger.warning("Failed to load telemetry session: %s", exc)

        return SessionId(str(uuid.uuid4()))

    def _persist(self) -> None:
        try:
            self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
            self._persistence_path.write_text(json.dumps({"session_id": str(self._session_id)}))
        except OSError as exc:
            logger.warning("Failed to persist telemetry session: %s", exc)

    def _delete_persistence(self) -> None:
        try:
            if self._persistence_path.exists():
                self._persistence_path.unlink()
        except OSError as exc:
            logger.warning("Failed to delete telemetry session: %s", exc)
```

### 11. `modules/telemetry/src/agent_telemetry_orchestrator.py`

Orchestrate the full flow: consent → session → classify → record. Do not compute business rules; delegate behavior to capabilities.

```python
from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    DurationMs,
    EnabledFlag,
    SessionId,
    SuccessFlag,
)
from modules.shared.src.telemetry.contract_telemetry_aggregate import (
    ITelemetryAggregate,
)
from modules.shared.src.telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_enrichment_protocol import (
    TelemetryEnrichmentProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_recording_protocol import (
    TelemetryRecordingProtocol,
)
from modules.shared.src.telemetry.contract_telemetry_session_protocol import (
    TelemetrySessionProtocol,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    DurationBucket,
    EnvironmentMetadata,
    OutcomeCategory,
    TelemetryDraft,
    TelemetryErrorCategory,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryOrchestrator(ITelemetryAggregate):
    def __init__(
        self,
        recorder: TelemetryRecordingProtocol,
        classifier: TelemetryClassificationProtocol,
        session_manager: TelemetrySessionProtocol,
        enricher: TelemetryEnrichmentProtocol,
    ) -> None:
        self._recorder = recorder
        self._classifier = classifier
        self._session_manager = session_manager
        self._enricher = enricher

    def record_startup_event(self) -> None:
        self._record(ActionName("startup"), OutcomeCategory("success"), None)

    def record_action_execution(
        self,
        action_name: ActionName,
        success: SuccessFlag,
        duration_ms: DurationMs,
    ) -> None:
        outcome = OutcomeCategory("success" if bool(success) else "failure")
        bucket = DurationBucket(float(duration_ms))
        self._record(action_name, outcome, bucket)

    def record_system_error(
        self,
        error_category: TelemetryErrorCategory,
    ) -> None:
        self._record(ActionName(str(error_category)), OutcomeCategory("error"), None)

    def get_session_id(self) -> SessionId | None:
        consent = self._recorder.is_enabled()
        return self._session_manager.get_session_id(EnabledFlag(bool(consent)))

    def initialize_session(self) -> None:
        self._session_manager.initialize_session()

    def get_environment_metadata(self) -> EnvironmentMetadata:
        return self._enricher.get_environment_metadata()

    def _record(
        self,
        action_type: ActionName,
        outcome: OutcomeCategory,
        duration_bucket: DurationBucket | None,
    ) -> None:
        try:
            consent = self._recorder.is_enabled()
            if not bool(consent):
                return

            session_id = self._session_manager.get_session_id(EnabledFlag(bool(consent)))
            if session_id is None:
                return

            classification = self._classifier.classify_event(action_type)
            draft = TelemetryDraft(
                action_type=action_type,
                classification=classification,
                session_id=session_id,
                outcome_category=outcome,
                duration_bucket=duration_bucket,
            )

            self._recorder.record_event(draft, EnabledFlag(bool(consent)))
        except Exception:
            logger.debug("Telemetry recording skipped due to internal failure")
```

### 12. `modules/telemetry/src/root_telemetry_container.py`

Wire the corrected contracts. Inject config-owned persistence path and app version in a later config-integration pass.

```python
from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import FilePath, VersionString

from .agent_telemetry_orchestrator import TelemetryOrchestrator
from .capabilities_telemetry_classifier import TelemetryEventClassifier
from .capabilities_telemetry_enricher import TelemetryEventEnricher
from .capabilities_telemetry_recorder import TelemetryRecordingCapability
from .capabilities_telemetry_session_manager import TelemetrySessionManager

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryContainer:
    def __init__(
        self,
        session_path: FilePath,
        app_version: VersionString | None = None,
    ) -> None:
        self._session_path = session_path
        self._app_version = app_version
        self._orchestrator: TelemetryOrchestrator | None = None
        self._wired = False

    def wire(self) -> None:
        if self._wired:
            return

        classifier = TelemetryEventClassifier()
        session_manager = TelemetrySessionManager(self._session_path)
        enricher = TelemetryEventEnricher(self._app_version)
        recorder = TelemetryRecordingCapability()

        self._orchestrator = TelemetryOrchestrator(
            recorder=recorder,
            classifier=classifier,
            session_manager=session_manager,
            enricher=enricher,
        )
        self._wired = True

    @property
    def agent(self) -> TelemetryOrchestrator:
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("TelemetryContainer not wired — call wire() first")
        return self._orchestrator


def create_telemetry_feature(
    session_path: FilePath,
    app_version: VersionString | None = None,
) -> TelemetryOrchestrator:
    container = TelemetryContainer(session_path, app_version)
    container.wire()
    return container.agent
```

```

```
