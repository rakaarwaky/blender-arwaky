# ARWAKY LOOP TODO

Escalate A1 (missing shared contract/taxonomy layer) to the loop's cross-module remediation; once `modules.shared.src.cli.*` exists, implement S1 masking + F1–F4 render gaps and re-run full FRD verification. Meanwhile keep lint/tests green each cycle.

Deferred WARNING (FR-CFG-003 env-path-non-dir warning) needs warning-channel design before implementation; otherwise continue monitoring

## Next Tasks

- [ ] T1: Audit agent_orchestrator.py — currently uses protocol directly, should use aggregate contracts
- [ ] T2: Verify FR-RND-003/FR-RND-004 test coverage matches FRD QA checklist items (camera_config + hdri_config tests)
- [ ] T3: Run lint-arwaky-cli scan on modules/render and modules/shared/src/render for structural violations
- [ ] T4: Check orphan files in render module (contract_viewport_capture.py may be duplicate of protocol)
