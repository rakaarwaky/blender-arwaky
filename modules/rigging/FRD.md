# FRD — Rigging and Deformation Feature

## Purpose

Provide bounded armature inspection, pose-bone control, allow-listed bone constraints, shape-key configuration, and deformation-state inspection through canonical dispatcher actions.

## Canonical actions

| Action | Type | Contract |
|---|---|---|
| `inspect_armature` | Read-only | Bounded armature bones, hierarchy, deform flags, and pose summary |
| `set_pose_bone_transform` | Mutation | Set one named pose bone location, Euler rotation, and/or scale with bounds |
| `configure_bone_constraint` | Mutation | Create/update/remove one allow-listed constraint with validated target references |
| `configure_shape_key` | Mutation | Create/update/remove one named shape key with bounded value and slider limits |
| `get_deformation_state` | Read-only | Bounded armature modifiers, constraints, and shape-key summary for one mesh |

## Invariants

Actions require explicit object names and never select arbitrary UI context. Armature inspection is limited to 1000 bones. Pose transforms use finite numeric vectors and bounded scale. Constraint types are limited to `COPY_LOCATION`, `COPY_ROTATION`, `LIMIT_LOCATION`, and `LIMIT_ROTATION`; arbitrary drivers, Python expressions, and full IK orchestration are not accepted. Shape-key values and slider limits are finite and bounded.

The feature does not implement automatic weighting, weight painting, retargeting, driver graph authoring, B-Bone authoring, or external rig formats. All Blender access is delegated through the injected gateway in the AES executor and the addon server handler; no direct MCP registration or private task registry is permitted.

## Verification

Unit tests cover vector bounds, constraint allow-list, shape-key bounds, and gateway delegation. Contract tests cover action ownership and read-only flags. Blender smoke tests cover armature creation and hierarchy inspection, pose-bone transform, copy-rotation constraint, shape-key configuration, deformation state, and structured invalid-input errors.
