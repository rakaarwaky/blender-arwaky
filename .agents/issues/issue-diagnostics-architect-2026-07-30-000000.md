
### `.agents/issues/issue-diagnostics-architect-2026-07-30-000000.md`

```markdown
# Issue: diagnostics — Architectural Review & Refactoring

## Summary
The `diagnostics` feature has a mostly correct AES skeleton: shared contracts exist, capabilities implement protocol ABCs, the agent implements an aggregate, and a root container performs composition. However, the feature has several architectural defects that reduce safety, scalability, and AES compliance. The most serious problems are: (1) the snapshot capability is wired against ad-hoc local provider protocols that the concrete health/metrics capabilities do not implement, creating a broken runtime data path; (2) the diagnostics aggregate contract uses primitives, `Any`, and `dict` return types instead of stable taxonomy VOs, weakening the public facade and violating AES contract-role expectations; (3) redaction logic is duplicated inside two diagnostics capabilities instead of being delegated to a shared security mechanism; and (4) several capability file names describe actions instead of capability roles. These issues should be fixed before the diagnostics module becomes the canonical observability authority for CLI/MCP and other features.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `SnapshotProvisioner` depends on local provider protocols `_HealthProvider`, `_MetricsProvider`, `_AuditProvider`, but `HealthComposer` and `MetricsCollector` do not implement `get_health()` / `get_metrics()`. The container nevertheless passes them as providers, creating an invalid cross-component wiring that can fail at runtime. | `modules/diagnostics/src/capabilities_snapshot_provision.py:_HealthProvider`, `_MetricsProvider`; `modules/diagnostics/src/root_diagnostics_container.py:wire()` | Move provider abstractions to the contract layer and make `HealthComposer` / `MetricsCollector` implement them, or introduce explicit adapters in the root layer. |
| 2 | 🟡 WARNING | Contract-like protocols are defined inside capabilities files: `_AuditSink` in audit emission and `_HealthProvider` / `_MetricsProvider` / `_AuditProvider` in snapshot provision. When these are used by root composition, they belong in the contract layer. | `modules/diagnostics/src/capabilities_audit_emission.py:_AuditSink`; `modules/diagnostics/src/capabilities_snapshot_provision.py:_HealthProvider` | Extract externally consumed protocols to `modules/shared/src/diagnostics/contract_*_protocol.py`. Keep only purely internal helper types inside capabilities. |
| 3 | 🟡 WARNING | Diagnostics capabilities implement sensitive-value redaction locally using security constants. This duplicates security policy behavior inside the diagnostics layer. FRD states redaction is applied via security policy rules. | `modules/diagnostics/src/capabilities_audit_emission.py:_redact_sensitive`; `modules/diagnostics/src/capabilities_logging_policy.py:_redact_sensitive` | Delegate redaction to the security feature via `RedactSensitiveProtocol`, or extract a single shared redaction utility/security capability. |
| 4 | 🟡 WARNING | `DiagnosticsConfigVO` is defined in the root container file. Root is a composition layer and should not own taxonomy/value-object definitions. | `modules/diagnostics/src/root_diagnostics_container.py:DiagnosticsConfigVO` | Move `DiagnosticsConfigVO` to `modules/shared/src/diagnostics/taxonomy_diagnostics_vo.py` or a diagnostics config taxonomy file. |
| 5 | 🟢 INFO | `InMemoryEventBus` lives inside `capabilities_audit_emission.py`, but it is not an audit-emission capability and is not consumed by the audit emitter. | `modules/diagnostics/src/capabilities_audit_emission.py:InMemoryEventBus` | Remove it, or move it to a shared infrastructure/utility module and wire it intentionally. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Capability file name uses an action/domain noun `_emission` instead of the capability role `emitter`. Class name is `AuditEmitter`. | `modules/diagnostics/src/capabilities_audit_emission.py` | Rename to `capabilities_audit_emitter.py`. |
| 2 | 🟡 WARNING | Capability file name uses `_composition` instead of the capability role `composer`. Class name is `HealthComposer`. | `modules/diagnostics/src/capabilities_health_composition.py` | Rename to `capabilities_health_composer.py`. |
| 3 | 🟡 WARNING | Capability file name uses `_collection` instead of the capability role `collector`. Class name is `MetricsCollector`. | `modules/diagnostics/src/capabilities_metrics_collection.py` | Rename to `capabilities_metrics_collector.py`. |
| 4 | 🟡 WARNING | Capability file name uses `_provision` instead of the capability role `provisioner`. Class name is `SnapshotProvisioner`. | `modules/diagnostics/src/capabilities_snapshot_provision.py` | Rename to `capabilities_snapshot_provisioner.py`. |
| 5 | 🟢 INFO | `capabilities_logging_policy.py` is acceptable because `policy` is a recognized internal capability role, but the class behavior is closer to an enforcer/policy implementation. | `modules/diagnostics/src/capabilities_logging_policy.py` | Keep as-is or rename to `capabilities_logging_policy_enforcer.py` if role suffix policy allows. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `InMemoryEventBus` is instantiated by the container and exposed via `event_bus`, but it is never connected to `AuditEmitter`, `DiagnosticsOrchestrator`, or any subscriber flow. It is effectively orphaned infrastructure. | `modules/diagnostics/src/root_diagnostics_container.py:wire()`; `modules/diagnostics/src/capabilities_audit_emission.py:InMemoryEventBus` | Remove it, or wire it as the audit sink/event dispatcher with real subscribers. |
| 2 | 🟢 INFO | Unused `logging` import / logger binding in agent. The agent defines `logger` but never uses it. | `modules/diagnostics/src/agent_diagnostics_orchestrator.py:logger` | Remove `import logging` and `logger` if no agent-level logging is needed. |
| 3 | 🟢 INFO | Unused logger bindings in capabilities. | `modules/diagnostics/src/capabilities_health_composition.py:logger`; `modules/diagnostics/src/capabilities_metrics_collection.py:logger`; `modules/diagnostics/src/capabilities_snapshot_provision.py:logger` | Remove unused loggers or add meaningful structured log calls through the diagnostics logging policy. |
| 4 | 🟢 INFO | Unused import `field` from `dataclasses`. | `modules/diagnostics/src/root_diagnostics_container.py:import field` | Remove unused import. |
| 5 | 🟢 INFO | `_probe_launcher()` and `_probe_gateway()` are passthrough stubs that merely return the input status. They simulate bounded probes but do not probe real subsystems. | `modules/diagnostics/src/capabilities_health_composition.py:_probe_launcher`, `_probe_gateway` | Replace with real probe-provider abstractions or remove the probe simulation until real providers exist. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `capabilities_snapshot_provision.py` declares four type-like constructs: `_HealthProvider`, `_MetricsProvider`, `_AuditProvider`, and `SnapshotProvisioner`. This exceeds the AES403 maximum of 3 type declarations for a capability file. | `modules/diagnostics/src/capabilities_snapshot_provision.py:_HealthProvider`, `_MetricsProvider`, `_AuditProvider`, `SnapshotProvisioner` | Move the provider protocols to the contract layer, or replace them with one shared state-provider contract. |
| 2 | 🟡 WARNING | Public contract and aggregate methods use long primitive parameter lists. `collect_metrics_snapshot()` has nine primitive parameters, making evolution brittle. | `modules/shared/src/diagnostics/contract_metrics_collection_protocol.py:collect_metrics_snapshot`; `modules/shared/src/diagnostics/contract_diagnostics_aggregate.py:collect_metrics_snapshot` | Introduce request VOs such as `MetricsSampleVO` or `MetricsCollectionRequestVO`. |
| 3 | 🟡 WARNING | `HealthComposer` does not actually pull health from launcher/gateway/config/job providers. Callers must pass raw subsystem statuses into the capability. This couples callers to health derivation and weakens the FRD pull/probe model. | `modules/shared/src/diagnostics/contract_health_composition_protocol.py:compose_health`; `modules/diagnostics/src/capabilities_health_composition.py:compose_health` | Introduce `HealthProbeProtocol` or subsystem-specific provider contracts and inject them into `HealthComposer`. |
| 4 | 🟡 WARNING | `MetricsCollector` does not pull from metric sources. It receives raw counters from callers and accumulates unbounded latency buffers. There is no source isolation or retention window. | `modules/diagnostics/src/capabilities_metrics_collection.py:collect_metrics_snapshot` | Introduce `MetricsSourceProtocol`, bounded windowed buffers, and source-level freshness indicators. |
| 5 | 🟡 WARNING | Redaction logic is duplicated across audit emission and logging policy. This increases maintenance cost and creates divergence risk for security-sensitive behavior. | `modules/diagnostics/src/capabilities_audit_emission.py:_redact_sensitive`; `modules/diagnostics/src/capabilities_logging_policy.py:_redact_sensitive` | Extract one shared redaction mechanism or delegate to security `RedactSensitiveProtocol`. |
| 6 | 🟡 WARNING | `DiagnosticsConfigVO` contains `health_probe_timeout_seconds` and `freshness_tolerance_seconds`, but the container does not pass them to `HealthComposer`. Configuration is defined but ignored. | `modules/diagnostics/src/root_diagnostics_container.py:DiagnosticsConfigVO`, `wire()` | Wire config values into `HealthComposer` construction. |
| 7 | 🟢 INFO | `LoggingPolicy` buffers records but does not implement configurable destinations, rotation, or retention described by FR-DIA-004. | `modules/diagnostics/src/capabilities_logging_policy.py:LoggingPolicy` | Introduce a destination/rotation strategy if this module is intended to be the production logging authority. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `IDiagnosticsAggregate` returns `Any` or `dict[str, Any]` instead of concrete taxonomy VOs. The orchestrator implementation returns VOs, but the aggregate facade hides them. Surface consumers cannot rely on stable typed shapes. | `modules/shared/src/diagnostics/contract_diagnostics_aggregate.py:IDiagnosticsAggregate` | Change aggregate methods to return `HealthDetailsVO`, `MetricsSnapshotVO`, `AuditRecordVO`, `LogResultVO`, and `DiagnosticsSnapshotVO`. |
| 2 | 🔴 CRITICAL | Aggregate `emit_audit_event()` omits `target_metadata`, while the protocol and orchestrator include it. Destructive-action metadata cannot flow through the public aggregate facade without contract divergence. | `modules/shared/src/diagnostics/contract_diagnostics_aggregate.py:emit_audit_event`; `modules/diagnostics/src/agent_diagnostics_orchestrator.py:emit_audit_event` | Align aggregate signature with protocol, preferably using `AuditEventRequestVO`. |
| 3 | 🟡 WARNING | Protocol contracts use primitive types such as `str`, `int`, `float`, `bool`, `dict`, and `list[str]` directly in method signatures. This violates AES402 expectations that contracts use taxonomy VO/constant types for domain values. | `modules/shared/src/diagnostics/contract_health_composition_protocol.py`; `modules/shared/src/diagnostics/contract_metrics_collection_protocol.py`; `modules/shared/src/diagnostics/contract_audit_emission_protocol.py`; `modules/shared/src/diagnostics/contract_logging_policy_protocol.py`; `modules/shared/src/diagnostics/contract_snapshot_provision_protocol.py` | Replace primitive parameters with request VOs and use taxonomy constants for enums/statuses/levels. |
| 4 | 🟡 WARNING | Snapshot data flow is broken because provider protocols expected by `SnapshotProvisioner` are not implemented by the concrete health/metrics capabilities. | `modules/diagnostics/src/capabilities_snapshot_provision.py:get_snapshot`; `modules/diagnostics/src/root_diagnostics_container.py:wire()` | Make `HealthComposer` expose `get_health()` and `MetricsCollector` expose `get_metrics()`, or use root-layer adapters. |
| 5 | 🟢 INFO | Audit fallback path creates a replacement record with `emission_confirmed=True` and `emission_path="fallback"`. This may misrepresent delivery confirmation semantics. | `modules/diagnostics/src/capabilities_audit_emission.py:emit_audit_event` | Clarify whether fallback records are confirmed. Consider `emission_confirmed=False` with `emission_path="fallback"`, or add a separate buffered/delivered state. |

## Violations
- **AES101 / AES102 — Naming Convention / Suffix Prefix Rules**
  - Capability files use non-role suffixes: `_emission`, `_composition`, `_collection`, `_provision`.
- **AES202 — Mandatory Import**
  - `contract_diagnostics_aggregate.py` does not import taxonomy VOs despite defining the diagnostics aggregate facade.
- **AES203 — Unused Import**
  - Unused `logging` / logger in agent and some capabilities.
  - Unused `field` import in root container.
- **AES305 — Duplication Code**
  - `_SENSITIVE_KEY_PATTERNS`, `_is_sensitive_key`, and `_redact_sensitive` are duplicated in audit emission and logging policy capabilities.
- **AES402 — Contract Role**
  - Contract and aggregate methods use primitive types, `dict`, `list`, and `Any` instead of taxonomy VOs.
- **AES403 — Capabilities Role**
  - `capabilities_snapshot_provision.py` contains more than 3 type declarations.
- **AES405 — Agent Role**
  - Agent method signatures use `Any` through `dict[str, Any]`.
- **AES503-like concern — Capabilities Orphan / Unwired Component**
  - `InMemoryEventBus` is instantiated but not functionally connected to audit emission or orchestration.

No AES201 forbidden cross-layer import, AES205 circular import, or AES304 bypass-comment violations were identified in the provided diagnostics source.

## Action Items (For Developer)
- [ ] P0 Fix snapshot wiring: move snapshot provider protocols to contract layer and make `HealthComposer` / `MetricsCollector` implement them, or create explicit adapters in root.
- [ ] P0 Rewrite `IDiagnosticsAggregate` to return concrete VOs and accept request VOs.
- [ ] P0 Align aggregate `emit_audit_event()` with protocol by including `target_metadata`, preferably via `AuditEventRequestVO`.
- [ ] P1 Remove local protocols from `capabilities_snapshot_provision.py` so the file has <= 3 type declarations.
- [ ] P1 Replace primitive contract parameters with request/response VOs in all diagnostics protocols.
- [ ] P1 Extract duplicated redaction logic into one shared security utility or delegate to security `RedactSensitiveProtocol`.
- [ ] P1 Move `DiagnosticsConfigVO` from root to taxonomy and wire its values into `HealthComposer`.
- [ ] P2 Rename capability files to role-based names: `capabilities_audit_emitter.py`, `capabilities_health_composer.py`, `capabilities_metrics_collector.py`, `capabilities_snapshot_provisioner.py`.
- [ ] P2 Remove or intentionally wire `InMemoryEventBus`.
- [ ] P2 Remove unused imports and unused logger bindings.
- [ ] P2 Introduce real health probe and metrics source abstractions to satisfy FRD pull-based observability without forcing callers to pass raw primitives.

## Proposed Fixes / Reference Code

### 1. Add request/config VOs to taxonomy

File: `modules/shared/src/diagnostics/taxonomy_diagnostics_vo.py`

```python
@dataclass(frozen=True)
class HealthCompositionRequestVO:
    """Request VO for composing system health."""

    launcher_status: str = "unknown"
    gateway_status: str = "unknown"
    config_valid: bool = False
    job_capacity_available: bool = True


