# FRD — Diagnostics & Observability Feature

## Purpose

Single observability authority. Every other feature reports into it; nothing computes its own health, keeps its own log format, or emits its own audit stream. Turns scattered runtime signals into one honest, redacted, point-in-time picture — available to CLI, MCP, and internal consumers through one canonical surface. Features do the work; diagnostics tells the truth about it.

## Scope

- Health status composition across launcher, gateway, config, providers, job capacity
- Bounded health probes with staleness indication
- Operational metrics collection with windowed aggregation
- Structured local logging with ingestion-time redaction
- Audit event emission for security violations, connection failures, task failures, destructive actions
- Trace correlation by tracking ID across logs, metrics, audit
- Diagnostics snapshot for CLI/MCP consumers
- Overall health derivation (healthy/degraded/unhealthy)
- Sink failure tolerance with fallback buffering
- Log rotation and retention policy

## Out of Scope

Anonymous analytics, domain business rules, settings loading, task execution, connection mechanics, repair/self-healing, remote log shipping, alerting/notifications, long-term metrics persistence beyond retention window.

## Depends On

launcher (process liveness/readiness), gateway (connection state, transport counters), dispatcher (routing/validation/completion counters), job (task lifecycle counters, capacity), security policy (redaction rules, violation reporting), config (log level, destinations, intervals, retention).

## Provides To

CLI, MCP layer, internal observability consumers across all features.

## Functional Requirements

### FR-DIA-001: Compose System Health

- **Description**: Aggregate subsystem states into one composed health view with bounded probes and explicit staleness
- **Input**: Health request (optional subsystem filter, probe depth)
- **Output**: Composed health (overall status, per-subsystem map, probe durations, staleness indicators, timestamp)
- **Rules**: Composes health only — never repairs/restarts/mutates. Covers: launcher status (liveness, readiness, executable), gateway connection (state, last liveness, protocol, reconnect count), config validity (loaded, warnings, mode), asset provider availability (optional, non-blocking), job capacity (active/limit, queue depth). Each subsystem probe bounded by configured timeout — slow subsystem → degraded/unknown, not stalled composition. Overall status: healthy (all required green), degraded (any stale/timeout), unhealthy (any failed/unreachable). Provider availability advisory only. Stale data indicated with delta. Read-only, idempotent. May cache within freshness tolerance.
- **Edge Cases**: Launcher not started, gateway mid-reconnect, permissive fallback with warnings, provider rate-limited, capacity exhausted, subsystem unresponsive, conflicting reports, first run before init, clock skew, freshness boundary
- **Error Handling**: Probe timeout degrades subsystem; state error for corrupt diagnostics state; always returns result even when multiple subsystems unreachable

### FR-DIA-002: Collect Operational Metrics

- **Description**: Pull counters/gauges/latency summaries from features at configured interval, expose as immutable snapshots
- **Input**: Collection cycle (interval-driven); snapshot request (on-demand)
- **Output**: Metrics snapshot (counters, gauges, latency summaries, collection timestamp, freshness indicators)
- **Rules**: Pull-based at interval; features expose counters. Required: pending ops gauge, queue depth, reconnect counter, execution/command latency, failed request counter, security violation counter, task created/failed/completed counters, active task gauge. Counters monotonic per lifetime; restart resets with indicator. Latency summaries: count, min, max, median/percentile. Collection lightweight, non-blocking; slow/missing source → stale, not fatal. Snapshot immutable, safe for concurrent consumers. No request payloads, code, credentials, or user data. Stable naming/units across releases. Isolation per source. Windowed aggregation distinguishes recent vs lifetime.
- **Edge Cases**: Source unavailable/not-yet-initialized, interval skew, zero samples, counter reset, high-cardinality labels, collection overrunning interval, memory pressure
- **Error Handling**: Warning + source marked stale; snapshot from remaining sources; config error for invalid interval/retention

### FR-DIA-003: Emit Audit Events

- **Description**: Immutable audit records for security-relevant and operationally significant activity with guaranteed fallback delivery
- **Input**: Audit context (category, severity, source feature, operation type, redacted target metadata, correlation ID, timestamp)
- **Output**: Audit record + emission status
- **Rules**: Auditable: security violations (all categories), connection failures/loss, task failures/timeouts, destructive actions (deletion, destructive modifier, forced termination). Security violations audited even when general emission disabled. Record: category, severity, source, operation, redacted target, correlation ID, timestamp, confirmation state. Immutable once emitted; correction = new record. Redaction before emission (no raw code/tokens/credentials/paths). Non-blocking to originating op — audit trouble → fallback buffering, never user-facing error. Buffer overflow drops oldest with warning. High-frequency categories rate-limited/grouped with suppression count. Separate from logs; own retention. Destructive actions: confirmed/unconfirmed/policy-overridden.
- **Edge Cases**: Sink unavailable, buffer overflow, flood of violations, sensitive value in context, missing correlation ID, clock skew, retention race, toggle conflict with mandatory security auditing, redaction failure
- **Error Handling**: Emission → fallback buffer + warning; redaction failure → mask field entirely; original operation outcome never altered

### FR-DIA-004: Structured Logging Policy

