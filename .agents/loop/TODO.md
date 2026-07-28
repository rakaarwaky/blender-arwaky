# ARWAKY LOOP TODO

Next concrete actions (filled by the loop):

- [X]  Run initial full test sweep to establish baseline.
- [X]  Audit each module FRD for unimplemented requirements.
- [X]  Replace first discovered dummy/stub with real tested code.
- [X]  Check structural compliance: one-FR-one-capability-one-protocol rules (asset + scene fixed)
- [X]  LINTER: Run lint-arwaky-cli scan — 1222 violations total; reduced to 38; fixed critical import/undefined-name bugs (F821 6->0, F811 2->0); remaining are ARG002(60)/B904(18)/AES202(38)/SIM/N818
- [X]  SCOPE: Audit mcp orphan files — REMOVED 4 verified orphans (health/lifecycle/startup/tool_discovery); NOT in bootstrap chain (duplicate surface_* classes); mcp now COMPLIANT (3 caps ↔ 3 FRs)
- [X]  TELEMETRY: Rename agent_orchestrator.py → agent_telemetry_orchestrator.py (AES101 naming); add ITelemetryAggregate inheritance; replace primitives with taxonomy VOs
- [X]  SECURITY: Fix AES401/AES202 violations in shared/src/security/taxonomy_security_error.py + taxonomy_security_event.py — added ErrorCategory/FilePath/FileSize/MetadataMap types; replaced primitives with VOs
- [X]  CLEANUP: ruff --fix applied (173 auto-fixes); fixed all F401 unused imports; added missing __all__ exports to shared/src/__init__.py
- [X]  ORCHESTRATOR: Add aggregate inheritance to scene/render orchestrators — fixed AES202 violations in scene/render modules (48→44 remaining)
- [X]  TAXONOMY ERROR: Fix AES202/AES401 in job/gateway/launcher error files — added ErrorString/ErrorMessage imports; replaced str with branded types
- [ ]  AES202: Fix remaining mandatory import violations in CLI/diagnostics capabilities and protocol files; GatewayOrchestrator's IBlenderServerAggregate base was reverted (wrong async server aggregate) — needs a proper gateway aggregate or server-aggregate wiring at the root/mcp entry orchestrator
- [ ]  SECURITY: Resolve AES401 in taxonomy_security_error.py line 120 (dict in details parameter — acceptable for flexible error metadata, may be deferred)
- [ ]  DEFERRED: cli lifecycle capability belongs to launcher per FRD (scope violation); wired into live cli composition root, removal risks breaking Bootstrap
- [X]  TAR FIX (cycle 11): version-guarded `filter='data'` on tar extraction in capabilities_asset_extract.py (FR-AST-003); +1 regression test guarding the DeprecationWarning; 341 tests pass (0 regressions)