@dataclass(frozen=True)
class MetricsSampleVO:
    """Request VO carrying one metrics sample from callers/sources."""

    pending_operations: int = 0
    reconnect_count: int = 0
    execution_latency_ms: float = 0.0
    command_latency_ms: float = 0.0
    failed_requests: int = 0
    security_violations: int = 0
    tasks_created: int = 0
    tasks_failed: int = 0
    tasks_completed: int = 0


@dataclass(frozen=True)
class AuditEventRequestVO:
    """Request VO for emitting an audit event."""

    category: str
    severity: str
    source_feature: str
    operation_type: str
    target_metadata: dict[str, Any] = dc_field(default_factory=dict)
    correlation_id: str | None = None


@dataclass(frozen=True)
class LogRecordRequestVO:
    """Request VO for writing a structured log record."""

    level: str
    source_feature: str
    message: str
    fields: dict[str, Any] = dc_field(default_factory=dict)
    tracking_id: str | None = None


@dataclass(frozen=True)
class SnapshotRequestVO:
    """Request VO for diagnostics snapshot retrieval."""

    detail_level: str = "summary"
    section_filter: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiagnosticsConfigVO:
    """Diagnostics configuration resolved from config feature."""

    health_probe_timeout_seconds: float = 5.0
    freshness_tolerance_seconds: float = 10.0
    audit_max_buffer_size: int = 1000
    logging_max_buffer_size: int = 10000
