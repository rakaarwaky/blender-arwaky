# ARWAKY LOOP TODO

### Violations Summary


| Rule   | Description                      | Count | Modules Affected                                                                                                                                  |
| -------- | ---------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| AES304 | Bypass comments                  | 367   | shared(280), asset(28), job(19), mcp(15), launcher(12), gateway(8), object(7), telemetry(4)                                                       |
| AES502 | Contract orphan                  | 54    | common(2), gateway(1), mcp(2), object(1), asset(6), job(5), security(5), render(4), scene(3), config(3), launcher(5), telemetry(6), dispatcher(6) |
| AES401 | Mandatory import                 | 26    | shared(10), mcp(4), job(3), asset(3), gateway(2), render(2), object(1)                                                                            |
| AES402 | Contract naming (wrong suffix)   | 21    | shared/common, shared/telemetry(4)                                                                                                                |
| AES203 | Forbidden import (lower layer)   | 18    | shared(6), mcp(4), asset(3), gateway(2), job(2), render(1), object(1), config(1)                                                                  |
| AES204 | Forbidden import (agent layer)   | 16    | shared(5), mcp(3), gateway(2), job(2), asset(2), render(1), object(1), config(1), telemetry(1)                                                    |
| AES202 | Mandatory import from barrel     | 15    | shared(6), mcp(3), job(2), asset(2), gateway(1), render(1), object(1)                                                                             |
| AES102 | Missing docstring                | 15    | shared(4), mcp(2), job(2), asset(2), gateway(1), render(1), object(1), config(1), telemetry(1)                                                    |
| AES504 | Agent not in__init__.py          | 12    | config(1), job(1), diagnostics(1), telemetry(1), security(1), render(1), scene(1), asset(1), launcher(1), gateway(1), dispatcher(1), mcp(1)       |
| AES505 | Agent not exported in__init__.py | 7     | config(1), telemetry(1), security(1), object(1), render(1), scene(1), launcher(1)                                                                 |
| AES305 | Missing noqa on bypass           | 7     | shared(3), mcp(1), job(1), asset(1), gateway(1)                                                                                                   |
| AES101 | Missing docstring (class)        | 6     | shared(2), mcp(1), job(1), asset(1), gateway(1)                                                                                                   |
| AES501 | Contract not in__init__.py       | 5     | config(1), job(1), telemetry(1), security(1), render(1)                                                                                           |
| AES403 | Surface not in contract          | 1     | mcp                                                                                                                                               |
| AES405 | Missing surface docstring        | 1     | mcp                                                                                                                                               |

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
