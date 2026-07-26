# FRD — Diagnostics & Observability Feature

## Purpose

Manages health check composition, operational metrics, structured logging, audit events, and trace correlation for **blender-arwaky**.

This feature is the single observability authority of the system. Every other feature reports into it; nothing computes its own health, keeps its own log format, or emits its own audit stream. Diagnostics turns scattered runtime signals into one honest, redacted, point-in-time picture of the system — and makes that picture available to command-line tooling, the MCP layer, and internal consumers through one canonical surface.

The design principle is simple: features do the work, diagnostics tells the truth about it. Health is composed, never repaired. Metrics are collected, never inferred. Audit records are immutable once written. Logs are structured and sanitized at ingestion, not after the fact.

## Scope

- Health status composition across launcher, gateway, configuration, providers, and job capacity
- Bounded health probes with staleness indication
- Operational metrics collection with windowed aggregation
- Structured local logging policy with ingestion-time redaction
- Audit event emission for security violations, connection failures, task failures, and destructive actions
- Trace correlation by tracking identifier across logs, metrics, and audit records
- Diagnostics snapshot for CLI and MCP consumers
- Overall health derivation rules: healthy, degraded, unhealthy
- Sink failure tolerance with fallback buffering
- Log rotation and retention policy

## Out of Scope

- Anonymous product analytics
- Business rules of any domain feature
- Settings loading, owned by config feature
- Task execution, owned by job feature and executors
- Connection mechanics, owned by gateway feature
- Repair or self-healing actions
- Remote log shipping or centralized observability platforms
- Alerting and notification delivery
- Long-term metrics persistence beyond configured retention window

## Depends On

- launcher feature for process liveness and readiness state
- gateway feature for connection state, liveness metadata, and transport counters
- dispatcher feature for routing, validation, and completion counters
- job feature for task lifecycle counters and capacity state
- security policy feature for redaction rules and security violation reporting
- config feature for log level, destinations, intervals, and retention settings

## Provides To

- cli feature
- mcp layer
- internal observability consumers across all features

## Functional Requirements

### FR-DIA-001: Compose System Health

Diagnostics checks: launcher status, gateway connection status, config validity, asset provider availability (optional), job capacity.

- **Description**: Aggregate subsystem states into one composed health view with bounded probes and explicit staleness
- **Input**: Health request concept containing optional subsystem filter and optional probe depth
- **Output**: Composed health concept containing overall status, per-subsystem status map, probe durations, staleness indicators, and composition timestamp
- **Business Rules**:
  - Diagnostics composes health; it never repairs, restarts, or mutates any subsystem
  - Composed health must cover at least:
    - launcher status: process liveness, readiness classification, registered executable validity
    - gateway connection status: connection state, last liveness timestamp, negotiated protocol version, reconnect attempt count
    - config validity: snapshot loaded indicator, warning count, strict or permissive mode in effect
    - asset provider availability: optional, non-blocking reachability indication per enabled provider
    - job capacity: active task count against configured limit, queue depth where exposed
  - Each subsystem probe must be bounded by configured probe timeout so one slow subsystem cannot stall the whole composition
  - Probe that exceeds its timeout contributes a degraded or unknown status for that subsystem, never a failed composition
  - Overall status derives deterministically from subsystem states:
    - healthy when all required subsystems report healthy
    - degraded when any required subsystem reports degraded, stale, or bounded-timeout result
    - unhealthy when any required subsystem reports failed or unreachable
  - Provider availability is advisory and must not drive overall status by default
  - Health result must indicate which subsystem data is stale and by how much
  - Composition must be read-only and idempotent
  - Health result must be safe for user-facing display: no secrets, no raw payloads, no sensitive paths
  - Repeated health requests within a short window may serve cached composition when freshness tolerance allows
- **Edge Cases**: Launcher not started, gateway mid-reconnect, config in permissive fallback with warnings, provider rate-limited during probe, job capacity exhausted, subsystem unresponsive to probe, conflicting subsystem reports, first run before any subsystem initialized, clock skew affecting staleness math, cached composition served near freshness boundary
- **Error Handling**: Probe timeout degrades the affected subsystem rather than failing composition; state error when diagnostics internal state is corrupt; composition always returns a result even when multiple subsystems are unreachable

