# ARWAKY LOOP TODO

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


| Module          | FR | Cap / Surface | Gap        | Tests | Score    | Status Notes                                      |
| ----------------- | ---- | --------------- | ------------ | ------- | ---------- | --------------------------------------------------- |
| **job**         | 5  | 5 cap         | ✅ 0       | 95    | **9/10** | 1:1 FR coverage + 95 comprehensive tests          |
| **config**      | 5  | 5 cap         | ✅ 0       | 11    | **8/10** | Full coverage; test count exceeds FRs             |
| **diagnostics** | 5  | 2 cap         | ✅ 0       | 106   | **8/10** | Full coverage via health composition + 106 tests  |
| **telemetry**   | 4  | 4 cap         | ✅ 0       | 4     | **7/10** | Full coverage; 1 test/FR                          |
| **asset**       | 5  | 5 cap         | ✅ 0       | 6     | **7/10** | Full coverage; pyproject added                    |
| **cli**         | 3  | 5 surface     | ✅ Surface | 1     | **6/10** | Surface-layer design; needs expanded test suite   |
| **security**    | 5  | 5 cap         | ✅ 0       | 1     | **6/10** | Full coverage; undertested                        |
| **launcher**    | 5  | 5 cap         | ✅ 0       | 1     | **6/10** | Full coverage; pyproject added; undertested       |
| **gateway**     | 5  | 5 cap         | ✅ 0       | 2     | **6/10** | Full coverage; pyproject added; socket leak fixed |
| **object**      | 7  | 7 cap         | ✅ 0       | 1     | **6/10** | Full coverage; undertested                        |
| **dispatcher**  | 6  | 6 cap         | ✅ 0       | 4     | **6/10** | Full coverage; pyproject added                    |
| **render**      | 4  | 3 cap         | 🔴 -1      | 3     | **5/10** | FR-RND-001 merged into executor                   |
| **scene**       | 2  | 1 cap         | 🟡 -1      | 1     | **5/10** | 2 FRs combined into 1 executor                    |
| **mcp**         | 3  | 10 surface    | ✅ Surface | 0     | **4/10** | Surfaces complete; pyproject added; 0 tests       |

## Recommended Execution Order

1. **shared** — Universal foundation.
2. **config** (8/10) — Consumed across all modules.
3. **job** (9/10) — Highest readiness with 95 unit tests.
4. **diagnostics** (8/10) — 106 tests across 4 suites.
5. **security** (6/10) — Core dependency for domain modules.
6. **gateway** (6/10) — Network transport foundation.
7. **launcher** (6/10) — Process host manager.
8. **telemetry** (7/10) — Observability pipeline.
9. **asset** (7/10) — Content provider integration.
10. **dispatcher** (6/10) — Action routing gateway.
11. **object** (6/10) — Blender entity management.
12. **scene** (5/10) — Scene graph operations.
13. **render** (5/10) — Rendering executor.
14. **cli** (6/10) — Terminal interface surface.
15. **mcp** (4/10) — AI surface interface (needs test suite).

## Critical Action Items


| Priority   | Module                           | Description & Gap                                                                                                                      |
| ------------ | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| 🔴**#1#1** | **mcp**                          | 0 tests across 10 surfaces; orchestrator routing mismatch in`list_commands`/`read_skill_context`; sync/async`execute_command`mismatch. |
| 🟡**#1#1** | **security / launcher / object** | Full capability coverage, but critically undertested (1 test file each).                                                               |
| 🟡**#2#2** | **render**                       | FR-RND-001 lacks dedicated standalone capability file.                                                                                 |

## Completed Cycles Summary

* **Cycle 60 — Diagnostics Test Coverage** : Added 100 tests across 4 suites covering health composition, metrics, audit emission, and logging policies (661 tests pass).
* **Cycle 59 — Job Test Coverage** : Built 95 tests across 4 suites covering task states, projections, cancellation, and capacity limits (558 tests pass).
* **Cycle 58 — Pyproject.toml Completion** : Added `pyproject.toml` to gateway, launcher, security, dispatcher, diagnostics, and mcp modules. Modernized asset test event loops.
* **Cycle 57 — Gateway Socket Leak Fix** : Resolved socket descriptor leak in `ConnectionExecutor.establish_connection` on handshake/auth failure paths (FR-GWY-001).
