# ARWAKY LOOP TODO

## Current Priorities

1. **Render tests broken** — 3 test files fail collection (wrong import paths: `capabilities_camera_config` → `capabilities_render_camera_config_executor`, same for hdri and operate executor). Fix imports, then add missing FR-RND-002/FR-RND-001 capability test.
2. **Security resolved**: `capabilities_code_validator.py` non-strict SyntaxError UnboundLocalError fixed (FR-SEC-003); security suite 238/238.
3. **Bulk remediation deferred** pending user decision: AES502 orphan deletion (58 contract orphans), AES304 surgical widening (431 bypass comments).

## Module Dependency Graph

```
shared (taxonomy + contract) — foundation
  └── config ──────────────────────────────────────────────┐
  └── security ────────────────────────────────────────────┤
  └── telemetry (→ config, security) ──────────────────────┤
  └── launcher (→ config, security, diagnostics) ──────────┤
  └── diagnostics (→ launcher, gateway, dispatcher,        ┤
                    job, security, config) ─────────────┐┤
  └── gateway (→ config, security, diagnostics) ──────────││
  └── job (→ config, diagnostics) ────────────────────────││
  └── asset (→ config, security, job, gateway) ────────────│
  └── object (→ gateway, config, security) ────────────────│
  └── scene (→ gateway, object, config, shared) ───────────│
  └── render (→ gateway, security, job, asset, config) ────│
  └── dispatcher (→ gateway, object, scene, render,         │
                    asset, job, security, diagnostics) ───┘
  └── cli (→ dispatcher, launcher, diagnostics, config, job, security)
  └── mcp (→ dispatcher, diagnostics, config, job, security)
```

## Readiness Evaluation

### Indicators

* **Rule** : 1 FR = 1 capability file (capability layer) / 1 FR = N surface files (surface layer).


| Indicator          | Weight     | Purpose                                          |
| -------------------- | ------------ | -------------------------------------------------- |
| **FR Coverage**    | **High**   | Verifies 1:1 FR mapping to capabilities/surfaces |
| **Test Coverage**  | **High**   | Assures test count ≥ FR count for all modules   |
| **pyproject.toml** | **Medium** | Ensures standalone packageability                |
| **Shared Domain**  | **Medium** | Complete taxonomy and contract definitions       |

### Production Readiness Scores (1–10)


| Module          | FR | Cap/Surf | Gap | Tests (P/F) | Score | Violations     | Status Notes                                      |
| ----------------- | ---- | -------- | --- | ----------- | ----- | -------------- | --------------------------------------------------- |
| **job**         | 5  | 5 cap    | ✅0  | 95/0        | **9/10** | Bypass:2       | 1:1 FR coverage + 95 comprehensive tests          |
| **config**      | 5  | 5 cap    | ✅0  | 112/0       | **8/10** | —              | Full coverage; test count exceeds FRs             |
| **diagnostics** | 5  | 2 cap    | ✅0  | 106/0       | **8/10** | —              | Full coverage via health composition + 106 tests  |
| **telemetry**   | 4  | 4 cap    | ✅0  | 39/0        | **7/10** | —              | Full coverage; 1 test/FR                          |
| **asset**       | 5  | 5 cap    | ✅0  | 78/0        | **9/10** | Bypass:4       | Full coverage + pyproject added                   |
| **cli**         | 3  | 5 surf   | ✅S  | 9/0         | **7/10** | —              | Surface-layer design; test coverage improving     |
| **security**    | 5  | 5 cap    | ✅0  | 238/0       | **9/10** | —              | Full coverage; 238 tests across 6 suites          |
| **launcher**    | 5  | 5 cap    | ✅0  | 17/0        | **7/10** | Bypass:1       | Full coverage + pyproject added                   |
| **gateway**     | 5  | 5 cap    | ✅0  | 27/0        | **8/10** | Bypass:1       | Full coverage + pyproject; socket leak fixed      |
| **object**      | 7  | 7 cap    | ✅0  | 29/0        | **8/10** | Orphan:1       | Full coverage; 29 tests                           |
| **dispatcher**  | 6  | 6 cap    | ✅0  | 59/0        | **8/10** | —              | Full coverage + pyproject added                   |
| **render**      | 4  | 4 cap    | ✅0  | 36/0        | **7/10** | —              | FR-RND-001..004 covered; 36 tests (Cycle 63)      |
| **scene**       | 2  | 2 cap    | ✅0  | 28/0        | **9/10** | —              | Both FRs tested; 28 tests across suites           |
| **mcp**         | 3  | 10 surf  | ✅S  | 13/0        | **6/10** | Bypass:1       | Surfaces complete + pyproject; 13 tests in 2 files|

