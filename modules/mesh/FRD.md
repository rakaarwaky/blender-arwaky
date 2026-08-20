# FRD — Mesh Feature

## System Overview
The Mesh module exposes bounded mesh statistics, topology validation, edit-mode-independent cleanup, normals recalculation, and UV-layer basics. It allows pipeline tools to inspect and sanitize geometry without requiring UI edit-mode context.

## Functional Requirements

### FR-001: Mesh Inspection and Validation
- **Description**: Retrieve vertex/edge/polygon statistics and validate topology for loose vertices, degenerate faces, and non-manifold edges.
- **Input**: `object_name` (required), `limit` (optional).
- **Output**: `UnifiedEnvelope` with geometry summary or bounded validation findings.
- **Business Rules**: Actions require an existing mesh object. Validation examples bounded by 1000 records. Does not accept arbitrary operators or Python code.
- **Edge Cases**: Non-mesh object; empty mesh; limit exceeded; cyclic geometry data.
- **Error Handling**: `not_found` for missing objects; `validation_error` for non-mesh types; `serialization_error` for unsafe cyclic data.

### FR-002: Mesh Edit Operations and UV Layers
- **Description**: Perform allow-listed edit operations and ensure named UV layers exist.
- **Input**: `object_name`, `operation` (recalculate_normals, triangulate, remove_doubles), `uv_layer_name`.
- **Output**: `UnifiedEnvelope` confirming mutation or UV layer creation.
- **Business Rules**: Edit operations use Blender `bmesh` without requiring UI edit-mode context. UV layer names limited to 64 characters.
- **Edge Cases**: Object lacks mesh data; invalid operation name; UV name exceeds length limit.
- **Error Handling**: `validation_error` for invalid operations/lengths; `execution_error` for bmesh failures.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `get_mesh_statistics` | `object_name` | `UnifiedEnvelope` | Read-only vertex/edge/polygon summary |
| `validate_mesh` | `object_name`, `limit` | `UnifiedEnvelope` | Topology validation findings |
| `perform_mesh_edit_operation` | `object_name`, `operation` | `UnifiedEnvelope` | Recalculate normals, triangulate, etc. |
| `ensure_mesh_uv_layer` | `object_name`, `uv_layer_name` | `UnifiedEnvelope` | Create or reuse UV layer |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (command transport), `object` (object resolution), `dispatcher` (action routing).

## Non-functional Requirements (Detailed)

- **Performance**: Validation bounded to 1000 records. Edit operations execute synchronously via `bmesh`.
- **Security**: No arbitrary operators or Python code accepted. Strict allow-list for edit operations.
- **Scalability**: Operations are local data-block mutations with deterministic limits.

## Test Scenarios / QA Checklist

- [ ] Verify `get_mesh_statistics` returns correct vertex/edge/polygon counts.
- [ ] Verify `validate_mesh` correctly identifies non-manifold edges and bounds output to 1000.
- [ ] Verify `perform_mesh_edit_operation` rejects operations not in the allow-list.
- [ ] Verify `ensure_mesh_uv_layer` rejects names > 64 characters.

## Assumptions & Constraints

- The feature does not accept filesystem paths or external geometry formats.
- Complex sculpting or procedural geometry generation is out of scope.

## Glossary

- **bmesh**: Blender's internal Python API for direct mesh topology manipulation.
- **Non-manifold**: Geometry where edges are shared by more than two faces, causing rendering/simulation issues.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `object`, `dispatcher`
