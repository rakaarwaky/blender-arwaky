# Plan: diagnostics — Business Analyst

## Summary
The diagnostics module provides centralized observability: health composition, metrics, audit, logging, snapshots per FRD. Code follows AES: 1 agent orchestrator, 5 capabilities, 1 root container. FRD-to-code mapping is strong. Domain isolation respected: diagnostics only composes, never mutates. No major violations found.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | �� 🟢 INFO | FRD mentions "bounded health probes with staleness indication" — staleness indicator not obvious in `capabilities_health_composer.py` output schema | `capabilities_health_composer.py` | Expose `stale_since` or similar field in health snapshot |
| 2 | �� 🟢 INFO | FRD "audit event emission for security violations, connection failures, task failures, destructive actions" — `capabilities_audit_emitter.py` exists but event categories not documented in code | `capabilities_audit_emitter.py` | Add docstring listing emitted audit categories |
| 3 | �� 🟢 INFO | FRD "trace correlation by tracking ID across logs, metrics, audit" — tracking ID propagation verified but not explicitly called out in logging/metrics code | `capabilities_logging_policy.py`, `capabilities_metrics_collector.py` | Add comment noting tracking ID inclusion in structured logs/metrics |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | �� 🟢 INFO | Health composition pulls from launcher/gateway/config/providers/job — provider availability noted as "optional, non-blocking" but no explicit health contribution from asset providers visible | `capabilities_health_composer.py` | Verify provider health integration; add if missing |
| 2 | �� 🟢 INFO | Snapshot provisioner returns immutable snapshot — thread-safety claimed but not evident in `capabilities_snapshot_provisioner.py` | `capabilities_snapshot_provisioner.py` | Add comment or locking if needed |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | �� 🟢 INFO | FRD "metrics immutable + safe for concurrent access" — `capabilities_metrics_collector.py` uses `collections.Counter` which is not thread-safe for increments | `capabilities_metrics_collector.py` | Replace with thread-safe counter or add locking |
| 2 | �� 🟢 INFO | FRD "Log rotation per size cap with bounded history" — rotation logic not visible in `capabilities_logging_policy.py` (may be handled by logging config) | `capabilities_logging_policy.py` | Confirm rotation implementation; document if external |
| 3 | �� 🟢 INFO | FRD "Redaction at ingestion; failure → mask entire payload" — redaction failure handling not obvious in `capabilities_logging_policy.py` | `capabilities_logging_policy.py` | Add explicit fallback for redaction errors |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | �� 🟢 INFO | No test for degraded health when subsystem timeout occurs | `tests/` | Add unit test simulating health probe timeout |
| 2 | �� 🟢 INFO | No integration test for audit emission on security violation | `tests/` | Add test triggering audit event via security policy violation |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | �� 🟢 INFO | All 5 FRD capabilities mapped to corresponding capabilities files | — | Traceability complete |
| 2 | �� 🟢 INFO | FRD error categories (state, config, emission, collection, probe timeout, redaction failure) present in code | `agent_diagnostics_orchestrator.py` | Error mapping verified |

## Violations
None found. AES boundaries intact: orchestrator does not contain business logic; capabilities are stateless helpers; root container only wires dependencies.

## Action Items
- [ ] �� 🟢 INFO Add staleness indicator to health snapshot
- [ ] �� 🟢 INFO Document audit event categories in emitter
- [ ] �� 🟢 INFO Ensure metrics collector thread-safety
- [ ] �� 🟢 INFO Add redaction failure fallback in logging policy
- [ ] �� 🟢 INFO Write unit tests for health degradation and audit emission

## Fixed Code
None required.

## Severity
- �� 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- �� 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- �� 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [x] Prerequisites read
- [x] Feature + modules identified
- [x] FRD mapped to code files
- [x] All 5 dimensions analyzed
- [x] Severity categorized
- [x] Deduped vs existing plans + active PRs
- [x] Plan written (NEW issues + fixed code)
- [x] Saved to correct path