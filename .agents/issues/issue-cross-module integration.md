## Integration Issues: Dispatcher ↔ Launcher (via Gateway)

These are the **cross-module integration gaps** where the Dispatcher→Gateway→Launcher chain breaks or behaves incorrectly.

---

### 🔴 CRITICAL Integration Failures

| # | Issue | Where It Breaks | Impact |
|---|-------|----------------|--------|
| 1 | **`SyncDispatchExecutor` not wired in container** | `root_dispatcher_container.py` never instantiates it | Dispatcher's `dispatch_sync()` always raises `RuntimeError`. **No action can ever reach Gateway.** The entire Dispatcher→Gateway→Blender pipeline is dead. |
| 2 | **Launcher spawns Blender without bridge addon** | `utility_process_ops.py:process_spawn()` only passes `--background` for headless | Blender starts but has **no MCP bridge active**. Gateway connects to a port with nothing listening. Every dispatched action gets `connection_error`. |
| 3 | **`bridge_probe=None` in Launcher container** | `root_launcher_container.py` line 52 | Gateway asks Launcher "is Blender ready?" → Launcher checks only PID liveness → reports `ready=True` even when bridge is dead. Gateway sends commands into a void. |

**Combined effect:** Even if you fix #1, actions fail at #2. Even if you fix #1 and #2, Gateway gets false readiness from #3. All three must be fixed together for the pipeline to work end-to-end.

---

### 🟡 WARNING Integration Gaps

| # | Issue | Modules Involved | Impact |
|---|-------|-----------------|--------|
| 4 | **No post-launch state persistence** | Launcher → Gateway | After `launch()` succeeds, Launcher never calls `persist()`. Gateway's next liveness check reads stale persisted state (old PID or `NOT_RUNNING`), potentially rejecting valid dispatch. |
| 5 | **No post-shutdown state update** | Launcher → Gateway | After `shutdown()` succeeds, persisted state still shows old PID as running. Gateway may attempt to send commands to a dead process. |
| 6 | **Version compatibility is a no-op** | Launcher → Dispatcher | `_check_compatibility()` always returns `SUPPORTED`. If an incompatible Blender version is launched, Dispatcher routes actions that silently fail with cryptic Blender errors instead of a clear `unsupported_error`. |
| 7 | **Neither module emits structured events** | Dispatcher + Launcher → Diagnostics | FRD specifies 6 dispatcher events + 7 launcher events. Zero are emitted (only `logger.*` calls). Diagnostics health composition has no data source from either module. |
| 8 | **Config feature not integrated** | Config → Dispatcher + Launcher | Both containers hardcode defaults (`LauncherConfigVO()`, `DispatcherContainer()`). User-configured timeouts, paths, capacity limits, and policies are silently ignored. |
| 9 | **`execute_action()` overrides caller's execution mode** | Dispatcher (internal) → Gateway/Job | Caller explicitly requests `sync`, but orchestrator checks `background_eligibility_flag` and silently routes to background. Gateway never receives the action; Job creates an orphan task. |
| 10 | **No launch-in-progress guard** | Launcher (internal) | If `shutdown()` is called while `launch()` is waiting for readiness, both race on the same PID. Shutdown may kill a process that launch is still probing, causing launch to report false failure. |

---

### Integration Flow: What Should Happen vs. What Actually Happens

```
EXPECTED (per FRD):
  CLI → Dispatcher.validate() → Dispatcher.dispatch_sync()
    → Gateway.execute()
      → Gateway asks Launcher: "Blender alive + bridge ready?"
        → Launcher: PID alive ✓ + TCP bridge connect ✓ → "READY"
      → Gateway sends command via socket → Blender executes
    → Dispatcher.normalize() → envelope → CLI

ACTUAL (current code):
  CLI → Dispatcher.validate() → Dispatcher.dispatch_sync()
    → RuntimeError("SyncDispatchProtocol not configured")  ← #1: not wired
    → (even if wired) Gateway.execute()
      → Gateway asks Launcher: "Blender alive?"
        → Launcher: PID alive ✓ + bridge_probe=None → "READY"  ← #3: no bridge check
      → Gateway sends command via socket → CONNECTION REFUSED  ← #2: no addon
    → Dispatcher maps to "connection_error" → envelope → CLI
```

---

### Minimum Fix Sequence (for Developer)

```
Step 1: Wire SyncDispatchExecutor in DispatcherContainer     [fixes #1]
Step 2: Extend process_spawn() to pass bridge config/addon   [fixes #2]
Step 3: Wire real bridge_probe (TCP connect) in Launcher     [fixes #3]
Step 4: Add post-launch + post-shutdown persist() calls      [fixes #4, #5]
Step 5: Wire event sink into both modules                    [fixes #7]
Step 6: Integrate Config feature for both containers         [fixes #8]
```

Steps 1–3 are **blocking** — nothing works without them. Steps 4–6 are **correctness** — the system runs but produces wrong state and silent failures.