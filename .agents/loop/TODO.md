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
| AES504 | Agent not in__init__.py          | 1     | shared/src/gateway/utility/utility_config_loader.py (false positive — utility file, not agent)                     |
| AES505 | Agent not exported in__init__.py | 7     | config(1), telemetry(1), security(1), object(1), render(1), scene(1), launcher(1)                                                                 |
| AES305 | Missing noqa on bypass           | 7     | shared(3), mcp(1), job(1), asset(1), gateway(1)                                                                                                   |
| AES101 | Missing docstring (class)        | 0     | All class docstrings added (Cycle 89)                                                                                                           |
| AES501 | Contract not in__init__.py       | 5     | config(1), job(1), telemetry(1), security(1), render(1)                                                                                           |
| AES403 | Surface not in contract          | 1     | mcp                                                                                                                                               |
| AES405 | Missing surface docstring        | 1     | mcp                                                                                                                                               |

## Recommended Execution Order

1. **shared**
2. **config** (8/10)
3. **job** (9/10)
4. **diagnostics** (9.5/10) — DiagnosticsOrchestrator added (FR-DIA-001..005); gap closed; missing integration/e2e (-1.0)
5. **security** (9/10)
6. **gateway** (8/10)
7. **launcher** (7/10)
8. **telemetry** (7/10)
9. **asset** (9/10)
10. **dispatcher** (8/10)
11. **object** (8/10)
12. **scene** (9/10)
13. **cli** (7/10)
14. **mcp** (6/10)
15. **render** (7/10)
