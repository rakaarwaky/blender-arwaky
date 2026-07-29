# Review Plan: diagnostics — Business Analyst (Phase 2)

## Summary

The diagnostics module implements core observability capabilities (health composition, metrics collection, audit emission, structured logging) but has significant gaps between the FRD specification and implementation. Key issues include: missing redaction at ingestion in logging policy, no dedicated contract/capability for FR-DIA-005 snapshot provision, orchestrator importing capabilities directly instead of contracts, no probe timeout or staleness indicators, incomplete latency summaries, missing backpressure handling, and absent config consumption. The module needs structural fixes to comply with AES layer boundaries and behavioral fixes to meet FRD requirements.

## Findings by Category

### Requirements Clarity

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-DIA-004: No redaction at ingestion — `LoggingPolicy.log_record()` writes raw messages without any redaction, violating "Redaction at ingestion via security policy rules" and "No raw code/tokens/credentials/passwords/paths at any level" | `capabilities_logging_policy.py` lines 55-68 | Integrate security `SensitiveRedactor` or apply pattern-based redaction before log emission |
| 2 | 🔴 CRITICAL | FR-DIA-003: Audit records not truly immutable — `_audit_records` is a mutable list of mutable dicts; records can be modified after emission, violating "Immutable once emitted; correction = new record" | `capabilities_audit_emission.py` lines 45-58 | Use `types.MappingProxyType` or `dataclasses(frozen=True)` for audit records |
| 3 | 🔴 CRITICAL | FR-DIA-005: No dedicated contract/capability — snapshot provision is a method on the orchestrator, not a separate contract protocol and capability. Orchestrator violates "Orchestration only" by composing health + metrics + audit into snapshot | `agent_diagnostics_orchestrator.py` lines 133-160 | Create `contract_snapshot_provision_protocol.py` + `capabilities_snapshot_provision.py` |

### Business Flow

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 4 | 🔴 CRITICAL | Orchestrator imports capabilities directly — `agent_diagnostics_orchestrator.py` imports `HealthComposer`, `MetricsCollector`, `AuditEmitter`, `LoggingPolicy` instead of contract protocols. Violates "Agent must depend on Contract, not concrete implementations" and AES201 | `agent_diagnostics_orchestrator.py` lines 18-24 | Change imports to contract protocols; container wires contracts to capabilities |
| 5 | 🟡 WARNING | No probe timeout — FR-DIA-001 requires "Each subsystem probe bounded by configured timeout — slow subsystem → degraded/unknown, not stalled composition" but implementation has no timeout mechanism | `capabilities_health_composition.py` lines 34-62 | Add configurable timeout parameter; wrap probe calls with `asyncio.wait_for()` |
| 6 | 🟡 WARNING | No staleness indicators — FR-DIA-001 requires "Stale data indicated with delta" but implementation only stores a timestamp, no staleness delta or freshness threshold | `capabilities_health_composition.py` line 55 | Add `staleness_delta_seconds` field to response; configure freshness tolerance |
| 7 | 🟡 WARNING | Metrics latency summaries are single values — FR-DIA-002 requires "Latency summaries: count, min, max, median/percentile" but implementation stores single float per call | `capabilities_metrics_collection.py` lines 38-45 | Store latency as `{count, min, max, mean, p50, p95}` object; accumulate across calls |

### Logic Implementation

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 8 | 🟡 WARNING | No fallback buffering for audit sink failure — FR-DIA-003 requires "Emission → fallback buffer + warning" but event bus subscriber failures are logged without guaranteed delivery or fallback record | `capabilities_audit_emission.py` lines 68-75 | Add in-memory ring buffer as fallback when subscribers fail; flush on recovery |
| 9 | 🟡 WARNING | No backpressure handling in logging — FR-DIA-004 requires "buffer + drop oldest under backpressure with drop counter" but `LoggingPolicy._log_buffer` grows unbounded | `capabilities_logging_policy.py` lines 46-52 | Implement bounded deque; drop oldest when full; expose drop counter |
| 10 | 🟡 WARNING | No log rotation — FR-DIA-004 requires "Log rotation per size cap with bounded history" but not implemented | `capabilities_logging_policy.py` (entire file) | Add rotation by size cap; maintain bounded history |
| 11 | 🟡 WARNING | Config not consumed — FRD specifies config keys (`structured_log_level`, `metrics_collection_interval`, `health_probe_timeout`, etc.) but no config is passed to any capability | All capability files | Pass config object to capabilities on construction; wire in container |

### Testability & Acceptance Criteria

| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 12 | 🟢 INFO | `source_tool` parameter unused — All contract methods have `source_tool: ToolName | None = None` but capabilities never use it; it's passed through and ignored | All contract files, all capability files | Either use it for telemetry attribution or remove from protocol signatures |
| 13 | 🟢 INFO | No trace correlation across logs/metrics/audit — FRD mentions "Trace correlation by tracking ID across logs, metrics, audit" but implementations don't tie records together through shared tracking | `capabilities_logging_policy.py`, `capabilities_audit_emission.py` | Add correlation_id to all audit events and log entries; verify in snapshot |
| 14 | 🟢 INFO | No config-based behavior — FRD QA checklist has no items about config consumption, but FRD "Configuration Keys" section defines 10 keys that should affect behavior | `root_diagnostics_container.py` (no config injected) | Wire config to capabilities; add tests for config-driven behavior |

## Violations

| # | Code | File | Description |
|---|------|------|-------------|
| V1 | AES201 | `agent_diagnostics_orchestrator.py:18-24` | Agent imports capabilities directly instead of contract protocols — forbidden by layer boundary rules |
| V2 | AES403 (CapabilityTooManyTypes) | `capabilities_audit_emission.py` | Contains 2 types (`AuditEmitter` + `InMemoryEventBus`) — within limit but event bus is infrastructure, not business logic |
| V3 | AES504 | `utility_security_path.py` | Utility file exists but is NOT imported by any diagnostics capability (diagnostics has its own logging, no shared utility usage) |
| V4 | AES302 | `contract_health_composition_protocol.py`, `contract_metrics_collection_protocol.py`, `contract_audit_emission_protocol.py`, `contract_logging_policy_protocol.py` | Contract files are thin ABC wrappers — could be consolidated or have more comprehensive docstrings |

## Action Items
- [ ] CRITICAL Fix orchestrator to import contracts instead of capabilities (AES201)
- [ ] CRITICAL Create `contract_snapshot_provision_protocol.py` + `capabilities_snapshot_provision.py` for FR-DIA-005
- [ ] CRITICAL Add redaction at ingestion in `LoggingPolicy.log_record()` (FR-DIA-004)
- [ ] CRITICAL Make audit records immutable using frozen dataclasses or MappingProxyType (FR-DIA-003)
- [ ] WARNING Add probe timeout and staleness indicators to health composition (FR-DIA-001)
- [ ] WARNING Fix metrics latency summaries to include count/min/max/percentile (FR-DIA-002)
- [ ] WARNING Add fallback buffering for audit sink failure (FR-DIA-003)
- [ ] WARNING Add backpressure handling and log rotation (FR-DIA-004)
- [ ] INFO Remove or use `source_tool` parameter consistently across contracts and capabilities

## Fixed Code

{Will be filled during execution}
