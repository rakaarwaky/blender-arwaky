# ARWAKY LOOP TODO

Next concrete actions (filled by the loop):

- [X]  Run initial full test sweep to establish baseline.
- [X]  Audit each module FRD for unimplemented requirements.
- [X]  Replace first discovered dummy/stub with real tested code.
- [X]  Check structural compliance: one-FR-one-capability-one-protocol rules (asset + scene fixed)
- [X]  LINTER: Run lint-arwaky-cli scan — 1222 violations total; reduced to 126; fixed critical import/undefined-name bugs (F821 6->0, F811 2->0); remaining are ARG002(60)/B904(18)/ARG001(11)/SIM/N818/F841/B007/B008/E402
- [X]  SCOPE: Audit mcp orphan files — REMOVED 4 verified orphans (health/lifecycle/startup/tool_discovery); NOT in bootstrap chain (duplicate surface_* classes); mcp now COMPLIANT (3 caps ↔ 3 FRs)
- [X]  TELEMETRY: Rename agent_orchestrator.py → agent_telemetry_orchestrator.py (AES101 naming); add ITelemetryAggregate inheritance; replace primitives with taxonomy VOs
- [X]  SECURITY: Fix AES401/AES202 violations in shared/src/security/taxonomy_security_error.py + taxonomy_security_event.py — added ErrorCategory/FilePath/FileSize/MetadataMap types; replaced primitives with VOs
- [X]  CLEANUP: ruff --fix applied (173 auto-fixes); fixed all F401 unused imports; added missing __all__ exports to shared/src/__init__.py
- [ ]  SECURITY: Resolve AES401 in taxonomy_security_error.py line 120 (dict in details parameter — acceptable for flexible error metadata, may be deferred)
- [ ]  DEFERRED: cli lifecycle capability belongs to launcher per FRD (scope violation); wired into live cli composition root, removal risks breaking Bootstrap