### FR-DIA-002: Collect Operational Metrics

Diagnostics collects: pending operations, reconnect count, execution latency, command latency, failed request count, security violation count, task created/failed/completed count.

- **Description**: Pull operational counters, gauges, and latency summaries from features at a configured interval and expose them as immutable snapshots
- **Input**: Collection cycle driven by configured interval; snapshot request concept for on-demand reads
- **Output**: Metrics snapshot concept containing counter values, gauge values, latency summaries, collection timestamp, and per-source freshness indicators
- **Business Rules**:
  - Collection is pull-based at configured interval; features expose counters rather than pushing continuously
  - Required metrics include at least:
    - pending operations gauge
    - queue depth gauge where exposed
    - reconnect counter
    - execution latency summary
    - command latency summary
    - failed request counter
    - security violation counter
    - task created, task failed, and task completed counters
    - active task gauge against capacity
  - Counters are monotonic within an application lifetime; restart resets counters with explicit reset indicator
  - Latency summaries must expose count, minimum, maximum, and median or percentile approximation rather than raw event streams
  - Collection from each source must be lightweight and non-blocking; a slow or missing source is marked stale, not fatal
  - Snapshot is immutable once produced and safe for concurrent consumers
  - Metrics must never carry request payloads, code content, credentials, or identifying user data
  - Metric naming and units must be stable across releases for consumer compatibility
  - Collection failures are isolated per source and surfaced as freshness warnings
  - Windowed aggregation should distinguish recent behavior from lifetime totals where configured
- **Edge Cases**: Source feature unavailable, source not yet initialized, interval skew between sources, no data collected yet, counter reset after restart, latency summary with zero samples, high-cardinality label explosion, collection cycle longer than interval, memory pressure from retained windows
- **Error Handling**: Collection error recorded as warning with affected source marked stale; snapshot still produced from remaining sources; configuration error when interval or retention settings are invalid

### FR-DIA-003: Emit Audit Events

Security violations, connection failures, task failures, and destructive actions must be audit-able.

- **Description**: Produce immutable audit records for security-relevant and operationally significant activity, with guaranteed fallback delivery
- **Input**: Audit context concept containing category, severity, source feature, operation type, redacted target metadata, correlation identifier, and timestamp
- **Output**: Audit record concept written to the audit stream, plus emission status
- **Business Rules**:
  - Auditable activity must include at least:
    - security violations of any category
    - connection establishment failures and connection loss
    - task failures and task timeout recoveries
    - destructive actions, including object deletion, destructive modifier application, and forced process termination
  - Security violations must be audited even when general audit emission is disabled by configuration
  - Audit record must include:
    - category and severity
    - source feature and operation type
    - redacted target metadata
    - correlation or tracking identifier when available
    - timestamp
    - confirmation state for destructive actions
  - Audit records are immutable once emitted; correction is a new record, never an edit
  - Record content must pass security policy redaction before emission; raw code, tokens, credentials, and sensitive paths are forbidden
  - Emission must not block or fail the originating operation; audit trouble degrades to fallback buffering, not user-facing errors
  - When audit sink is unavailable, records buffer to fallback storage and flush on recovery, with buffer overflow dropping oldest records and emitting warning
  - High-frequency audit categories may be rate-limited or grouped to protect the sink, with suppression count recorded
  - Audit stream is separate from normal application logs and subject to its own retention window
  - Destructive action records must distinguish confirmed, unconfirmed, and policy-overridden execution
- **Edge Cases**: Sink unavailable at emission, buffer overflow during sustained failure, flood of duplicate violations, sensitive value embedded in audit context, missing correlation identifier, clock skew ordering records oddly, retention purge racing new emission, audit disabled toggle conflicting with mandatory security auditing, redaction failure during record construction
- **Error Handling**: Emission error triggers fallback buffering and warning event; redaction failure masks the affected field entirely rather than emitting it raw; original operation outcome is never altered by audit trouble

