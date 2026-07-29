# FRD — Telemetry Feature

## Purpose

Collects anonymous usage analytics on opt-in basis only. Answers product questions (which capabilities used, where workflows fail, which flows abandoned) without answering questions about who the user is. Separate stream from operational observability — diagnostics debugs the running system, telemetry understands the product. Never share data, storage, or purpose.

## Scope

- Opt-in consent (disabled by default)
- Consent withdrawal (immediate stop + buffer discard)
- Anonymous event recording (PII-free schema)
- Session ID generation, persistence, rotation
- Environment metadata enrichment (coarse fields only)
- Event categorization via fixed feature + operation taxonomy
- Background batching and transmission
- Local buffering with bounded size + drop-oldest backpressure
- Telemetry-specific observability via diagnostics logging

## Out of Scope

Operational logs/health checks/metrics/error diagnostics/security audit (diagnostics), user identification/fingerprinting, behavioral profiling, real-time streaming, A/B experimentation frameworks, backend storage/retention/access policies.

## Depends On

config (consent toggle, endpoint, session, transmission settings), security policy (redaction patterns for PII scrubbing).

## Provides To

Product analytics backend.

## Functional Requirements

### FR-TLM-001: Record Anonymous Usage Event

- **Description**: Capture single anonymous usage record when consent is active, strip all sensitive content at ingestion
- **Input**: Usage event (action type, feature area, operation type, outcome category, optional bucketed duration)
- **Output**: Buffered anonymous record (timestamp, action type, session ID, sanitized fields); acknowledgment internal only
- **Rules**: Nothing recorded/buffered/transmitted unless consent active. Withdrawal → immediate stop + discard all untransmitted records. Core fields: timestamp, action type, session ID. PII scrubbing at ingestion (before buffering) via security policy redaction patterns. Never: raw payloads/user content, object/scene/file names, paths, prompts/code/asset identifiers resolvable to user, error messages/stack traces, hostnames/usernames/network addresses. Outcome = category only (success/failure/rejected). Duration in coarse buckets. Only allowlisted action types recorded. Asynchronous + non-blocking. Bounded local buffer; backpressure → drop oldest + counter exposed via diagnostics logging. Records immutable once buffered. Individual records never retried; reliability at batch level.
- **Edge Cases**: Consent withdrawn mid-session, buffer full, action type not allowlisted, clock skew, duplicate from retried action, recording during transmission, consent race between record and batch
- **Error Handling**: Invalid record → silent drop with internal counter; recording failure never surfaces to originating op; consent race → non-collection wins

### FR-TLM-002: Classify and Categorize Events

- **Description**: Assign every event to fixed low-cardinality taxonomy; never transmit free-form content
- **Input**: Candidate event with raw action context
- **Output**: Categorized event (feature area, operation type, outcome category)
- **Rules**: Feature area taxonomy: object, scene, render, asset, configuration, connection. Operation type: create, update, delete, query, execute, search, import. Categorization at recording time, not transmission. Unknown/unmapped → bounded "other" category (raw names never transmitted). Outcome: success/failure/rejected/cancelled/timeout. Failure = which category failed, never why. Bounded cardinality; new categories require schema version increment. Deterministic: identical activity → identical categories across sessions/versions. No free-text fields. Schema version stamped on every record.
- **Edge Cases**: Action type after taxonomy freeze, ambiguous operation, feature under refactor, failed op with sensitive context, schema mismatch, high-cardinality attempt via extension
- **Error Handling**: Uncategorizable → dropped with counter (never transmitted raw); validation error via diagnostics logging only; schema mismatch → config warning

### FR-TLM-003: Manage Analytics Sessions

- **Description**: Random, unlinkable session ID surviving restarts within rotation window; clean linkage severance at rotation
- **Input**: Session lifecycle trigger (start, rotation timeout, consent change, reset)
- **Output**: Session state (current ID, creation timestamp, rotation deadline, consent record ref)
- **Rules**: ID from collision-resistant random source (never derived from machine/user/fs/hardware). Persists locally within allowed storage; same session across restarts within rotation window. Rotation after timeout → fresh ID, no stored linkage to previous. Rotation discards old ID; buffered records may still transmit, but no future refs will. Never correlates with diagnostics tracking IDs or gateway request IDs. Consent withdrawal → delete local session state entirely; re-opt-in → fresh session. Corrupt/unreadable → fresh session with warning, never app failure. Only ID, timestamps, consent ref stored. No machine fingerprint.
- **Edge Cases**: Corrupt/missing session state file, restart just inside/outside rotation window, clock skew, consent withdrawal + re-opt-in within one run, concurrent access, unwritable persistence, rotation racing batch transmission
- **Error Handling**: Session state error → fresh session generation; persistence failure → in-memory session + warning; rotation failure → immediate fresh session

