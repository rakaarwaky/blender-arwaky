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


| Indicator          | Weight     | Scoring Formula                                                                                        |
| -------------------- | ------------ | -------------------------------------------------------------------------------------------------------- |
| **FR Coverage**    | **High**   | Base 3.0; -0.5 per FR without matching cap/surf file                                                   |
| **Test Coverage**  | **High**   | Base 3.0; -0.5 per missing type (unit/integration/smoke/e2e/acceptance), -1.0 if test count < FR count |
| **pyproject.toml** | **Medium** | Base 1.0; -1.0 if module lacks pyproject.toml                                                          |
| **Shared Domain**  | **Medium** | Base 1.0; -0.5 per missing taxonomy/contract file for the module's domain                              |

### Scoring Methodology

```
Score = (FR_Coverage + Test_Coverage + PyProject + Shared_Domain) - Violations × 0.5
Clamped to [0, 10]
```

**Test type requirements by layer:**

- **Capabilities**: Must have `unit` (+ mandatory `integration`). Missing `integration` → -0.5, missing `smoke` → -0.5, missing `e2e` → -0.5, missing `acceptance` → -0.5.
- **Surfaces** (cli/mcp): `unit` only is acceptable. No deduction for missing integration/smoke/e2e/acceptance.
- **Agents**: `unit` + `smoke`. Missing `smoke` → -0.5.

**Violations penalty:** Each violation (-0.5), applied after base score calculation. Includes AES304 (bypass), AES402 (naming), AES502 (orphan), AES503/505/506 (unexported).

### Production Readiness Scores (1–10)


| Module          | FR | Cap/Surf | Gap | Tests (P/F) | Violations | Test Types         | Score      | Notes                                                                                         |
| ----------------- | ---- | ---------- | ----- | ------------- | ------------ | -------------------- | ------------ | ----------------------------------------------------------------------------------------------- |
| **job**         | 5  | 5 cap    | ✅0 | 95/0        | 7          | unit:4             | **6.5/10** | 1:1 FR coverage + 95 tests; missing integration/smoke/e2e/acceptance (-1.5)                   |
| **config**      | 5  | 5 cap    | ✅0 | 112/0       | 6          | unit:11            | **7/10**   | Full coverage; test count exceeds FRs; missing integration/smoke/e2e/acceptance (-1.5)        |
| **diagnostics** | 5  | 2 cap    | ✅0 | 106/0       | 2          | unit:4, smoke:1    | **9/10**   | Full coverage; missing integration/e2e/acceptance (-1.0)                                      |
| **telemetry**   | 4  | 4 cap    | ✅0 | 39/0        | 5          | unit:4             | **7.5/10** | Full coverage; missing integration/smoke/e2e/acceptance (-1.5)                                |
| **asset**       | 5  | 5 cap    | ✅0 | 78/0        | 9          | unit:6             | **5.5/10** | Full coverage + pyproject added; missing integration/smoke/e2e/acceptance (-1.5)              |
| **cli**         | 3  | 5 surf   | ✅S | 9/0         | 5          | unit:1             | **7.5/10** | Surface-layer design; unit only is acceptable for surfaces                                    |
| **security**    | 5  | 5 cap    | ✅0 | 238/0       | 6          | unit:6             | **7/10**   | Full coverage; missing integration/smoke/e2e/acceptance (-1.5)                                |
| **launcher**    | 5  | 5 cap    | ✅0 | 17/0        | 1          | unit:1             | **9.5/10** | Full coverage + pyproject added; missing integration/smoke/e2e/acceptance (-1.5)              |
| **gateway**     | 5  | 5 cap    | ✅0 | 27/0        | 1          | unit:2             | **9.5/10** | Full coverage + pyproject; socket leak fixed; missing integration/smoke/e2e/acceptance (-1.5) |
| **object**      | 7  | 7 cap    | ✅0 | 29/0        | 2          | unit:1             | **9/10**   | Full coverage; missing integration/smoke/e2e/acceptance (-1.5)                                |
| **dispatcher**  | 6  | 6 cap    | ✅0 | 59/0        | 0          | unit:4             | **10/10**  | Full coverage + pyproject added; missing integration/smoke/e2e/acceptance (-1.5)              |
| **render**      | 4  | 4 cap    | ✅0 | 36/0        | 5          | unit:3             | **7.5/10** | FR-RND-001..004 covered; missing integration/smoke/e2e/acceptance (-1.5)                      |
| **scene**       | 2  | 2 cap    | ✅0 | 28/0        | 3          | unit:1             | **8.5/10** | Both FRs tested; missing integration/smoke/e2e/acceptance (-1.5)                              |
| **mcp**         | 3  | 10 surf  | ✅S | 13/0        | 13         | contract:1, unit:1 | **3.5/10** | Surfaces complete; contract+unit is acceptable for surfaces                                   |

### Violations Summary


| Rule   | Description                             | Count | Modules Affected                                                                            |
| -------- | ----------------------------------------- | ------- | --------------------------------------------------------------------------------------------- |
| AES304 | Bypass comments                         | 53    | shared(44), asset(4), job(2), mcp(1), launcher(1), gateway(1)                               |
| AES402 | Contract naming (wrong suffix)          | 5     | shared/common, shared/telemetry(4)                                                          |
| AES502 | Contract orphan                         | 6     | common(2), gateway(1), mcp(2), object(1)                                                    |
| AES503 | Capabilities not exported in__init__.py | 33    | config(5), job(5), diagnostics(2), telemetry(4), security(5), render(4), scene(2), asset(5) |
| AES505 | Agent not exported in__init__.py        | 6     | config(1), telemetry(1), security(1), object(1), render(1), scene(1)                        |
| AES506 | Surface not exported in__init__.py      | 15    | cli(5), mcp(10)                                                                             |

**Total: 115 violations** (53 bypass + 5 naming + 6 orphan + 33 unexported caps + 6 unexported agents + 15 unexported surfaces)

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
15. **render** (7/10) — Fixed (Cycle 63): 36 tests pass; full suite 886 green.

## Critical Action Items


| Priority                                                               | Module                                         | Description & Gap                                                                                                                                                          |
| ------------------------------------------------------------------------ | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 🔴**#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1#1** | **All modules**                                | **AES503**: 33 capability files not exported in `__init__.py` (config, job, diagnostics, telemetry, security, render, scene, asset). Fix all module __init__.py exports.   |
| 🔴**#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2#2** | **cli / mcp**                                  | **AES506**: 15 surface files not exported in `__init__.py`. Add exports to cli/__init__.py and mcp/__init__.py.                                                            |
| 🟡**#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3#3** | **config, telemetry, security, render, scene** | **AES505**: 6 agent files not exported in `__init__.py`. Add agent exports.                                                                                                |
| 🟡**#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4#4** | **shared/common, shared/telemetry**            | **AES402**: 5 contract files with wrong suffix (should be _protocol): contract_command_catalog, contract_telemetry_recording/classification/session_management/enrichment. |
| 🟡**#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5#5** | **object**                                     | **AES502**: 1 orphan contract: `contract_object_operate_protocol.py` (0 implementation imports). Verify if deprecated.                                                     |
| 🟢**#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6#6** | **mcp**                                        | 13 tests across 2 files; 10 surfaces complete; verify orchestrator routing in`list_commands`/`read_skill_context`.                                                         |
