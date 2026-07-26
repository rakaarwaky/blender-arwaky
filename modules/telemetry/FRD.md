# FRD —  Telemetry Feature

## Purpose

Collects anonymous usage analytics on an opt-in basis only for **blender-arwaky**.

This feature answers product questions — which capabilities are used, where workflows fail, which flows are abandoned — without ever answering questions about who the user is. It is a strictly separate stream from operational observability: diagnostics exists to debug the running system, telemetry exists to understand the product, and the two never share data, storage, or purpose.

Trust is the design constraint, not a compliance checkbox. Collection is off until the user turns it on, every record is stripped at ingestion, sessions are random and rotatable, and the pipeline is engineered so that it can never slow down, block, or corrupt a real operation. When telemetry and product behavior could ever conflict, product behavior wins.

## Scope

- Opt-in consent with disabled-by-default posture
- Consent withdrawal with immediate stop and buffer discard
- Anonymous event recording with PII-free schema
- Session identifier generation, persistence, and rotation
- Environment metadata enrichment with coarse fields only
- Event categorization through fixed feature and operation taxonomy
- Background batching and transmission
- Local buffering with bounded size and drop-oldest backpressure
- Telemetry-specific observability through diagnostics logging policy

## Out of Scope

- Operational logs, owned by diagnostics feature
- Health check, owned by diagnostics feature
- Metrics for debugging, owned by diagnostics feature
- Error diagnostics, owned by diagnostics feature
- Security audit, owned by security policy and diagnostics features
- User identification or machine fingerprinting
- Behavioral profiling or cohort tracking across sessions
- Real-time event streaming
- Backend storage, retention, or access policies beyond transmission
- A/B experimentation frameworks

## Depends On

- config feature for consent toggle, endpoint, session, and transmission settings
- security policy feature for redaction patterns applied during PII scrubbing

## Provides To

- Product analytics backend

## Functional Requirements

### FR-TLM-001: Record Anonymous Usage Event

Record event without PII. Event includes timestamp, action type, and session ID.

- **Description**: Capture a single anonymous usage record when and only when consent is active, stripping all sensitive content at ingestion
- **Input**: Usage event concept containing action type, feature area, operation type, outcome category, and optional bucketed duration
- **Output**: Buffered anonymous record concept containing timestamp, action type, session identifier, and sanitized fields; recording acknowledgment is internal only
- **Business Rules**:
  - Nothing is recorded, buffered, or transmitted unless consent is active; disabled telemetry produces zero side effects
  - Consent withdrawal immediately stops recording and discards all buffered but untransmitted records
  - Every record must include timestamp, action type, and session identifier as core fields
  - PII scrubbing applies at ingestion, before buffering, using security policy redaction patterns as baseline
  - Records must never contain:
    - raw payloads or user content
    - object names, scene names, or file names
    - filesystem paths
    - prompts, code text, or asset identifiers resolvable to user activity
    - error messages, stack traces, or diagnostic detail
    - hostnames, usernames, or network addresses
  - Outcome is recorded as category only, such as success, failure, or rejected — never as message
  - Duration is recorded in coarse buckets rather than precise measurements where precision could fingerprint usage patterns
  - Only allowlisted action types may be recorded; unlisted activity is ignored rather than passed through raw
  - Recording must be asynchronous and non-blocking; the originating operation never waits on telemetry
  - Local buffer is bounded; sustained backpressure drops oldest records with drop counter exposed through diagnostics logging
  - Records are immutable once buffered; correction is impossible by design
  - Individual records are never retried; reliability is handled at batch level
- **Edge Cases**: Consent withdrawn mid-session, buffer full under backpressure, action type not in allowlist, timestamp anomaly from clock skew, duplicate event from retried user action, recording attempted while transmission in progress, consent state changed between record and batch
- **Error Handling**: Invalid record shape dropped silently with internal counter; recording failure never surfaces into the originating operation; consent race resolved in favor of non-collection

### FR-TLM-002: Classify and Categorize Events

Categorize events by feature area and operation type. No raw payloads or user content.