```

Update `__all__` in `modules/shared/src/diagnostics/__init__.py` accordingly.

---

### 2. Fix diagnostics aggregate contract

File: `modules/shared/src/diagnostics/contract_diagnostics_aggregate.py`

```python
"""Diagnostics domain contract: diagnostics aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for diagnostics operations: health, metrics, audit, logging, snapshot.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import (
    AuditEventRequestVO,
    AuditRecordVO,
    DiagnosticsSnapshotVO,
    HealthCompositionRequestVO,
    HealthDetailsVO,
    LogRecordRequestVO,
    LogResultVO,
    MetricsSampleVO,
    MetricsSnapshotVO,
    SnapshotRequestVO,
)


class IDiagnosticsAggregate(ABC):
    """Aggregate facade for diagnostics operations."""

    @abstractmethod
    async def compose_health(
        self,
        request: HealthCompositionRequestVO,
    ) -> HealthDetailsVO: ...

    @abstractmethod
    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO,
    ) -> MetricsSnapshotVO: ...

    @abstractmethod
    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO: ...

    @abstractmethod
    async def log_record(
        self,
        request: LogRecordRequestVO,
    ) -> LogResultVO: ...

    @abstractmethod
    async def get_snapshot(
        self,
        request: SnapshotRequestVO,
    ) -> DiagnosticsSnapshotVO: ...
```

---

### 3. Update protocol contracts to use request VOs

Example file: `modules/shared/src/diagnostics/contract_health_composition_protocol.py`

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import (
    HealthCompositionRequestVO,
    HealthDetailsVO,
)


class HealthCompositionProtocol(ABC):
    """Protocol for composing system health from subsystem states."""

    @abstractmethod
    async def compose_health(
        self,
        request: HealthCompositionRequestVO,
    ) -> HealthDetailsVO: ...
```

Example file: `modules/shared/src/diagnostics/contract_metrics_collection_protocol.py`

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import (
    MetricsSampleVO,
    MetricsSnapshotVO,
)


class MetricsCollectionProtocol(ABC):
    """Protocol for collecting operational metrics from features."""

    @abstractmethod
    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO,
    ) -> MetricsSnapshotVO: ...
```

Example file: `modules/shared/src/diagnostics/contract_audit_emission_protocol.py`

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import (
    AuditEventRequestVO,
    AuditRecordVO,
)


class AuditEmissionProtocol(ABC):
    """Protocol for emitting immutable audit records."""

    @abstractmethod
    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO: ...
```

Example file: `modules/shared/src/diagnostics/contract_logging_policy_protocol.py`

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import (
    LogRecordRequestVO,
    LogResultVO,
)


class LoggingPolicyProtocol(ABC):
    """Protocol for enforcing structured logging policy with redaction."""

    @abstractmethod
    async def log_record(
        self,
        request: LogRecordRequestVO,
    ) -> LogResultVO: ...
```

Example file: `modules/shared/src/diagnostics/contract_snapshot_provision_protocol.py`

```python
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import (
    DiagnosticsSnapshotVO,
    SnapshotRequestVO,
)


class SnapshotProvisionProtocol(ABC):
    """Protocol for providing diagnostics snapshots to CLI/MCP consumers."""

    @abstractmethod
    async def get_snapshot(
        self,
        request: SnapshotRequestVO,
    ) -> DiagnosticsSnapshotVO: ...
```

---

### 4. Move snapshot provider protocols to contract layer

New file: `modules/shared/src/diagnostics/contract_health_state_provider_protocol.py`

```python
"""Diagnostics domain contract: health state provider protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import HealthDetailsVO