### FR-DIA-004: Structured Logging Policy

All features send logs through diagnostics policy. Logs must be structured. Logs must not contain raw code, tokens, or secrets.

- **Description**: Define and enforce one structured logging policy for the whole system, with redaction applied at ingestion
- **Input**: Log record concept containing level, source feature, message, structured fields, and optional tracking identifier
- **Output**: Sanitized structured log entry written to configured destinations
- **Business Rules**:
  - All features log through the diagnostics policy; private per-feature log formats and destinations are not permitted
  - Every record is structured with consistent fields:
    - timestamp
    - level
    - source feature
    - message
    - structured field set
    - tracking identifier when available
  - Level hierarchy spans debug, info, warning, and error; active level comes from configuration
  - Destinations come from configuration and may include local log file and standard streams
  - Redaction is applied at ingestion using security policy rules, before any destination write
  - Redaction failure must mask the entire affected payload rather than risk leaking sensitive content
  - Debug verbosity must never bypass redaction; increased detail exposes structure, not secrets
  - Raw code text, tokens, credentials, passwords, and sensitive paths are forbidden in log content at every level
  - Logging must not block callers; records buffer and drop oldest under sustained backpressure with drop counter exposed
  - Log file rotation follows configured size cap, retaining bounded history
  - Oversized individual records are truncated with truncation marker after redaction
  - Records preserve best-effort ordering per source feature
- **Edge Cases**: Invalid logging configuration, destination unwritable, disk full, sustained log flood under backpressure, sensitive value embedded in free-text message, oversized record, conflicting redaction patterns, level filter misconfiguration silencing errors, rotation racing active write, destination removed during runtime
- **Error Handling**: Configuration error for invalid log level or destination settings; unwritable destination falls back to secondary destination or in-memory ring with warning; logging failure never propagates into the calling feature's operation result

### FR-DIA-005: Provide Diagnostics Snapshot

CLI and MCP retrieve health/metrics from diagnostics. They do not compute themselves.

- **Description**: Serve one canonical, point-in-time diagnostics snapshot combining health, metrics, recent audit summary, and configuration metadata
- **Input**: Snapshot request concept containing optional detail level and optional section filter
- **Output**: Diagnostics snapshot concept containing composed health, metrics snapshot, recent audit summary, config validity metadata, system version and protocol information, and per-section staleness indicators
- **Business Rules**:
  - CLI feature and MCP layer consume snapshots; they must never probe subsystems or compute health themselves
  - Snapshot is a consistent point-in-time view assembled from current composed state, not a live aggregation triggered per request
  - Detail levels include summary and full; summary is safe for routine display, full adds per-subsystem and per-metric depth
  - Section filter allows consumers to request health only, metrics only, or audit summary only
  - Snapshot shape is identical for all consumers; presentation formatting belongs to the consuming feature
  - Snapshot is read-only and idempotent
  - Snapshot must complete within bounded latency by reusing composed state and triggering recomposition only when freshness tolerance has expired
  - Stale sections carry explicit staleness indicators rather than silently presenting aged data
  - Snapshot must contain no secrets, raw code, credentials, or sensitive paths; audit summary carries categories and counts, not full record detail
  - First run with no metrics history returns empty-window indicators rather than misleading zero values
- **Edge Cases**: Snapshot requested while health composition in progress, partial subsystem data, all subsystems down, detail level exceeding configured maximum, no metrics history yet, audit summary empty, sensitive field slipping into section metadata, concurrent snapshot requests, freshness tolerance boundary
- **Error Handling**: State error when diagnostics internal state is corrupt; partial snapshot returned with per-section warnings rather than hard failure whenever possible; configuration error when detail level or section filter is invalid

## Error Categories

- state error — diagnostics internal state corrupt, inconsistent, or unrecoverable
- configuration error — logging, metrics, or audit configuration invalid
- emission error — audit or log sink unavailable and fallback engaged
- collection error — metrics source unavailable or stale, recorded as warning rather than failure
- probe timeout error — health probe exceeded bounded duration, degrading the affected subsystem

## Events

