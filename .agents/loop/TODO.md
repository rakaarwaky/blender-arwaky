# ARWAKY LOOP TODO

## Deferred & Pending Actions

```
shared (taxonomy + contract) — foundation for all modules
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
  └── dispatcher (→ gateway, object, scene, render,        │
                     asset, job, security, diagnostics) ───┘
  └── cli (→ dispatcher, launcher, diagnostics,
               config, job, security)
  └── mcp (→ dispatcher, diagnostics, config, job,
               security)
```

---

## Readiness Indicators

> **Primary rule: 1 FR = 1 capabilities file** (for modules with a capabilities layer)
> CLI & MCP are surface-layer by design — indicator is **1 FR = N surface files**


| Indicator                          | Weight   | Notes                                |
| ------------------------------------ | ---------- | -------------------------------------- |
| FR coverage (1 FR = 1 cap/surface) | **High** | Gap = unimplemented FR               |
| Test count ≥ FR count             | **High** | Every FR must have at least one test |
| pyproject.toml present             | Medium   | Module is not packagable without it  |
| Shared domain complete             | Medium   | Taxonomy + Contract files exist      |

---

## Production Readiness Score (1–10)


| Module          | FR | Cap / Surface | Gap          | Tests | Score    | Notes                                                        |
| ----------------- | ---- | --------------- | -------------- | ------- | ---------- | -------------------------------------------------------------- |
| **config**      | 5  | 5 cap         | ✅ 0         | 11    | **8/10** | Full coverage, tests exceed FR count                         |
| **job**         | 5  | 5 cap         | ✅ 0         | 0     | **7/10** | Full 1:1 FR→cap refactor complete,**0 tests** remaining     |
| **telemetry**   | 4  | 4 cap         | ✅ 0         | 4     | **7/10** | Full coverage, 1 test/FR, minor shared naming inconsistency  |
| **asset**       | 5  | 5 cap         | ✅ 0         | 6     | **7/10** | Full coverage, good tests, no pyproject                      |
| **cli**         | 3  | 5 surface     | ✅ by design | 1     | **6/10** | Surface-layer by design, needs more test coverage            |
| **security**    | 5  | 5 cap         | ✅ 0         | 1     | **6/10** | Full coverage, severely undertested, no pyproject            |
| **launcher**    | 5  | 5 cap         | ✅ 0         | 1     | **6/10** | Full coverage, only 1 test, no pyproject                     |
| **gateway**     | 5  | 5 cap         | ✅ 0         | 2     | **6/10** | Full coverage, minimal tests, no pyproject                   |
| **object**      | 7  | 7 cap         | ✅ 0         | 1     | **6/10** | Full coverage, critically undertested                        |
| **dispatcher**  | 6  | 6 cap         | ✅ 0         | 4     | **6/10** | Full coverage, no pyproject                                  |
| **render**      | 4  | 3 cap         | 🔴 -1        | 3     | **5/10** | FR-RND-001 (screenshot) merged into executor, not standalone |
| **scene**       | 2  | 1 cap         | 🟡 -1        | 1     | **5/10** | 2 FRs in 1 capabilities — acceptable if FRs are simple      |
| **mcp**         | 3  | 10 surface    | ✅ by design | 0     | **4/10** | Surfaces complete,**0 tests**                                |
| **diagnostics** | 5  | 2 cap         | 🔴 -3        | 1     | **4/10** | FR-DIA-002,003,004,005 missing dedicated capabilities        |

---

## Recommended Work Priority (dependency + readiness)

```
1.  shared      → foundation, must be fully stable first
2.  config      → 8/10, most ready, consumed by everything
3.  security    → 6/10, consumed by almost every module
4.  job         → 7/10, 5-cap refactor done — add tests next
5.  gateway     → 6/10, consumed by all domain features
6.  launcher    → 6/10, consumed by diagnostics / cli / mcp
7.  diagnostics → 4/10, missing 3 capabilities, consumed widely
8.  telemetry   → 7/10, standalone — can run in parallel
9.  asset       → 7/10, consumed by render
10. object      → 6/10, consumed by scene + dispatcher
11. scene       → 5/10, consumed by dispatcher
12. render      → 5/10, consumed by dispatcher
13. dispatcher  → 6/10, gates all domain actions
14. cli         → 6/10, terminal entry point
15. mcp         → 4/10, AI entry point — needs tests urgently
```

---

## Critical Gaps (immediate action required)


| Priority | Module                           | Gap                                                        |
| ---------- | ---------------------------------- | ------------------------------------------------------------ |
| 🔴#1     | **job**                          | 5 capabilities done,**0 tests** — highest risk            |
| 🔴#2     | **mcp**                          | **0 tests**, no pyproject, primary AI entry point          |
| 🔴#3     | **diagnostics**                  | 3 capabilities missing (FR-DIA-002, 003, 004, 005)         |
| 🟡#4     | **render**                       | FR-RND-001 not standalone — needs dedicated capability    |
| 🟡#5     | **security / launcher / object** | Full cap coverage but critically undertested (1 test each) |

---
