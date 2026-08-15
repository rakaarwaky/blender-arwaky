# Evidence Ledger — Plan Revalidation

## Purpose

This ledger records the evidence used to revise the 2026-08-08 business-analyst plans. It is a documentation artifact only. No production code was changed or executed during this revalidation.

## Confirmed Current Behavior

| Area | Evidence | Decision |
|---|---|---|
| Job atomicity | `modules/job/src/capabilities_job_repository.py` owns an `RLock` and uses it around create, update, transition, read, list, and delete operations. | Close the old speculative atomicity finding; retain concurrency as a regression criterion. |
| Job task creation | `modules/job/src/agent_job_orchestrator.py` creates the lifecycle record synchronously after capacity evaluation. | Close the old “task ID may not be ready” finding. |
| Job stale recovery | The orchestrator collects stale running task IDs, applies timeout transitions, and purges records. | Close the old implementation-gap question; keep a stale-recovery test backlog item. |
| Object wiring | `modules/object/src/root_object_container.py` wires seven executors, constructs `ObjectOrchestrator`, and exposes the aggregate. | Close the old AES505 “not wired” finding. |
| Object taxonomy ownership | Current object VOs are under `modules/shared/src/object/taxonomy_object_vo.py`; the old `modules/object/src/taxonomy_object_vo.py` path is absent. | Mark the old location-specific AES401 finding obsolete, not executable. |
| Render output security | `modules/render/src/capabilities_render_scene_image_executor.py` calls `ValidatePathProtocol` before executing render code. | Close the old security-validation uncertainty. |
| Render overwrite policy | The executor validates that a policy value is allowed, but `build_scene_render_code()` does not apply overwrite/reject/unique behavior. | Keep overwrite behavior open and require acceptance tests. |
| Render background jobs | `RenderOrchestrator` has no job lifecycle/submit dependency, and the scene executor only checks capacity; returned `task_ref` remains `None`. | Keep background-render job integration open. |
| HDRI delegation | `RenderHdriConfigExecutor` validates a local path and executes Blender image loading; it does not itself download through Asset. | Keep the exact Asset delegation contract as needs-clarification until the FRD/API boundary is confirmed. |
| Security validation order | `modules/gateway/src/capabilities_code_execution.py` validates code through the injected security protocol before transport execution. | Close the old validation-order uncertainty. |
| Security AST analysis | `modules/security/src/capabilities_code_validator.py` uses `ast.parse`, walks AST nodes, and derives blocked modules/functions from `SecurityPolicyVO`. | Close the old AST and configurability uncertainties. |
| Telemetry metadata/transmission | `modules/telemetry/src/capabilities_telemetry_recorder.py` stamps records with `VersionString("unknown")` and only appends to a bounded buffer; no backend transmission step is present. | Keep schema/version and transmission findings open. |
| Shared contract stubs | `modules/shared/src/common/contract_workflow_protocol.py`, `contract_command_catalog_protocol.py`, and `contract_execute_action_protocol.py` still contain abstract methods with `pass`. | Keep the shared contract-stub finding open. |

## Status Rules

A finding marked `open` has a concrete implementation or acceptance gap supported by current evidence. A finding marked `needs-clarification` is intentionally not an implementation instruction: its exact requirement, API boundary, or current file mapping must be confirmed first. A finding marked `resolved` is a regression criterion, not a request to change code. A finding marked `obsolete` must not be executed because its path or assumption was superseded.

## Execution Order

The revised plans are the only safe execution source. First resolve all `needs-clarification` rows with focused source/test checks. Then implement confirmed `open` rows in risk order: Security and Gateway, Job and Render reliability, shared contract completeness, Telemetry delivery, and finally lower-risk test/documentation improvements. Do not execute historical 2026-08-08 plans directly.

## References

- [`ARCHITECTURE.md`](../ARCHITECTURE.md)
- [`PRD.md`](../PRD.md)
- [`RULES_AES.md`](../.agents/rules/RULES_AES.md)
- [`PLAN_REVALIDATION_ALL_FEATURE_MODULES_20260814.md`](PLAN_REVALIDATION_ALL_FEATURE_MODULES_20260814.md)
- [`Revalidated plans`](../.agents/plans/)
