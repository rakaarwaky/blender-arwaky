# Review Plan: diagnostics — Backend Developer

## Summary

Reviewed the diagnostics module source (`modules/diagnostics/src/`) against FR-DIA-001…005 and the AES rule set. The module exposes a unified `DiagnosticsCapability` (the composer) that correctly implements the five shared diagnostics protocols (`HealthCompositionProtocol`, `MetricsCollectionProtocol`, `AuditEmissionProtocol`, `LoggingPolicyProtocol`, `DiagnosticsSnapshotProtocol`) — signatures match, so AES403 conformance holds for the composer. However, the module has one CRITICAL AES bypass defect, two correctness/quality defects, and is partially un-importable due to an **external gateway-module break** that is out of diagnostics scope.

The most severe *in-scope* issue is a forbidden `type: ignore[override]` bypass comment (AES304, CRITICAL) in the metrics collector, plus a capability that imports a contract symbol (`IMetricsProvider`) from the wrong layer (gateway taxonomy, where it does not exist), and a dead attribute in the event bus. These are fixed this cycle. Deeper FRD business-rule gaps (ingestion-time redaction, staleness, fallback buffering, subsystem probing) are structural and require cross-module dependencies (security-policy redaction, config, subsystem adapters); they are catalogued as deferred findings, not fixed here to respect module scope.

## Findings by Category

### Architecture & Layer Compliance

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| A1 | BLOCKER (external) | Importing any gateway taxonomy submodule triggers `modules.gateway.__init__`, which raises `NameError: name 'TransportOutcomeVO' is not defined` at `modules/gateway/src/capabilities_code_execution_executor.py:157`. This prevents `contract_event_bus_protocol`, `capabilities_metrics_collector`, `surface_server_diagnostics_controller`, and `root_diagnostics_container` from importing. Out of diagnostics scope. | gateway module | Report to gateway-focused cycle; do NOT modify gateway per loop rules. |
| A2 | 🟡 WARNING | `IMetricsProvider` is imported from `modules.gateway.src.taxonomy_server_vo`, but it is **not defined there** — it lives in `modules/diagnostics/src/contract_metrics_protocol.py`. When the A1 blocker is resolved this line will raise `ImportError`. | `capabilities_metrics_collector.py:32` | Import `IMetricsProvider` from the local contract; keep `ServerMetrics` from gateway taxonomy. |
| A3 | 🟡 WARNING | Two divergent metrics mechanisms exist: `DiagnosticsCapability.collect_metrics_snapshot` (pull API) and `MetricsCollector` (event-driven, from `InMemoryEventBus`). Only `DiagnosticsCapability` is wired in `root_diagnostics_container`; `MetricsCollector` and `surface_server_diagnostics_controller` are never wired → capabilities/surface orphans (AES503/AES506). | `root_diagnostics_container.py`, `capabilities_metrics_collector.py`, `surface_server_diagnostics_controller.py` | Reconcile in a future wiring cycle; out of scope for this review (would change container composition). |

### Security

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| S1 | 🟡 WARNING | `emit_audit_event` stores records in a plain `list` with no redaction of sensitive fields and no fallback buffering/overflow handling. FR-DIA-003 requires ingestion-time redaction via security-policy rules and fallback buffering with oldest-drop on overflow. | `capabilities_diagnostics_composer.py:106-124` | Deferred: requires security-policy redaction contract + config; cross-module. |
| S2 | 🟡 WARNING | `log_record` appends to a buffer and forwards to `logging` with **no redaction** of `message`/`fields`. FR-DIA-004 mandates redaction at ingestion before any destination write, debug verbosity must never bypass it, and backpressure must drop oldest with a drop counter. | `capabilities_diagnostics_composer.py:127-150` | Deferred: same cross-module redaction dependency as S1. |

### Performance

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| P1 | 🟢 INFO | Latency lists are capped at 100 samples (good), but there is no windowed aggregation or explicit counter-reset indicator (FR-DIA-002). | `capabilities_metrics_collector.py:59-61,86-87,121-122` | Deferred: timestamped windows + reset flag need config; out of scope. |

### Error Handling

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| E1 | 🔴 CRITICAL | Forbidden bypass comment `type: ignore[override]` (AES304). The override signature is identical to `IEventSubscriber.handle`, so the suppression is spurious and masks nothing legitimate. | `capabilities_metrics_collector.py:63` | Remove the comment; signature already matches the base. |
| E2 | 🟡 WARNING | Dead attribute `self._lock = False` is assigned but never read — misleading no-op state implying threading safety that does not exist. | `capabilities_event_bus.py:27` | Remove the attribute (asyncio single-threaded model needs no lock). |
| E3 | 🟢 INFO | `pending_operations` and `running_operations` counters are initialised but never incremented by any event handler, so FR-DIA-002 gauges are permanently zero. | `capabilities_metrics_collector.py:46-47,142-143` | Deferred: requires defining which events drive pending/running transitions; needs event semantics clarity. |

## Violations

- **AES304 (CRITICAL):** `type: ignore[override]` in `capabilities_metrics_collector.py:63`.
- **AES201 (import correctness):** `IMetricsProvider` pulled from gateway taxonomy instead of the diagnostics contract layer (`capabilities_metrics_collector.py:32`). Not a strict layer-direction violation (taxonomy is an allowed import for capabilities) but a symbol-location error that breaks at runtime.
- **AES203/quality:** dead `self._lock` attribute in `capabilities_event_bus.py`.
- No AES101/AES102 (naming) violations — all files follow `prefix_concept_suffix`.
- **No violation** for composer↔protocol conformance (AES403 satisfied).
- External: gateway `TransportOutcomeVO` NameError (A1) — not a diagnostics-layer violation but a hard import blocker.

## Action Items

- [x] 🔴 Fix E1: remove `type: ignore[override]` (AES304).
- [x] 🟡 Fix A2: repoint `IMetricsProvider` import to local `contract_metrics_protocol`.
- [x] 🟡 Fix E2: remove dead `self._lock` attribute.
- [ ] 🟡 Deferred S1/S2: implement ingestion-time redaction + fallback buffering (needs security-policy contract + config).
- [ ] 🟡 Deferred A3: reconcile/wire `MetricsCollector` and `ServerDiagnosticsController` in the container.
- [ ] 🟢 Deferred E3/P1: pending/running gauges + windowed aggregation.

## Fixed Code

### E1 — `capabilities_metrics_collector.py` (remove bypass comment)

```python
# BEFORE
    async def handle(self, event: ServerEvent) -> None:  # type: ignore[override]
        """Handle events and update metrics counters."""

# AFTER
    async def handle(self, event: ServerEvent) -> None:
        """Handle events and update metrics counters."""
```

### A2 — `capabilities_metrics_collector.py` (correct `IMetricsProvider` source)

```python
# BEFORE
from modules.gateway.src.taxonomy_server_vo import IMetricsProvider, ServerMetrics

# AFTER
from modules.diagnostics.src.contract_metrics_protocol import IMetricsProvider
from modules.gateway.src.taxonomy_server_vo import ServerMetrics
```

### E2 — `capabilities_event_bus.py` (remove dead attribute)

```python
# BEFORE
    def __init__(self) -> None:
        self._subscribers: list[IEventSubscriber] = []
        self._lock = False  # Not using threading; asyncio handles concurrency

# AFTER
    def __init__(self) -> None:
        self._subscribers: list[IEventSubscriber] = []
```
