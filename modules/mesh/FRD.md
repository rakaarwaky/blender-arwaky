# FRD — Mesh Feature

## Purpose

Expose bounded mesh statistics, topology validation, edit-mode-independent cleanup, normals recalculation, and UV-layer basics through canonical dispatcher actions.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `get_mesh_statistics` | Read-only | Vertex, edge, polygon, UV-layer, and custom-normal summary |
| `validate_mesh` | Read-only | Loose vertices, degenerate faces, and non-manifold edge findings |
| `perform_mesh_edit_operation` | Mutation | One of `recalculate_normals`, `triangulate`, or `remove_doubles` |
| `ensure_mesh_uv_layer` | Mutation | Create or reuse one named UV layer |

## Invariants

Actions require an existing mesh object. Validation examples are bounded by 1000 records. Edit operations are an explicit allow-list and use Blender `bmesh` without requiring UI edit-mode context. UV layer names are limited to 64 characters. The feature does not accept arbitrary operators, Python code, or filesystem paths.

## Security and verification

All operations are local data-block mutations with deterministic limits. Unit tests cover allow-lists and orchestrator delegation; Blender smoke tests cover statistics, validation, UV creation, normals recalculation, and structured non-mesh errors.
