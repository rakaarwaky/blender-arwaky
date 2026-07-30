# Integration Issues: Security ↔ Launcher

Yes — there are **significant integration gaps** between the two modules. The PRD data flow diagram explicitly draws the arrow `Security -->|path validation| Launcher`, and the Launcher FRD lists `security policy (safe auth material handling)` under "Depends On." However, **the code has zero cross-module wiring**. Here is the full breakdown:

---

## 1. 🔴 Path Validation Is Never Delegated

**PRD says:** `Security -->|path validation| Launcher`
**Launcher FRD says:** Depends on `security policy (safe auth material handling)`
**Code does:** Nothing.

`ExecutableLocator._validate()` uses raw `os.path` calls:

```python
# capabilities_executable_locator.py — lines 82-95
canonical = os.path.realpath(path)
if not os.path.isfile(canonical) or not os.access(canonical, os.X_OK):
    raise ExecutableValidationError(...)
```

It never calls `SecurityOrchestrator.validate_path()` or injects `ValidatePathProtocol`. This means:

| Security check (FR-SEC-001) | Applied to launcher executable path? |
|---|---|
| Traversal rejection (`..`) | ❌ No |
| Symlink escape prevention | ❌ No (uses `realpath` but no allowed-dir check after) |
| Allowed-directory enforcement | ❌ No |
| Audit event on denial | ❌ No |
| Redacted path in diagnostics | ❌ No — full path in events |

The same gap exists in `StatePersistence` — the persistence file path is never validated through security.

---

## 2. 🔴 Launcher Container Does Not Inject Security

`root_launcher_container.py` wires 5 capabilities but has **no reference** to `SecurityContainer`, `ISecurityOperateAggregate`, or any security protocol:

```python
# root_launcher_container.py — wire()
persist_cap = StatePersistence(...)
status_cap = RuntimeStatusChecker(...)
locate_cap = ExecutableLocator(...)
launch_cap = ProcessLauncher(...)
shutdown_cap = ProcessShutdown(...)
# ← No security capability injected anywhere
```

Compare with what the PRD requires: the launcher should receive a `ValidatePathProtocol` (for executable + persistence path validation) and a `RedactSensitiveProtocol` (for state persistence secret handling).

---

## 3. 🟡 Secret Detection Is Duplicated and Weaker

`StatePersistence` has its own naive secret check:

```python
# capabilities_state_persistence.py
_SECRET_KEYS = ("secret", "token", "password", "credential", "auth")


def _contains_secret(self, state: RuntimeStateVO) -> bool:
    data = self._to_dict(state)
    for key in _SECRET_KEYS:
        if key in data:
            return True
    return False
```

The security module's `utility_security_redactor.py` has **far more comprehensive** detection:

```python
# utility_security_redactor.py
REDACTION_SENSITIVE_PATTERNS = (
    r"(?i)(password|passwd|secret|token|api[_-]?key|...)\s*[:=]\s*...",
    r"(?i)(bearer|basic)\s+[A-Za-z0-9\-._~+/]+=*",
    r"(?i)sk-[A-Za-z0-9]{20,}",  # OpenAI keys
    r"(?i)ghp_[A-Za-z0-9]{36}",  # GitHub tokens
    r"(?i)AKIA[0-9A-Z]{16}",  # AWS keys
)
```

This is both an **AES305 duplication violation** and a **security gap** — the launcher's version misses bearer tokens, AWS keys, GitHub tokens, and pattern-based secrets entirely.

---

## 4. 🟡 No Security Audit Events From Launcher

The security FRD (FR-SEC-005) requires: *"Every security violation produces audit event."*

The launcher emits its own `LauncherLifecycleEvent` but **never** emits `SecurityAuditEventVO`. Scenarios that should produce security audit events but don't:

| Scenario | Security audit event emitted? |
|---|---|
| Executable path outside allowed directories | ❌ |
| Symlinked executable pointing outside allowed dirs | ❌ |
| State persistence path in sensitive location | ❌ |
| Secret-like field detected in runtime state | ❌ |
| Non-Blender executable rejected (validation failure) | ❌ |

---

## 5. 🟡 Full Paths Leaked in Launcher Events

`LauncherLifecycleEvent.process_reference` carries the **full executable path**:

```python
# capabilities_executable_locator.py
self._emit_registered(source, path)  # path = "/home/user/.local/share/blender/blender"
```

The security FRD (FR-SEC-001) says: *"Result never exposes sensitive path details beyond redacted diagnostic info."* The security module even provides `_redact_path()` for this purpose, but the launcher never uses it.

---

## 6. 🟡 Bridge Endpoint / Auth Material Unprotected

FR-LAU-002 explicitly states:
> *"Auth material through security policy, never logged"*
> *"Passes bridge endpoint settings + protocol info"*

The launcher code has **no integration** with the security module for:
- Redacting bridge endpoint credentials from logs/events
- Validating that bridge endpoint settings don't contain secrets
- Protecting auth material passed to the Blender process

The `LaunchOutcomeVO.bridge_endpoint` field is a raw `str | None` — no redaction applied.

---

## 7. 🟢 No Shared Cross-Module Contract

There is no contract defining how launcher consumes security services. The launcher's 5 protocols (`LaunchProtocol`, `LocateRegisterProtocol`, etc.) have no security-related parameters. A proper integration would require either:

- **(a)** Injecting `ValidatePathProtocol` + `RedactSensitiveProtocol` into launcher capabilities via the container, or
- **(b)** Having the launcher orchestrator call `ISecurityOperateAggregate.validate_path()` before delegating to `ExecutableLocator`

Neither exists.

---

## Summary Table

| # | Severity | Gap | FRD Reference |
|---|---|---|---|
| 1 | 🔴 | Executable path never validated through security | PRD diagram + FR-LAU-001 + FR-SEC-001 |
| 2 | 🔴 | Launcher container has no security DI wiring | PRD diagram + FR-LAU "Depends On" |
| 3 | 🟡 | Secret detection duplicated & weaker than security module | FR-LAU-005 + FR-SEC-004 + AES305 |
| 4 | 🟡 | No security audit events from launcher operations | FR-SEC-005 |
| 5 | 🟡 | Full paths in launcher events (not redacted) | FR-SEC-001 |
| 6 | 🟡 | Bridge endpoint / auth material unprotected | FR-LAU-002 |
| 7 | 🟢 | No cross-module contract for security consumption | Architecture gap |

**Bottom line:** The PRD and both FRDs declare a dependency, but the implementation treats the two modules as completely isolated. The launcher performs its own ad-hoc path checks and secret detection instead of delegating to the security module as the architecture requires.