### Violations Summary

| Type    | Rule  | Count | Modules Affected                                  |
|---------|-------|-------|---------------------------------------------------|
| Bypass  | AES304| 9     | asset(4), job(2), gateway(1), launcher(1), mcp(1) |
| Orphan  | AES502| 6     | common(2), gateway(1), mcp(2), object(1)          |

**Total: 15 violations** (9 bypass + 6 orphan)

## Recommended Execution Order

1. **shared** — Universal foundation.
2. **config** (8/10) — Consumed across all modules.
3. **job** (9/10) — Highest readiness with 95 unit tests.
4. **diagnostics** (8/10) — 111 tests across 5 suites.
5. **security** (9/10) — Core dependency for domain modules; 238 tests.
6. **gateway** (8/10) — Network transport foundation.
7. **launcher** (7/10) — Process host manager.
8. **telemetry** (7/10) — Observability pipeline.
9. **asset** (9/10) — Content provider integration; 78 tests.
10. **dispatcher** (8/10) — Action routing gateway; 59 tests.
11. **object** (8/10) — Blender entity management; 29 tests.
12. **scene** (9/10) — Scene graph operations; 28 tests.
13. **cli** (7/10) — Terminal interface surface; 9 tests.
14. **mcp** (6/10) — AI surface interface; 13 tests in 2 files.
15. **render** (7/10) — ✅ Fixed (Cycle 63): 36 tests pass; full suite 886 green.

## Critical Action Items


| Priority   | Module                           | Description & Gap                                                                                                                      |
| ------------ | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 🟡**#1#1** | **object**                       | 1 orphan contract: `contract_object_operate_protocol.py` (0 implementation imports). Verify if deprecated and remove.                  |
| 🟡**#2#2** | **mcp**                          | 13 tests across 2 files; 10 surfaces complete; verify orchestrator routing in `list_commands`/`read_skill_context`.                    |
| 🟢**#3#3** | **render**                       | RESOLVED (Cycle 63): 36 tests pass; full suite 886 green.                                                                            |
| 🟢**#4#4** | **launcher / object / security** | Fully tested now: launcher 17 tests, object 29 tests, security 238 tests. No longer critically undertested.                        |

## Completed Cycles Summary

* **Cycle 63 — TODO Audit & Render Aggregate Fix** : Updated readiness scores across all modules; fixed render aggregate docstring to document FR-RND-001 through FR-RND-004. Verified scene module import chain intact (false alarm resolved). Security suite confirmed at 238 tests. Added Tests(P/F) and Bypass/Orphan columns to readiness table. Found 6 contract orphans across shared: `contract_execute_action_protocol`, `contract_workflow_protocol` (common), `contract_gateway_aggregate` (gateway), `contract_discovery_protocol`, `contract_health_protocol` (mcp), `contract_object_operate_protocol` (object). Total bypass comments: 9 across job(2), launcher(1), gateway(1), mcp(1), asset(4).
* **Cycle 60 — Diagnostics Test Coverage** : Added 100 tests across 4 suites covering health composition, metrics, audit emission, and logging policies (661 tests pass).
* **Cycle 59 — Job Test Coverage** : Built 95 tests across 4 suites covering task states, projections, cancellation, and capacity limits (558 tests pass).
* **Cycle 58 — Pyproject.toml Completion** : Added `pyproject.toml` to gateway, launcher, security, dispatcher, diagnostics, and mcp modules. Modernized asset test event loops.
* **Cycle 57 — Gateway Socket Leak Fix** : Resolved socket descriptor leak in `ConnectionExecutor.establish_connection` on handshake/auth failure paths (FR-GWY-001).