- **Description**: Assign every recorded event to a fixed, low-cardinality taxonomy so analytics remain comparable across versions without carrying free-form content
- **Input**: Candidate event concept with raw action context
- **Output**: Categorized event concept with feature area, operation type, and outcome category
- **Business Rules**:
  - Feature area taxonomy covers product surfaces such as object, scene, render, asset, configuration, and connection
  - Operation type taxonomy covers interaction classes such as create, update, delete, query, execute, search, and import
  - Categorization happens at recording time, not at transmission time
  - Unknown or unmapped action types resolve to a bounded other category; raw action names are never transmitted
  - Outcome categories are fixed: success, failure, rejected, cancelled, and timeout
  - Failure categorization records which category failed, never why it failed; diagnostic detail belongs to diagnostics feature
  - Taxonomy cardinality must remain bounded; new categories require explicit schema version increment
  - Categorization must be deterministic: identical activity produces identical categories across sessions and versions
  - No free-text field exists anywhere in the telemetry schema
  - Category schema version is stamped on every record for backend compatibility
- **Edge Cases**: Action type introduced after taxonomy freeze, ambiguous operation belonging to two areas, feature area under refactor, failed operation with sensitive context, category schema mismatch with backend expectations, high-cardinality value attempting to sneak through extension fields
- **Error Handling**: Uncategorizable event dropped with internal counter rather than transmitted raw; validation error recorded through diagnostics logging only; schema version mismatch surfaces as configuration warning

### FR-TLM-003: Manage Analytics Sessions

Generate anonymous session ID. Persist session across restarts. Rotate session after timeout.

- **Description**: Maintain a random, unlinkable session identifier that survives restarts within a rotation window and severs linkage cleanly at rotation
- **Input**: Session lifecycle trigger: application start, rotation timeout, consent change, or explicit reset
- **Output**: Session state concept containing current session identifier, creation timestamp, rotation deadline, and consent record reference
- **Business Rules**:
  - Session identifier is generated from collision-resistant random source; it must never be derived from machine identifiers, user accounts, filesystem attributes, or hardware characteristics
  - Session state persists locally within allowed storage so restarts inside the rotation window continue the same session
  - Session rotates after configured timeout, producing a fresh identifier with no stored linkage to the previous one
  - Rotation discards the old identifier from local state; buffered records already carrying it may still transmit, but no future record references it
  - Session identifier must not correlate with diagnostics tracking identifiers or gateway request identifiers
  - Consent withdrawal deletes local session state entirely; re-opt-in starts from a fresh session
  - Corrupt or unreadable session state recovers as fresh session with warning, never as application failure
  - Session persistence must not store anything beyond identifier, timestamps, and consent record reference
  - No machine fingerprint of any kind may be constructed or transmitted
- **Edge Cases**: Corrupt session state file, missing session state, restart just inside rotation window, restart just outside rotation window, clock skew advancing or delaying rotation, consent withdrawal and re-opt-in within one run, concurrent access to session state, persistence location unwritable, rotation racing batch transmission
- **Error Handling**: Session state error recovered through fresh session generation; persistence failure degrades to in-memory session with warning; rotation failure falls back to immediate fresh session rather than reusing stale identifier

### FR-TLM-004: Enrich Events with Environment Metadata

Add OS, Python version, Blender version, app version. No identifying information.

- **Description**: Attach coarse, version-level environment context to outgoing batches so product decisions can be weighted by platform without identifying anyone
- **Input**: Environment probe results for operating system family, runtime version, Blender version, and application version
- **Output**: Environment metadata concept stamped onto batch envelope
- **Business Rules**:
  - Permitted fields are limited to:
    - operating system family
    - runtime major and minor version
    - Blender major and minor version
    - application version
    - telemetry schema version
    - consent record version
  - Versions are truncated to major and minor granularity; patch and build identifiers are excluded to limit fingerprint surface
  - Hostnames, usernames, paths, hardware identifiers, locale precision beyond coarse region-free defaults, and network addresses are forbidden
  - Environment snapshot is computed once per session and cached, not per event
  - Unavailable values become explicit unknown markers rather than free-text fallbacks
  - Environment changes during a session take effect at next rotation, preserving within-session consistency
  - Metadata schema is fixed per telemetry schema version; backend compatibility follows the same versioning as event categories
  - Environment probing must be lightweight and must never prompt, block, or require elevated permissions
- **Edge Cases**: Version detection unavailable, Blender not running when snapshot computed, operating system detection failure, runtime version changed mid-session by external update, environment probe slow under system load, schema version mismatch with backend, all optional fields unknown producing near-empty envelope
- **Error Handling**: Enrichment failure transmits batch with unknown markers rather than dropping events; probing error logged through diagnostics logging only; configuration error when metadata schema settings are invalid

## Hard Rules

