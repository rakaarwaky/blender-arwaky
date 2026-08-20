# FRD — Scene Management Feature

## System Overview
The Scene module owns scene-level inspection, bulk cleanup policy, preservation decisions, and reporting. It is policy-oriented and report-oriented, delegating the technical deletion of individual objects to the Object module.

## Functional Requirements

### FR-001: Scene Inspection and Hierarchy
- **Description**: Retrieve structured summary of active scene and inspect object hierarchies.
- **Input**: `detail_level`, `include_hidden`, `object_name`, `max_depth`.
- **Output**: `UnifiedEnvelope` with scene state summary or bounded tree nodes.
- **Business Rules**: Read-only, idempotent. Deterministic object ordering. Hidden objects excluded by default. Hierarchy depth bounded 1–64. Safe serialization (no cycles).
- **Edge Cases**: Empty scene; missing active camera; large scene; cyclic parent references.
- **Error Handling**: `connection_error` if Gateway unavailable; `scene_state_error` if unsafe to inspect.

### FR-002: Bulk Cleanup and History Navigation
- **Description**: Remove objects based on preservation policy and navigate Blender undo/redo history.
- **Input**: `mode`, `preservation_list`, `dry_run`, `confirmation`.
- **Output**: `UnifiedEnvelope` with cleanup report (removed/preserved/skipped) or history status.
- **Business Rules**: Scene owns policy resolution. Object feature executes deletions. Dry-run previews without mutation. Protected objects (cameras, lights) respected. Undo/redo reports `unavailable` in headless context.
- **Edge Cases**: Scene already empty; only protected objects remaining; missing confirmation; headless undo.
- **Error Handling**: `protection_error`; `confirmation_error`; `delegated_deletion_error`.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `get_scene_info` | None | `UnifiedEnvelope` | Full scene metadata summary |
| `list_scene_objects` | `include_hidden`, `object_type`, `limit` | `UnifiedEnvelope` | Bounded object listing |
| `get_object_hierarchy` | `object_name`, `max_depth` | `UnifiedEnvelope` | Parent-child tree |
| `cleanup_scene` | `mode`, `dry_run`, `confirm` | `UnifiedEnvelope` | Bulk policy-based deletion |
| `undo` | None | `UnifiedEnvelope` | Navigate history backward |
| `redo` | None | `UnifiedEnvelope` | Navigate history forward |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (connection), `object` (deletion execution), `config` (preservation policies), `shared` (taxonomy).

## Non-functional Requirements (Detailed)

- **Performance**: Large scenes summarized via `detail_level` to avoid oversized responses. Hierarchy bounded to depth 64.
- **Security**: Destructive cleanup requires explicit confirmation if undo is unavailable.
- **Scalability**: Dry-run operations prevent accidental mass deletion. Linked/instanced objects handled without unintended shared data removal.

## Test Scenarios / QA Checklist

- [ ] Verify `get_scene_info` handles empty scene and missing active camera gracefully.
- [ ] Verify `cleanup_scene` respects preservation list (cameras, lights).
- [ ] Verify `cleanup_scene` dry-run does not mutate the scene.
- [ ] Verify `undo`/`redo` explicitly reports `unavailable` in headless background context.
- [ ] Verify `list_scene_objects` reports truncation instead of silently implying completeness.

## Assumptions & Constraints

- Scene decides what should happen (policy); Object executes the technical deletion safely.
- Scene never removes world, render settings, or scene metadata.

## Glossary

- **Preservation Policy**: Rules defining which objects (e.g., active camera, lights) are protected from bulk cleanup.
- **Dry-Run**: A preview execution that calculates what would be deleted without actually mutating the scene.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `object`, `config`, `shared`, `dispatcher`
