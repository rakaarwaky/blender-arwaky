# ARWAKY LOOP ASSUMPTIONS 

## 🏗️ Architecture & Workflows


| Topic                         | Decision                                                                                                                                                                                                             |
| ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Concurrency & Commits         | Local changes verified against the combined working tree; no forced auto-commits.                                                                                                                                    |
| Scene Import (Resolved C63)   | taxonomyscenevo + protocol class names (ISceneInspectionProtocol/ISceneCleanupProtocol) resolve the import chain — 886 tests pass.                                                                                  |
| Render Executor API (C63)     | Separate executors per concern (RenderCameraConfigExecutor, RenderHdriConfigExecutor, RenderViewportCaptureExecutor, RenderSceneImageExecutor) → return frozen VOs. Canonical constants: taxonomyrenderconstant.py. |
| Gateway Orchestration         | GatewayOrchestrator MUST NOT inherit IBlenderServerAggregate — remains a synchronous feature orchestrator (FR-GWY-001..005).                                                                                        |
| CLI & MCP Agent               | Legacy agent layers removed (C25, 26, 28). Routing via surface* handlers + DI container (coreagent_orchestrator).                                                                                                    |
| Reconnect Hardening (C36, 54) | MaintenanceExecutor.attemptreconnect → ConnectionExecutor.establishconnection. Counter reconnectattempts resets to 0 at the start of each new session.                                                              |
| MCP Surface Routing (C60, 71) | ToolRegistryHandler.registertools() static method imports fixed. Routes to diagnostics.getsnapshot(), SkillDocumentationReader, orchestrator.discoveractions()/executeaction().                                      |
| MCP Test Naming (C60)         | Pytest requires test* prefix. unit/contract_ filenames are ignored by the collector.                                                                                                                                 |

## 📐 Taxonomy & Types


| Topic                       | Decision                                                                                              |
| ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| Host Type                   | NewType("Host", str) in common core VOs — prevents undefined type crashes (C4).                      |
| ConnectionError             | Single top-level re-export to avoid F811 collisions without renaming public APIs (C4).                |
| Job Status                  | JobStatusSnapshot = canonical read-model. Deprecated factories removed (C46).                         |
| Tar Extraction (FR-AST-003) | filter='data' guarded by sys.version_info >= (3, 12) — prevents TypeError on Python 3.10/3.11 (C11). |

## 🔒 Security & Redaction (FR-SEC-004)


| Topic                     | Decision                                                                                                                                |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Audit Metadata (C42)      | AuditEmitter.emitaudit → self-contained recursive redaction on targetmetadata & redacted_reason → prevents secret leaks in log sinks. |
| JSON Text Redaction (C43) | SensitiveRedactor uses quoted-key regex ("key": "value") — redacts JSON payloads without duplicating config module dictionary rules.   |

## 🔧 Linter: Behavior & False Positives


| Topic                        | Decision                                                                                                                                                   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Orphan Flags (AES501/AES504) | Orphan flags are UNRELIABLE — cross-module imports are missed. Deletion candidates MUST be verified via full-repo grep (C38, 39).                         |
| Barrel Re-exports (AES202)   | Barrel files intentionally aggregate protocol exports. DO NOT force dummy taxonomy imports → triggers AES203/AES204 (C48, 50).                            |
| Linter Bugs (C51, 53)        | AES305 (noqa missing reason on clean files) & AES302/AES403 on capabilitiesjobmonitor.py = linter bugs. Do NOT refactor clean code to satisfy these flags. |
| Signature Bypasses (AES304)  | type: ignore on protocol ABC signatures = intentional to accommodate type inheritance mismatches.                                                          |
| Targeted Scan (C60)          | lint-arwaky-cli scan  = authoritative for per-file AES304 counts. Full-repo scan breakdown can be unreliable for individual file attribution.              |

## Cycle 87

- **DiagnosticsOrchestrator design**: DiagnosticsOrchestrator delegates to the unified `DiagnosticsCapability` class (implements all 5 FR-DIA protocols) rather than requiring separate capability instances — matches existing pattern where single capability covers multiple FRs.
- **AES505 false positives**: All 7 AES505 violations confirmed as false positives — agents ARE correctly exported in __init__.py; linter reports at line:1:1 with empty entry_points config causing unconditional flags.
- **AES504 shared utility**: Remaining AES504 on `shared/src/gateway/utility/utility_config_loader.py` is a false positive — pure utility function, not an agent orchestrator.