- Telemetry must NOT be used for operational debugging — diagnostics feature owns debugging; telemetry records never feed back into error handling, health checks, or support flows
- Telemetry must NOT store PII — scrubbing happens at ingestion, not before transmission; no downstream component ever receives raw content
- Telemetry must NOT block main operations — recording, batching, and transmission are asynchronous; telemetry failure of any kind is invisible to product behavior
- Telemetry is opt-in only — disabled by default, silent until enabled, and withdrawal immediately stops collection and discards untransmitted records
- Telemetry must NOT identify machines or users — no fingerprinting, no persistent cross-session identity, no derived identifiers from system attributes
- Telemetry must remain separable — its buffers, storage, and stream never mix with logs, metrics, or audit records

## Error Categories

- configuration error — telemetry configuration invalid, such as malformed endpoint, invalid interval, or unknown schema version
- provider error — analytics backend unreachable or rejecting batches, always non-blocking
- transmission error — batch delivery failed after retries, resolved by bounded retry then discard with counter
- session state error — local session state corrupt or unreadable, recovered through fresh session
- validation error — event shape or category invalid, resolved through silent drop with internal counter

Every error category in this feature is non-blocking by definition. No telemetry error may ever propagate into a product operation result.

## Events

Telemetry's own lifecycle signals flow through the diagnostics logging policy, never through the telemetry pipeline itself, so the stream cannot observe its own internals.

- anonymous event recorded event — usage record buffered with category summary and consent state
- session created or rotated event — session lifecycle transition with rotation reason
- telemetry batch transmitted event — batch delivered with record count and schema version
- telemetry transmission failed event — batch discarded after retry exhaustion with provider error category
- consent changed event — opt-in or withdrawal applied with buffer action taken

Event payloads should include:

- event category
- record or batch counts
- schema and consent record versions
- error category when failed

Event payloads must avoid:

- any telemetry record content
- session identifiers in full form
- endpoint addresses beyond redacted host summary
- user or machine identifying information

## Configuration Keys


| Configuration Concept            | Description                                                  | Typical Default                       |
| ---------------------------------- | -------------------------------------------------------------- | --------------------------------------- |
| Opt-in toggle                    | Master consent switch for all collection and transmission    | Disabled                              |
| Analytics endpoint               | Backend destination for transmitted batches                  | Vendor-operated endpoint              |
| Session rotation interval        | How long a session identifier remains active before rotation | Bounded window measured in hours      |
| Background transmission interval | Frequency of batch delivery attempts                         | Periodic interval measured in minutes |
| Batch size cap                   | Maximum records per transmission batch                       | Conservative batch limit              |
| Local buffer cap                 | Maximum buffered records before drop-oldest backpressure     | Conservative buffer limit             |
| Environment metadata enabled     | Whether coarse environment fields are attached to batches    | Enabled when consent active           |
| Transmission retry bound         | Maximum delivery attempts per batch before discard           | Small retry count                     |

## QA Checklist

- [ ]  Events recorded without PII across every supported action type
- [ ]  Scrubbing applied at ingestion before buffering, not before transmission only
- [ ]  Raw payloads, object names, paths, prompts, and error messages never appear in records
- [ ]  Failed operations recorded as outcome category only, never as message
- [ ]  Opt-in consent respected: disabled telemetry produces zero records, zero buffers, zero transmissions
- [ ]  Consent withdrawal immediately stops recording and discards untransmitted buffer
- [ ]  Re-opt-in after withdrawal starts from fresh session with no linkage
- [ ]  Session ID generated from random source, not derived from machine or user attributes
- [ ]  Session ID persists across restarts within rotation window
- [ ]  Session ID rotates after timeout with no stored linkage to previous identifier
- [ ]  Session ID does not correlate with diagnostics tracking identifiers
- [ ]  Corrupt session state recovers as fresh session without application failure
- [ ]  Environment metadata contains only OS family, runtime, Blender, and application versions at major and minor granularity
- [ ]  No hostname, username, path, or hardware identifier in environment metadata
- [ ]  Unavailable environment values become explicit unknown markers
- [ ]  Environment snapshot computed once per session, not per event
- [ ]  Categorization deterministic and bounded in cardinality
- [ ]  Unknown action types resolve to other category rather than raw transmission
- [ ]  Recording never blocks the originating operation under any condition
- [ ]  Buffer backpressure drops oldest records with counter exposed through diagnostics logging
- [ ]  Backend unreachable degrades to bounded retry then discard, invisibly to product behavior
- [ ]  Telemetry buffers and storage remain separate from logs, metrics, and audit records
- [ ]  Telemetry data never consumed for operational debugging or error handling
- [ ]  Telemetry lifecycle signals flow through diagnostics logging, not the telemetry stream
- [ ]  Schema version stamped on every batch and validated against backend expectations