### FR-TLM-004: Enrich Events with Environment Metadata

- **Description**: Attach coarse version-level context to outgoing batches; no identifying information
- **Input**: Environment probes (OS family, runtime version, Blender version, app version)
- **Output**: Environment metadata stamped on batch envelope
- **Rules**: Permitted: OS family, runtime major.minor, Blender major.minor, app version, telemetry schema version, consent record version. Versions truncated to major.minor (no patch/build — limits fingerprint surface). Forbidden: hostnames, usernames, paths, hardware IDs, precise locale, network addresses. Snapshot computed once per session (cached), not per event. Unavailable → explicit unknown marker. Changes during session → effect at next rotation (within-session consistency). Fixed schema per telemetry version. Lightweight probing, never blocks/prompts/requires elevated permissions.
- **Edge Cases**: Version detection unavailable, Blender not running, OS detection failure, runtime version changed mid-session, probe slow, schema version mismatch, all optional unknown → near-empty envelope
- **Error Handling**: Enrichment failure → transmit batch with unknown markers (never drop events); probing error → diagnostics logging only; config error for invalid metadata settings

## Hard Rules

- Telemetry NOT for operational debugging (diagnostics owns debugging; telemetry never feeds error handling, health checks, or support flows)
- Telemetry NOT store PII (scrubbing at ingestion, not before transmission; no downstream component receives raw content)
- Telemetry NOT block main operations (async recording/batching/transmission; failure invisible to product behavior)
- Opt-in only (disabled by default, silent until enabled, withdrawal → immediate stop + discard)
- Telemetry NOT identify machines/users (no fingerprinting, no cross-session identity, no derived identifiers)
- Telemetry remain separable (buffers/storage/stream never mixed with logs, metrics, or audit)

## Error Categories

- configuration error — invalid endpoint/interval/schema version (non-blocking)
- provider error — backend unreachable/rejecting batches (non-blocking)
- transmission error — batch delivery failed after retries → discard with counter (non-blocking)
- session state error — corrupt/unreadable → fresh session (non-blocking)
- validation error — invalid event shape/category → silent drop with counter (non-blocking)

Every error category is non-blocking by definition. No telemetry error may ever propagate into a product operation result.

## Events

Telemetry lifecycle signals flow through diagnostics logging, never telemetry pipeline itself.

- anonymous event recorded (buffered + category summary + consent state)
- session created/rotated (rotation reason)
- telemetry batch transmitted (record count + schema version)
- telemetry transmission failed (discarded after retry exhaustion + provider error)
- consent changed (opt-in/withdrawal + buffer action)

Payloads: category, record/batch counts, schema/consent versions, error category. Never: any telemetry record content, full session IDs, endpoint addresses beyond redacted host summary, user/machine identifying info.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| opt_in_toggle | Master consent switch | Disabled |
| analytics_endpoint | Backend destination | Vendor-operated |
| session_rotation_interval | Active duration before rotation | Bounded (hours) |
| background_transmission_interval | Batch delivery frequency | Periodic (minutes) |
| batch_size_cap | Max records per batch | Conservative |
| local_buffer_cap | Max buffered before drop-oldest | Conservative |
| environment_metadata_enabled | Attach coarse env fields | Enabled when consent active |
| transmission_retry_bound | Delivery attempts before discard | Small |

## QA Checklist

- [ ] Events recorded without PII across all action types
- [ ] Scrubbing at ingestion (not just before transmission)
- [ ] Raw payloads, names, paths, prompts, error messages never in records
- [ ] Failed ops → outcome category only (never message)
- [ ] Opt-in respected: disabled → zero records/buffers/transmissions
- [ ] Withdrawal → immediate stop + discard untransmitted buffer
- [ ] Re-opt-in → fresh session, no linkage
- [ ] Session ID: random source, not derived from machine/user attributes
- [ ] Persists across restarts within rotation; rotates with no stored linkage
- [ ] No correlation with diagnostics tracking IDs
- [ ] Corrupt session → fresh session, no app failure
- [ ] Environment: only OS family, runtime/Blender/app versions (major.minor)
- [ ] No hostname, username, path, hardware IDs
- [ ] Unknown → explicit marker; snapshot once per session
- [ ] Categorization deterministic + bounded; unknown → "other" (never raw)
- [ ] Recording never blocks originating op
- [ ] Backpressure → drop oldest, counter via diagnostics logging
- [ ] Backend unreachable → bounded retry then discard, invisible to product
- [ ] Buffers/storage separate from logs, metrics, audit
- [ ] Telemetry never used for debugging/error handling
- [ ] Lifecycle signals via diagnostics logging (not telemetry stream)
- [ ] Schema version on every batch
