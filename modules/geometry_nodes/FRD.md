# FRD — Geometry Nodes Feature

## System Overview
The Geometry Nodes module provides bounded inspection and mutation of Blender Geometry Node graphs. It allows AI agents to inspect node group topology, create basic node groups, and wire sockets without exposing the full complexity of Blender's node tree API or allowing arbitrary code execution.

## Functional Requirements

### FR-001: Node Group Inspection and Creation
- **Description**: Inspect node group topology and create allow-listed geometry node groups.
- **Input**: `node_group_name`, `object_name` (optional).
- **Output**: `UnifiedEnvelope` with bounded node/socket metadata or creation confirmation.
- **Business Rules**: Inspection bounded to 1000 nodes/links per group. Node creation uses explicit allow-list of basic types (e.g., `GeometryNodeGroup`). Arbitrary Blender type strings rejected.
- **Edge Cases**: Non-existent node group; node group name collision; object does not support geometry nodes.
- **Error Handling**: `not_found` for missing groups; `validation_error` for invalid names; `unsupported` for incompatible objects.

### FR-002: Node Linking and Modifier Application
- **Description**: Link specific sockets between nodes and add/remove geometry node modifiers on objects.
- **Input**: `node_group_name`, `from_node`, `from_socket`, `to_node`, `to_socket`, `object_name`.
- **Output**: `UnifiedEnvelope` confirming linkage or modifier application.
- **Business Rules**: Link mutation requires exact node and socket names. Socket type validation prevents invalid links. Cyclic dependency detection prevents graph corruption.
- **Edge Cases**: Socket type mismatch (e.g., Float to Geometry); cyclic dependencies; missing sockets.
- **Error Handling**: `validation_error` for socket mismatches or cycles; `not_found` for missing sockets.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `inspect_geometry_node_group` | `node_group_name` | `NodeGroupTopology` | Read-only bounded topology (max 1000 nodes/links per group); raises `not_found` on missing group, `validation_error` on invalid name |
| `create_geometry_node_group` | `node_group_name`, `object_name` | `geometry_node_group_created` | Create basic allow-listed node group; raises `unsupported` for incompatible objects, `validation_error` on invalid names |
| `set_geometry_node_link` | `node_group_name`, `from_node`, `to_node` | `geometry_node_link_set` | Link exact sockets with socket-type validation and cyclic dependency detection (idempotent); raises `validation_error` on mismatch/cycle, `not_found` on missing sockets |
| `set_geometry_node_modifier` | `object_name`, `node_group_name` | `geometry_node_modifier_set` | Add/Remove geometry node modifier on object; raises `not_found`, `unsupported` |
## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (command transport), `object` (applying modifiers), `security` (preventing code injection).

## Non-functional Requirements (Detailed)

- **Performance**: Topology reads bounded to 1000 nodes to prevent payload exhaustion.
- **Security**: Node creation restricted to an allow-list. No geometry node action executes arbitrary Python.
- **Scalability**: Link mutations are idempotent and serialized via the `gateway` queue.

## Test Scenarios / QA Checklist

- [ ] Verify inspection bounds enforce max 1000 nodes per group.
- [ ] Verify socket type validation prevents linking Float to Geometry.
- [ ] Verify cyclic dependency detection prevents graph corruption.
- [ ] Verify node creation rejects types not in the allow-list.

## Assumptions & Constraints

- Evaluating node tree outputs is handled by Blender's render engine, not this module.
- Modifying node group internal math/logic beyond basic linking is out of scope.

## Glossary

- **Allow-list**: Predefined set of safe geometry node types permitted for creation.
- **Socket**: The input/output connection point on a geometry node.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `object`, `security`
