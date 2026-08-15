# End-to-End Delivery Checklist

**Scope:** Repository-wide mission execution on `develop`.

## Feature Matrix

| Module / FR IDs | Contract coverage | Verification evidence | Status |
|---|---|---|---|
| Config — `FR-CFG-001..006` | File → environment → defaults resolution, schema validation, immutable snapshot, workspace root, metadata, and redaction | Config unit/integration tests and mutation/redaction tests | Complete |
| Security — `FR-SEC-001..005` | Path validation, archive traversal protection, code validation, sensitive-value redaction, and audit emission | Security test suite covering path, archive, code, redaction, and audit boundaries | Complete |
| Launcher — `FR-LAU-001..005` | Executable discovery/registration, process lifecycle, runtime readiness, persistence, and stale/PID-reuse handling | Launcher feature, persistence, business-logic, and cross-process tests | Complete |
| Gateway — `FR-GWY-001..005` | TCP transport, heartbeat, reconnect/disconnect behavior, queueing, and safe code execution boundary | Gateway, maintenance, and addon TCP E2E checks | Complete |
| Dispatcher — `FR-DSP-001..006` | Canonical catalog, request validation, sync/background routing, normalized envelope, errors, and registration | Dispatcher catalog, validation, dispatch, and normalization tests | Complete |
| Object — `FR-OBJ-001..007` | Primitive creation, inspection, transforms, materials, modifiers, deletion, and asset placement | Object and addon TCP execution tests | Complete |
| Scene — `FR-SCN-001..002` | Scene inspection and policy-aware cleanup | Scene inspection and Blender TCP E2E checks | Complete |
| Render — `FR-RND-001..004` | Viewport capture, scene render, camera configuration, and HDRI/environment setup | Camera/HDRI/render tests and Blender TCP E2E checks | Complete |
| Asset — `FR-AST-001..005` | Provider search, metadata, download/cache, secure extraction, and Blender import | Provider adapter, download, extraction, import, and CLI routing tests | Complete |
| Job — `FR-JOB-001..005` | Task lifecycle, progress, cancellation, cleanup, capacity, and cross-process persistence | Job lifecycle, cancellation, capacity, monitor, and persistence tests | Complete |
| Diagnostics — `FR-DIA-001..005` | Health composition, metrics, audit, structured logs, and diagnostics snapshots | Diagnostics health, metrics, logging, audit, and smoke tests | Complete |
| CLI — `FR-CLI-001..003` | Dedicated subcommands, global flags, action routing, JSON/error output, destructive confirmation, and help/FRD parity | CLI unit, dispatch integration, help surface, and asset routing tests | Complete |
| MCP — `FR-MCP-001..003` | Canonical schema exposure, CLI-equivalent routing, deterministic catalog metadata, bounded responses, and recursive redaction | MCP contract, routing, schema, security, truncation, and tracking-ID tests | Complete |
| Telemetry — `FR-TLM-001..004` | Opt-in classification, enrichment, recording, session management, and transmission boundary | Telemetry classification, enrichment, recording, session, and boundary tests | Complete |

## Engineering and Delivery Matrix

| Area | Acceptance criteria | Verification | Status |
|---|---|---|---|
| Architecture | AES naming and dependency boundaries preserved | Ruff and repository architecture conventions | Complete |
| Static quality | No Ruff errors, format drift, syntax errors, whitespace errors, or high/medium security findings | Ruff lint/format, `compileall`, Bandit `-ll -ii`, and `git diff --check` | Complete |
| Automated tests | Full suite passes on supported Python 3.10–3.13 with coverage above threshold | `1029 passed`; explicit coverage run: `70.03%` against a 60% threshold | Complete |
| Integration coverage | Cross-feature CLI, MCP, Asset, and Launcher contracts are exercised | Dedicated integration job in `.github/workflows/ci.yml` | Complete |
| Build verification | Addon ZIP and Python wheel/sdist build and integrity checks | Local/CI package jobs | Complete |
| CI/CD | Push and PR gates run for `develop` and `main`; tagged release builds and publishes artifacts | `.github/workflows/ci.yml` and `release.yml` | Complete |
| Runtime hygiene | Generated launcher/registry state is not tracked or left by local CI | Cleanup trap and final artifact scan | Complete |
| Documentation | README, AGENT, TEST, CONTRIBUTING, scripts, PR template, and CHANGELOG use current paths/commands | Repository-wide stale-reference scan | Complete |

## Known Deliberate Boundaries

The real Blender TCP smoke test remains an environment-dependent verification because GitHub-hosted runners do not provide the project's configured Blender runtime by default. It is covered locally when Blender is available, while CI validates the deterministic addon, protocol, dispatcher, CLI, MCP, Asset, and Launcher contracts.

The repository retains `mypy.ini` as an advisory configuration for the current dynamic Python/Blender boundaries. The mandatory CI static gates are Ruff, syntax compilation, and the complete automated test suite; the release workflow no longer invokes the obsolete `src/`-only mypy command.