- health check composed event — composition completed with overall status and per-subsystem summary
- health degraded event — overall status transitioned from healthy to degraded or unhealthy
- metrics snapshot event — collection cycle completed with source freshness summary
- audit event emitted event — audit record written with category, severity, and emission path
- audit sink recovered event — fallback buffer flushed after sink recovery
- log redaction failure event — payload masked wholesale after redaction could not be applied safely

Event payloads should include:

- event category
- overall or section status where applicable
- affected subsystem or source feature
- counts and duration metadata
- correlation identifier when available

Event payloads must avoid:

- raw audit record bodies beyond category and count
- secrets, tokens, and credentials
- raw code content
- sensitive filesystem paths

## Configuration Keys


| Configuration Concept         | Description                                                             | Typical Default                       |
| ------------------------------- | ------------------------------------------------------------------------- | --------------------------------------- |
| Structured log level          | Active logging level across all features                                | Info                                  |
| Local log destination         | File path or stream target for structured logs within allowed locations | Platform-standard local log location  |
| Log rotation size cap         | Maximum log file size before rotation with bounded history              | Conservative size cap                 |
| Metrics collection interval   | Frequency of pull-based metrics collection                              | Periodic interval measured in seconds |
| Metrics retention window      | How long windowed aggregations remain available                         | Bounded window measured in minutes    |
| Health probe timeout          | Maximum duration per subsystem health probe                             | Short bounded probe limit             |
| Health freshness tolerance    | How long cached composition may serve repeated requests                 | Short tolerance window                |
| Audit emission toggle         | Whether general audit events are emitted                                | Enabled                               |
| Mandatory security auditing   | Whether security violations are audited regardless of toggle            | Always enabled                        |
| Audit retention window        | How long audit records remain available before purge                    | Bounded window measured in hours      |
| Snapshot default detail level | Detail level served when request omits it                               | Summary                               |

## QA Checklist

- [ ]  Health check composes status from launcher, gateway, config, and job capacity
- [ ]  Asset provider availability reported as advisory without driving overall status
- [ ]  Slow subsystem bounded by probe timeout and marked degraded rather than stalling composition
- [ ]  Overall status derives deterministically as healthy, degraded, or unhealthy
- [ ]  Stale subsystem data carries explicit staleness indicator
- [ ]  Health composition is read-only and never mutates subsystems
- [ ]  Metrics collected: pending operations, reconnect count, execution latency, command latency, failed request count, security violation count, task created/failed/completed count
- [ ]  Latency summaries expose count, minimum, maximum, and median or percentile
- [ ]  Counter reset after restart carries explicit reset indicator
- [ ]  Unavailable metrics source marked stale without failing snapshot
- [ ]  Metrics snapshot immutable and safe for concurrent consumers
- [ ]  Audit events emitted for security violations, connection failures, task failures, and destructive actions
- [ ]  Security violations audited even when general audit emission disabled
- [ ]  Audit records immutable once emitted with correction as new record
- [ ]  Destructive action audit records distinguish confirmation state
- [ ]  Audit sink failure engages fallback buffering without affecting originating operation
- [ ]  Audit flood rate-limited with suppression count recorded
- [ ]  Structured logs emitted in consistent structured shape from all features
- [ ]  Structured logs exclude raw code, tokens, and secrets at every level
- [ ]  Redaction applied at ingestion before any destination write
- [ ]  Redaction failure masks entire payload rather than leaking content
- [ ]  Debug verbosity never bypasses redaction
- [ ]  Log backpressure drops oldest records with drop counter exposed
- [ ]  Log rotation respects configured size cap
- [ ]  Invalid logging configuration raises configuration error
- [ ]  CLI and MCP retrieve snapshot from diagnostics rather than computing themselves
- [ ]  Snapshot identical in shape for CLI and MCP consumers
- [ ]  Snapshot completes within bounded latency using composed state
- [ ]  Snapshot sections carry staleness indicators
- [ ]  First run with no metrics history returns empty-window indicators
- [ ]  Tracking identifier correlates logs, metrics context, and audit records
- [ ]  No feature maintains private log format, destination, or health computation