class HealthStateProviderProtocol(ABC):
    """Provides cached or freshly composed health state for snapshots."""

    @abstractmethod
    async def get_health(self) -> HealthDetailsVO | None: ...
```

New file: `modules/shared/src/diagnostics/contract_metrics_state_provider_protocol.py`

```python
"""Diagnostics domain contract: metrics state provider protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import MetricsSnapshotVO


class MetricsStateProviderProtocol(ABC):
    """Provides the latest metrics snapshot for diagnostics snapshots."""

    @abstractmethod
    async def get_metrics(self) -> MetricsSnapshotVO | None: ...
```

New file: `modules/shared/src/diagnostics/contract_audit_state_provider_protocol.py`

```python
"""Diagnostics domain contract: audit state provider protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import AuditSummaryVO


class AuditStateProviderProtocol(ABC):
    """Provides recent audit summary state for diagnostics snapshots."""

    @abstractmethod
    async def get_audit_summary(self) -> AuditSummaryVO | None: ...
```

Register all three in `modules/shared/src/diagnostics/__init__.py`.

---

### 5. Reduce type count in snapshot capability

File: `modules/diagnostics/src/capabilities_snapshot_provisioner.py`
Renamed from: `modules/diagnostics/src/capabilities_snapshot_provision.py`

```python
"""Capability: Diagnostics snapshot provisioner.

FR-DIA-005: Provide Diagnostics Snapshot
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.diagnostics.contract_audit_state_provider_protocol import (
    AuditStateProviderProtocol,
)
from modules.shared.src.diagnostics.contract_health_state_provider_protocol import (
    HealthStateProviderProtocol,
)
from modules.shared.src.diagnostics.contract_metrics_state_provider_protocol import (
    MetricsStateProviderProtocol,
)
from modules.shared.src.diagnostics.contract_snapshot_provision_protocol import (
    SnapshotProvisionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    DiagnosticsSnapshotVO,
    SnapshotRequestVO,
)


class SnapshotProvisioner(SnapshotProvisionProtocol):
    """Provide point-in-time diagnostics snapshots."""

    def __init__(
        self,
        health_provider: HealthStateProviderProtocol | None = None,
        metrics_provider: MetricsStateProviderProtocol | None = None,
        audit_provider: AuditStateProviderProtocol | None = None,
    ) -> None:
        self._health_provider = health_provider
        self._metrics_provider = metrics_provider
        self._audit_provider = audit_provider

    async def get_snapshot(
        self,
        request: SnapshotRequestVO,
    ) -> DiagnosticsSnapshotVO:
        sections = set(request.section_filter or ("health", "metrics", "audit_summary"))
        snapshot_parts: dict[str, Any] = {}

        if "health" in sections and self._health_provider:
            health = await self._health_provider.get_health()
            if health is not None:
                snapshot_parts["health"] = health

        if "metrics" in sections and self._metrics_provider:
            metrics = await self._metrics_provider.get_metrics()
            if metrics is not None:
                snapshot_parts["metrics"] = metrics

        if "audit_summary" in sections and self._audit_provider:
            audit = await self._audit_provider.get_audit_summary()
            if audit is not None:
                snapshot_parts["audit_summary"] = audit

        first_run = len(snapshot_parts) == 0

        return DiagnosticsSnapshotVO(
            health=snapshot_parts.get("health"),
            metrics=snapshot_parts.get("metrics"),
            audit_summary=snapshot_parts.get("audit_summary"),
            detail_level=request.detail_level,
            staleness_indicators={},
            first_run_indicator=first_run,
        )

    def __repr__(self) -> str:
        return "SnapshotProvisioner()"
```

This leaves only one type declaration in the capability file.

---

### 6. Make health and metrics capabilities implement snapshot provider contracts

File: `modules/diagnostics/src/capabilities_health_composer.py`
Renamed from: `modules/diagnostics/src/capabilities_health_composition.py`

```python
from modules.shared.src.diagnostics.contract_health_state_provider_protocol import (
    HealthStateProviderProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    HealthCompositionRequestVO,
)


class HealthComposer(HealthCompositionProtocol, HealthStateProviderProtocol):
    ...

    async def compose_health(
        self,
        request: HealthCompositionRequestVO,
    ) -> HealthDetailsVO: ...

    async def get_health(self) -> HealthDetailsVO | None:
        """Return the most recently composed health state."""
        return self._composition_cache
```

File: `modules/diagnostics/src/capabilities_metrics_collector.py`
Renamed from: `modules/diagnostics/src/capabilities_metrics_collection.py`

```python
from modules.shared.src.diagnostics.contract_metrics_state_provider_protocol import (
    MetricsStateProviderProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    MetricsSampleVO,
)


class MetricsCollector(MetricsCollectionProtocol, MetricsStateProviderProtocol):
    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._latency_buffers: dict[str, list[float]] = {}
        self._collection_timestamp: str = ""
        self._counter_reset_indicator: bool = False
        self._last_snapshot: MetricsSnapshotVO | None = None

    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO,
    ) -> MetricsSnapshotVO:
        ...
        self._last_snapshot = MetricsSnapshotVO(
            counters=dict(self._counters),
            latency_summaries=latency_summaries,
            freshness_indicators=freshness,
            collection_timestamp=self._collection_timestamp,
            counter_reset_indicator=self._counter_reset_indicator,
        )
        return self._last_snapshot

    async def get_metrics(self) -> MetricsSnapshotVO | None:
        """Return the latest metrics snapshot."""
        return self._last_snapshot
```

---

### 7. Update agent orchestrator to match aggregate contract

File: `modules/diagnostics/src/agent_diagnostics_orchestrator.py`

```python
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    AuditEventRequestVO,
    AuditRecordVO,
    DiagnosticsSnapshotVO,
    HealthCompositionRequestVO,
    HealthDetailsVO,
    LogRecordRequestVO,
    LogResultVO,
    MetricsSampleVO,
    MetricsSnapshotVO,
    SnapshotRequestVO,
)


class DiagnosticsOrchestrator(IDiagnosticsAggregate):
    ...

    async def compose_health(
        self,
        request: HealthCompositionRequestVO,
    ) -> HealthDetailsVO:
        return await self._health_composer.compose_health(request)

    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO,
    ) -> MetricsSnapshotVO:
        return await self._metrics_collector.collect_metrics_snapshot(sample)

    async def emit_audit_event(
        self,
        request: AuditEventRequestVO,
    ) -> AuditRecordVO:
        return await self._audit_emitter.emit_audit_event(request)

    async def log_record(
        self,
        request: LogRecordRequestVO,
    ) -> LogResultVO:
        return await self._logging_policy.log_record(request)

    async def get_snapshot(
        self,
        request: SnapshotRequestVO,
    ) -> DiagnosticsSnapshotVO:
        return await self._snapshot_provisioner.get_snapshot(request)
```

Remove unused `import logging` and `logger` from this file if no logging is performed.

---

### 8. Extract duplicated redaction logic

Preferred option: delegate to security `RedactSensitiveProtocol` via DI.

Fallback option if a shared utility is accepted:

New file: `modules/shared/src/security/utility_security_redactor.py`

```python
"""Security utility: stateless sensitive-value redaction."""

from __future__ import annotations

import re
from typing import Any

from .taxonomy_security_constant import REDACTION_SENSITIVE_PATTERNS

_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(re.compile(p) for p in REDACTION_SENSITIVE_PATTERNS)

_SENSITIVE_KEY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(rf"(?i)\b({p})\b", re.IGNORECASE)
    for p in (
        "password",
        "passwd",
        "secret",
        "token",
        "api[_-]?key",
        "access[_-]?key",
        "private[_-]?key",
        "credential",
    )
)


def is_sensitive_key(key: str) -> bool:
    """Return True if the key name looks like a secret holder."""
    return any(p.search(key) for p in _SENSITIVE_KEY_PATTERNS)


def redact_sensitive(value: object) -> Any:
    """Recursively mask sensitive values without mutating input objects."""
    if isinstance(value, str):
        text = value
        for pattern in _SENSITIVE_PATTERNS:
            text = pattern.sub("[REDACTED]", text)
        return text

    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, val in value.items():
            if is_sensitive_key(key) and isinstance(val, str):
                candidate = val
                for pattern in _SENSITIVE_PATTERNS:
                    candidate = pattern.sub("[REDACTED]", candidate)
                redacted[key] = "[REDACTED]" if candidate == val else candidate
            else:
                redacted[key] = redact_sensitive(val)
        return redacted

    if isinstance(value, (list, tuple)):
        return type(value)(redact_sensitive(item) for item in value)

    return value
```

Then in diagnostics capabilities:

```python
from modules.shared.src.security.utility_security_redactor import redact_sensitive
```

Remove duplicated `_SENSITIVE_KEY_PATTERNS`, `_is_sensitive_key`, and `_redact_sensitive` from:

- `modules/diagnostics/src/capabilities_audit_emission.py`
- `modules/diagnostics/src/capabilities_logging_policy.py`

If strict AES utility domain-agnosticism is enforced, replace this utility with an injected security capability implementing `RedactSensitiveProtocol`.

---

### 9. Fix root composition

File: `modules/diagnostics/src/root_diagnostics_container.py`

```python
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    DiagnosticsConfigVO,
)

from modules.diagnostics.src.capabilities_audit_emitter import AuditEmitter
from modules.diagnostics.src.capabilities_health_composer import HealthComposer
from modules.diagnostics.src.capabilities_logging_policy import LoggingPolicy
from modules.diagnostics.src.capabilities_metrics_collector import MetricsCollector
from modules.diagnostics.src.capabilities_snapshot_provisioner import SnapshotProvisioner


class DiagnosticsContainer:
    ...

    def wire(self) -> None:
        if self._wired:
            return

        health_composer = HealthComposer(
            probe_timeout_seconds=self._config.health_probe_timeout_seconds,
            freshness_tolerance_seconds=self._config.freshness_tolerance_seconds,
        )
        metrics_collector = MetricsCollector()
        audit_emitter = AuditEmitter(
            max_buffer_size=self._config.audit_max_buffer_size,
        )
        logging_policy = LoggingPolicy(
            max_buffer_size=self._config.logging_max_buffer_size,
        )
        snapshot_provisioner = SnapshotProvisioner(
            health_provider=health_composer,
            metrics_provider=metrics_collector,
            audit_provider=None,
        )

        self._orchestrator = DiagnosticsOrchestrator(
            health_composer=health_composer,
            metrics_collector=metrics_collector,
            audit_emitter=audit_emitter,
            logging_policy=logging_policy,
            snapshot_provisioner=snapshot_provisioner,
        )

        self._wired = True
```

Remove `DiagnosticsConfigVO` from this file after moving it to taxonomy.

Remove unused `field` import:

```python
from dataclasses import dataclass
```

Remove `InMemoryEventBus` unless it is intentionally wired:

```python
# Delete event_bus property and InMemoryEventBus instantiation if unused.
```

---

### 10. Rename capability files

```bash
git mv modules/diagnostics/src/capabilities_audit_emission.py \
       modules/diagnostics/src/capabilities_audit_emitter.py

git mv modules/diagnostics/src/capabilities_health_composition.py \
       modules/diagnostics/src/capabilities_health_composer.py

git mv modules/diagnostics/src/capabilities_metrics_collection.py \
       modules/diagnostics/src/capabilities_metrics_collector.py

git mv modules/diagnostics/src/capabilities_snapshot_provision.py \
       modules/diagnostics/src/capabilities_snapshot_provisioner.py
```

Update imports in:

- `modules/diagnostics/src/__init__.py`
- `modules/diagnostics/src/root_diagnostics_container.py`
- any tests or external consumers.

```

```
