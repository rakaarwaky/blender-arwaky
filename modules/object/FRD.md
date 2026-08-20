# FRD — Object Management Feature

## System Overview
The Object module is the single authority for single-object technical operations: creating primitives, placing existing objects, transforming, assigning materials, managing modifiers, and deleting individual objects. Bulk scene decisions belong to the Scene module.

## Functional Requirements

### FR-001: Object Placement, Creation, and Transformation
- **Description**: Position existing objects, create primitives, and modify transforms.
- **Input**: `object_name`, `primitive_type`, `location`, `rotation`, `scale`.
- **Output**: `UnifiedEnvelope` with resolved `BlenderObjectRef` and final transform summary.
- **Business Rules**: Reference resolution deterministic. CLI rotation converted to radians at addon boundary. Zero scale rejected unless allowed. Locked channels respected. Idempotent for identical absolute values.
- **Edge Cases**: Not found; ambiguous ref; invalid/non-finite coordinates; locked channels; unit mismatch.
- **Error Handling**: `not_found`; `ambiguous_reference`; `validation_error`; `transform_lock`.

### FR-002: Material and Modifier Management
- **Description**: Assign PBR materials, manage material properties/textures, and add/configure/remove modifiers.
- **Input**: `object_name`, `material_name`, PBR values, `modifier_type`, `modifier_name`.
- **Output**: `UnifiedEnvelope` with resolved material/modifier refs.
- **Business Rules**: PBR properties bounded 0–1. Destructive modifier application requires confirmation. Shared materials not modified unless explicitly allowed.
- **Edge Cases**: Object without slots; invalid color values; stack order conflict; linked data not editable.
- **Error Handling**: `material_assignment`; `modifier_compatibility`; `confirmation_error`.

### FR-003: Object Deletion and Inspection
- **Description**: Remove single objects with protection policies and retrieve detailed structured info.
- **Input**: `object_name`, `confirmation` flag, `detail_level`.
- **Output**: `UnifiedEnvelope` with deleted ref or object state representation.
- **Business Rules**: Protected categories (active camera, marked protected) require confirmation. Child/dependent policies respected. Safe serialization (no cyclic refs).
- **Edge Cases**: Protected without confirmation; used as constraint target; very large mesh; circular parent.
- **Error Handling**: `deletion_protection`; `scene_state`; `serialization_error`.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `get_object_info` | `object_name` | `UnifiedEnvelope` | Detailed object state |
| `create_primitive` | `primitive_type`, `location` | `UnifiedEnvelope` | Create basic 3D object |
| `set_object_transform` | `object_name`, `location`, `rotation` | `UnifiedEnvelope` | Update transform |
| `delete_object` | `object_name`, `confirm` | `UnifiedEnvelope` | Remove single object |
| `set_material` | `object_name`, `material_name` | `UnifiedEnvelope` | Assign material |
| `create_material` | `material_name`, `base_color` | `UnifiedEnvelope` | Create PBR material |
| `set_material_properties`| `material_name`, `metallic` | `UnifiedEnvelope` | Update PBR properties |
| `set_material_texture` | `material_name`, `file_path` | `UnifiedEnvelope` | Attach image texture |
| `apply_modifier` | `object_name`, `modifier_name` | `UnifiedEnvelope` | Apply/Configure modifier |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (transport), `config` (naming/protection policies), `security` (redaction), `scene` (delegates deletions).

## Non-functional Requirements (Detailed)

- **Performance**: Object info respects `detail_level` to avoid oversized responses for large meshes.
- **Security**: Destructive operations require explicit confirmation. Texture paths validated by `security`.
- **Scalability**: Single-object operations are atomic. Linked/instanced objects handled safely without unintended shared data removal.

## Test Scenarios / QA Checklist

- [ ] Verify `set_object_transform` converts CLI degrees to Blender radians correctly.
- [ ] Verify `delete_object` rejects deletion of active camera without confirmation flag.
- [ ] Verify `create_material` validates PBR bounds (0–1) and rejects out-of-range values.
- [ ] Verify `apply_modifier` requires confirmation for destructive application.
- [ ] Verify `get_object_info` safely serializes without cyclic reference crashes.

## Assumptions & Constraints

- Object owns single-object technical ops; Scene owns bulk cleanup and preservation policy.
- Generic transform belongs to Object; camera-specific optics (lens, DoF) belong to Render.

## Glossary

- **BlenderObjectRef**: Deterministic string identifier for a Blender data-block.
- **PBR (Physically Based Rendering)**: Material model using base color, metallic, roughness, and alpha.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `config`, `security`, `dispatcher`, `scene`