- **Description**: One structured logging policy for whole system with redaction at ingestion
- **Input**: Log record (level, source feature, message, structured fields, tracking ID)
- **Output**: Sanitized structured log entry to configured destinations
- **Rules**: All features log through diagnostics policy — no private log formats/destinations. Consistent fields: timestamp, level, source, message, structured fields, tracking ID. Hierarchy: debug/info/warning/error; active level from config. Destinations from config (file + streams). Redaction at ingestion via security policy rules. Redaction failure → mask entire payload. Debug never bypasses redaction. No raw code/tokens/credentials/passwords/paths at any level. Non-blocking — buffer + drop oldest under backpressure with drop counter. Log rotation per size cap with bounded history. Oversized records truncated after redaction with marker. Best-effort ordering per source.
- **Edge Cases**: Invalid config, unwritable destination, disk full, flood under backpressure, sensitive value in free-text, oversized record, conflicting patterns, level filter silencing errors, rotation racing write, destination removed at runtime
- **Error Handling**: Config error for invalid level/destination; unwritable → fallback or in-memory ring with warning; logging failure never propagates to caller

### FR-DIA-005: Provide Diagnostics Snapshot

- **Description**: Serve one canonical point-in-time snapshot combining health, metrics, recent audit summary, config metadata
- **Input**: Snapshot request (optional detail level, section filter)
- **Output**: Diagnostics snapshot (health, metrics, audit summary, config validity, system version/protocol, staleness indicators)
- **Rules**: CLI/MCP consume snapshots — never probe subsystems or compute health themselves. Consistent point-in-time view from composed state. Detail: summary (safe for routine) or full (per-subsystem/metric depth). Section filter: health/metrics/audit only. Identical shape for all consumers; formatting belongs to consumer. Read-only, idempotent. Bounded latency — reuse composed state, recompute only when freshness expired. Stale sections carry staleness indicators. No secrets/raw code/credentials/sensitive paths; audit summary = categories+counts. First run with no history → empty-window indicators.
- **Edge Cases**: Snapshot during composition, partial data, all subsystems down, detail level exceeding max, no metrics history, empty audit summary, sensitive field in metadata, concurrent requests, freshness boundary
- **Error Handling**: State error → partial snapshot with warnings; config error for invalid detail level/section filter

## Error Categories

- state error — diagnostics internal state corrupt/inconsistent
- configuration error — logging/metrics/audit config invalid
- emission error — audit/log sink unavailable, fallback engaged
- collection error — metrics source unavailable/stale (warning, not failure)
- probe timeout error — health probe exceeded duration

## Events

- health check composed (overall + per-subsystem status)
- health degraded (transition to degraded/unhealthy)
- metrics snapshot (collection complete with freshness)
- audit event emitted (category, severity, emission path)
- audit sink recovered (fallback buffer flushed)
- log redaction failure (payload masked after redaction failure)

Payloads: category, section status, affected subsystem/source, counts, duration, correlation ID. Never: raw audit bodies, secrets, tokens, credentials, raw code, sensitive paths.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| structured_log_level | Active level across features | info |
| local_log_destination | File/stream for structured logs | Platform-standard location |
| log_rotation_size_cap | Max file size before rotation | Conservative |
| metrics_collection_interval | Pull frequency | Periodic (seconds) |
| metrics_retention_window | Windowed aggregation duration | Bounded (minutes) |
| health_probe_timeout | Max per-subsystem probe | Short |
| health_freshness_tolerance | Cache TTL for repeated requests | Short |
| audit_emission_toggle | General audit enabled | Enabled |
| mandatory_security_auditing | Security violations always audited | Always enabled |
| audit_retention_window | Record availability | Bounded (hours) |
| snapshot_default_detail_level | Default when omitted | summary |

## QA Checklist

- [ ] Health composes launcher, gateway, config, job capacity
- [ ] Provider availability advisory-only (no overall status impact)
- [ ] Slow subsystem → degraded, not stalled
- [ ] Overall status: healthy/degraded/unhealthy deterministically
- [ ] Stale data carries staleness indicator
- [ ] Metrics collected: pending ops, reconnect count, latency, failed requests, violations, task counts
- [ ] Latency: count, min, max, median/percentile
- [ ] Counter reset after restart has reset indicator
- [ ] Unavailable source → stale, snapshot still produced
- [ ] Metrics immutable + safe for concurrent access
- [ ] Audit: security violations, connection failures, task failures, destructive actions
- [ ] Security violations audited regardless of toggle
- [ ] Records immutable; correction = new record
- [ ] Destructive records distinguish confirmed/unconfirmed/overridden
- [ ] Sink failure → fallback buffer, no op impact
- [ ] Flood rate-limited with suppression count
- [ ] Structured logs from all features, consistent shape
- [ ] No raw code/tokens/secrets at any level
- [ ] Redaction at ingestion; failure → mask entire payload
- [ ] Debug never bypasses redaction
- [ ] Backpressure drops oldest, counter exposed
- [ ] Rotation respects size cap
- [ ] CLI/MCP consume snapshot, never compute themselves
- [ ] Identical shape for all consumers
- [ ] Snapshot bounded latency via reuse of composed state
- [ ] First run → empty-window indicators, not misleading zeros
- [ ] Tracking ID correlates logs/metrics/audit
- [ ] No feature maintains private log format or health computation
