# FRD — Scene Management Feature

## Purpose

Scene-level inspection and bulk cleanup policy. Owns scene-wide awareness, summary, preservation decisions, and cleanup reports. Technical deletion of individual objects delegated to object feature. Policy-oriented and report-oriented — not low-level object manipulation.

## Scope

- Inspect scene state
- Scene metadata summary
- Object summary by type and visibility
- Camera/light summary
- Active camera + active object awareness
- Render settings summary
- Collection summary
- Protected object awareness
- Bulk cleanup (preservation policy, dry-run preview, reporting)
- Deterministic filtering and ordering
- Event emission for inspection and cleanup

## Out of Scope

Single object CRUD (object feature), material/modifier detail (object), render execution (render), asset import (asset), queue management (gateway), task tracking (job), network transport (gateway), licensing compliance.

## Depends On

gateway (Blender command execution + connection), object (single-object deletion primitives + ref resolution), config (preservation policy, dry-run default, inspection limits, protection rules), shared (taxonomy, result envelope, error categories).

## Provides To

dispatcher, higher-level workflow/agent orchestration layers.

## Functional Requirements

### FR-SCN-001: Inspect Scene State

- **Description**: Retrieve structured summary of active scene
- **Input**: Inspection request (detail level, object filter, include hidden flag)
- **Output**: Scene inspection result (success, scene state summary)
- **Rules**: Read-only, idempotent. Summary: scene name/ID, total object count, count by type, visible count, hidden count (if requested), camera list, light list, active camera ref, active object ref, render settings (resolution, engine, frame range), unit system, collection summary, world/environment summary, protected object summary. Deterministic object ordering (by stable ref or name). Hidden objects excluded by default; included if explicitly requested. Large scenes → summarized detail level to avoid oversized response. Missing active camera/object → empty ref (not failure). Safe serialization (no cycles). Capability flags for supported operations.
- **Edge Cases**: Empty scene, no active object/camera, missing render engine info, large scene, hidden/linked/instanced/protected objects, stale refs, serialization limit, gateway not connected, timeout
- **Error Handling**: Connection error (gateway unavailable); timeout error; scene state error (unsafe to inspect); delegated gateway error

### FR-SCN-002: Cleanup Scene Objects

- **Description**: Remove objects based on preservation policy, cleanup filter, confirmation rules. Scene owns policy; object feature owns execution.
- **Input**: Cleanup request (mode, preservation list, object filter, dry-run flag, confirmation flag, child/dependent handling policy, protected object policy)
- **Output**: Cleanup report (success, removed/preserved/skipped counts + refs, dry-run indicator)
- **Rules**: Scene: policy resolution (candidate vs preserved), dry-run preview, confirmation requirement. Object: deletion execution (ref resolution, low-level deletion, constraints). Preservation may protect: cameras, lights, active camera, sole camera, marked protected objects, protected collection contents. Default policy from config when request omits. Dry-run: report without mutation. Report structure identical for dry-run and actual. Deterministic + repeatable for identical state + policy. Reports removed/preserved/skipped refs. Never removes world, render settings, or scene metadata. Child policy: delete hierarchy/detach/reject. Dependent policy: ignore/reject/remove direct. Linked/instanced handled carefully (no unintended shared data removal). Undo-aware when Blender supports. No undo + destructive → confirmation required. Partial failure reported clearly. Emits completion event.
- **Edge Cases**: Scene already empty, only camera/light/protected remaining, linked/instanced/multi-user objects, active camera, locked/protected/hidden objects, children, constraint targets, large scene, timeout, partial deletion failure, missing confirmation, dry-run with no removable objects
- **Error Handling**: Scene state error; protection error; validation error; confirmation error; delegated deletion error; timeout error; connection error

## Boundary: Scene vs Object

Scene: bulk ops, scene-wide inspection, preservation policy, cleanup filtering, dry-run, reporting, protected object policy decisions. Object: single-object technical ops, deletion execution, ref resolution, low-level constraints, hierarchy handling per scene policy, linked/instanced safety at execution level. Scene decides what should happen; object executes the technical deletion safely.

## Error Categories

- scene state error — invalid state for operation
- protection error — attempted delete of protected object without override
- validation error — invalid mode/policy/filter
- confirmation error — destructive without required confirmation
- delegated deletion error — object feature failed deletion
- timeout error — inspection/cleanup exceeded limit
- connection error — gateway/Blender unavailable

## Events

- scene inspection completed (state summary)
- scene cleanup completed (report)
- scene cleanup dry-run completed (preview report)
- scene cleanup failed (partial/full failure)

Payloads: operation type, success, summary counts, dry-run indicator, error category, correlation ID. Never: full object dumps (large scenes), sensitive data.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| default_preservation_list | Default protected categories | cameras + lights |
| default_dry_run_mode | Cleanup defaults to preview only | Disabled |
| include_hidden_in_inspection | Hidden objects in inspection by default | Disabled |
| max_inspection_detail_limit | Object detail cap to avoid oversized response | Safe limit |
| protected_object_policy | Active camera/sole camera/lights/protected | active camera protected |
| cleanup_confirmation_required | Destructive cleanup confirmation | Enabled if undo unavailable |
| child_handling_default | Behavior for orphaned children | detach or reject |
| dependent_handling_default | Behavior for dependents | reject or handle only when safe |
| cleanup_timeout | Max cleanup duration | Configured |

## QA Checklist

- [ ] Inspection returns: object/camera/light/render settings/active camera/collection summaries
- [ ] Handles empty scene + missing active camera gracefully
- [ ] Hidden objects excluded by default, included when requested
- [ ] Deterministic ordering; summarized detail for large scenes
- [ ] Cleanup uses preservation policy (cameras, lights, protected)
- [ ] Dry-run doesn't mutate scene; same report structure as actual
- [ ] Deletion delegated to object feature
- [ ] Report: removed/preserved/skipped counts + refs
- [ ] Linked/instanced objects handled without unintended shared data removal
- [ ] Children + dependents handled per configured policies
- [ ] Protected objects respected without override
- [ ] Missing confirmation → confirmation error
- [ ] Partial failure reported clearly
- [ ] No overlap: object (single ops), render (execution), asset (import), job (tracking)
