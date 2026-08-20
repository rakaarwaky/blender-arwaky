# FRD — Telemetry Feature

## System Overview
The Telemetry module collects anonymous usage analytics on an opt-in basis only. It answers product questions (which capabilities are used, where workflows fail) without identifying the user. It maintains a strict separation from operational observability (diagnostics).

## Functional Requirements

### FR-001: Record and Classify Anonymous Events
- **Description**: Capture anonymous usage records when consent is active, and classify them into fixed taxonomies.
- **Input**: Usage event (action type, feature area, operation type, outcome).
- **Output**: Buffered anonymous record.
- **Business Rules**: Nothing recorded unless consent active. PII scrubbing at ingestion via `security` patterns. Categorization at recording time. Never transmits free-form content or raw payloads.
- **Edge Cases**: Consent withdrawn mid-session; buffer full; action type not allowlisted; uncategorizable event.
- **Error Handling**: Invalid records silently dropped with internal counter; `validation_error` logged via diagnostics.

### FR-002: Session Management and Environment Enrichment
- **Description**: Manage unlinkable session IDs and attach coarse version-level context to batches.
- **Input**: Session lifecycle triggers, environment probes.
- **Output**: Session state, Environment metadata stamped on batch.
- **Business Rules**: Session ID from collision-resistant random source. Rotates after timeout with no stored linkage. Environment limited to OS family, runtime/Blender/app major.minor versions. No hostnames or hardware IDs.
- **Edge Cases**: Corrupt session state; restart inside/outside rotation window; version detection unavailable.
- **Error Handling**: `session_state_error` triggers fresh session; `transmission_error` discards batch after retries.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `record_event` | `action_type`, `outcome` | `InternalAck` | Internal: Buffer anonymous event |
| `transmit_batch` | None | `InternalAck` | Internal: Send batch to backend |

## Integration Points

- **3rd Party**: Product Analytics Backend (Vendor-operated).
- **Internal**: `config` (consent toggle, endpoint), `security` (PII redaction patterns).

## Non-functional Requirements (Detailed)

- **Performance**: Async recording and batching. Never blocks main operations. Backpressure drops oldest records.
- **Security**: Strict opt-in. PII scrubbed at ingestion. No machine fingerprinting. Buffers separate from logs.
- **Scalability**: Bounded local buffer. Transmission retries bounded before discard.

## Test Scenarios / QA Checklist

- [ ] Verify zero records/buffers/transmissions when opt-in is disabled.
- [ ] Verify consent withdrawal immediately stops collection and discards untransmitted buffer.
- [ ] Verify session ID rotates with no stored linkage to previous ID.
- [ ] Verify environment metadata excludes hostnames, usernames, and hardware IDs.
- [ ] Verify telemetry errors never propagate into product operation results.

## Assumptions & Constraints

- Telemetry is NOT for operational debugging (diagnostics owns debugging).
- Telemetry never feeds error handling, health checks, or support flows.

## Glossary

- **PII (Personally Identifiable Information)**: Data that can identify a user, strictly scrubbed by telemetry.
- **Session Rotation**: Process of generating a fresh, unlinkable session ID after a configured timeout.
- **UnifiedEnvelope**: Not used for telemetry transmission; telemetry uses its own anonymous batch schema.

## Reference

- PRD: `./PRD.md`
- Depends On: `config`, `security`
