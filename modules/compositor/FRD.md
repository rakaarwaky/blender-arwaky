# FRD — Compositor Feature

## System Overview
The Compositor module provides bounded compositor node graph inspection and mutation for the active scene. It allows AI agents to wire basic post-processing effects without exposing the full complexity of Blender's node tree API or allowing arbitrary code execution.

## Functional Requirements

### FR-001: Compositor Inspection and Configuration
- **Description**: Inspect compositor nodes and enable/disable compositor node usage.
- **Input**: `limit` (optional), `use_nodes` (boolean).
- **Output**: `UnifiedEnvelope` with bounded node/socket metadata or configuration confirmation.
- **Business Rules**: Inspection bounded to 1000 nodes and links. Node creation uses an explicit allow-list.
- **Edge Cases**: Compositor disabled; empty node tree; limit exceeded.
- **Error Handling**: `validation_error` for invalid limits; `state_error` if compositor context is unavailable.

### FR-002: Node Creation and Linking
- **Description**: Create allow-listed nodes and link exact existing sockets.
- **Input**: `node_type`, `node_name`, `from_node`, `from_socket`, `to_node`, `to_socket`.
- **Output**: `UnifiedEnvelope` confirming creation or linkage.
- **Business Rules**: Link mutation requires exact node and socket names and is idempotent. No compositor action opens sockets or executes arbitrary code.
- **Edge Cases**: Socket type mismatch; cyclic dependencies; missing node/socket names.
- **Error Handling**: `validation_error` for socket mismatches; `not_found` for missing nodes; `unsupported` for disallowed node types.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `inspect_compositor_nodes` | `limit` | `UnifiedEnvelope` | Read-only bounded node graph |
| `configure_compositor` | `use_nodes` | `UnifiedEnvelope` | Enable/disable compositor |
| `create_compositor_node` | `node_type`, `node_name` | `UnifiedEnvelope` | Create allow-listed node |
| `set_compositor_link` | `from_node`, `from_socket`, `to_node`, `to_socket` | `UnifiedEnvelope` | Link exact sockets |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (Blender command transport), `dispatcher` (action routing).

## Non-functional Requirements (Detailed)

- **Performance**: Node graph inspection bounded to 1000 records to prevent payload exhaustion.
- **Security**: Node creation restricted to an explicit allow-list to prevent injection of dangerous Blender operators.
- **Scalability**: Link mutations are idempotent and serialized via the `gateway` queue.

## Test Scenarios / QA Checklist

- [ ] Verify `inspect_compositor_nodes` truncates safely at 1000 nodes.
- [ ] Verify `create_compositor_node` rejects arbitrary Blender type strings not in the allow-list.
- [ ] Verify `set_compositor_link` fails with `validation_error` on socket type mismatch.

## Assumptions & Constraints

- The feature does not evaluate node tree outputs (handled by Blender's render engine).
- Material node trees are out of scope; only the scene compositor is managed.

## Glossary

- **Allow-list**: A predefined set of safe node types permitted for creation.
- **Socket**: The input/output connection point on a compositor node.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `dispatcher`
