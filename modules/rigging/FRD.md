# FRD — Rigging and Deformation Feature

## System Overview
The Rigging module provides bounded armature inspection, pose-bone control, allow-listed bone constraints, shape-key configuration, and deformation-state inspection. It delegates all Blender access through the Gateway and avoids automatic weighting or external rig formats.

## Functional Requirements

### FR-001: Armature Inspection and Pose Control
- **Description**: Inspect armature hierarchy and set pose-bone transforms.
- **Input**: `armature_name`, `bone_name`, `location`, `rotation_euler`, `scale`, `limit`.
- **Output**: `UnifiedEnvelope` with bounded bone summary or transform confirmation.
- **Business Rules**: Inspection limited to 1000 bones. Pose transforms use finite numeric vectors. Actions require explicit object names.
- **Edge Cases**: Missing armature; non-existent bone; non-finite vectors; scale bounds exceeded.
- **Error Handling**: `not_found` for missing armatures/bones; `validation_error` for invalid vectors.

### FR-002: Constraints, Shape Keys, and Deformation State
- **Description**: Configure allow-listed bone constraints, manage shape keys, and inspect deformation modifiers.
- **Input**: `constraint_type`, `target_object`, `shape_key_name`, `value`, `slider_min`.
- **Output**: `UnifiedEnvelope` confirming mutation or deformation summary.
- **Business Rules**: Constraint types limited to `COPY_LOCATION`, `COPY_ROTATION`, `LIMIT_LOCATION`, `LIMIT_ROTATION`. Shape-key values bounded. No arbitrary drivers or Python expressions accepted.
- **Edge Cases**: Invalid constraint target; shape-key value outside slider limits; cyclic constraint dependencies.
- **Error Handling**: `validation_error` for disallowed constraints or out-of-bounds values; `execution_error` for Blender evaluation failures.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `inspect_armature` | `object_name`, `limit` | `ArmatureHierarchy` | Bounded bone hierarchy (max 1000 bones); raises `not_found` on missing armature, `validation_error` on invalid limit |
| `set_pose_bone_transform` | `armature_name`, `bone_name`, `location` | `pose_bone_transform_updated` | Mutate pose bone with finite numeric vectors; raises `not_found` on missing armature/bone, `validation_error` for non-finite vectors |
| `configure_bone_constraint` | `armature_name`, `bone_name`, `constraint_type` | `bone_constraint_configured` | Add/update allow-listed constraint (COPY_LOCATION, COPY_ROTATION, LIMIT_LOCATION, LIMIT_ROTATION); raises `validation_error` for disallowed types or invalid targets |
| `configure_shape_key` | `object_name`, `shape_key_name`, `value` | `shape_key_configured` | Mutate shape key within slider bounds; raises `not_found`, `validation_error` for out-of-bounds value |
| `get_deformation_state` | `object_name` | `DeformationState` | Read-only armature modifiers summary; raises `not_found` |
## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway` (command transport), `dispatcher` (action routing).

## Non-functional Requirements (Detailed)

- **Performance**: Armature inspection bounded to 1000 bones to prevent payload exhaustion.
- **Security**: Constraint targets validated to prevent arbitrary object linkage. No Python drivers accepted.
- **Scalability**: Pose mutations serialized via Gateway queue.

## Test Scenarios / QA Checklist

- [ ] Verify `inspect_armature` truncates safely at 1000 bones.
- [ ] Verify `set_pose_bone_transform` rejects non-finite vectors.
- [ ] Verify `configure_bone_constraint` rejects types not in the allow-list.
- [ ] Verify `configure_shape_key` enforces slider min/max bounds.

## Assumptions & Constraints

- Automatic weighting, weight painting, and retargeting are out of scope.
- Full IK orchestration and driver graph authoring are not supported.

## Glossary

- **Pose Bone**: The animatable representation of a bone in an armature, distinct from the edit bone.
- **Allow-list**: Predefined set of safe constraint types permitted for configuration.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `dispatcher`
