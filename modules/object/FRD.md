# FRD — Object Management Feature

## Purpose

Manages 3D objects that already exist in the scene.

## Scope

- Create primitive
- Place existing object
- Transform object
- Material assignment
- Modifier management
- Delete object
- Get object info

## Out of Scope

- Asset download (owner: `asset`)
- Asset import (owner: `asset`)
- Scene cleanup bulk (owner: `scene`)
- Render (owner: `render`)
- Camera lens/framing (owner: `render`)
- HDRI (owner: `render`)
- Queue (owner: `gateway`)
- Background task (owner: `job`)

## Depends On

- `gateway`
- `config`
- `security`

## Provides To

- `dispatcher`
- `scene`

## Functional Requirements

### FR-OBJ-001: Place Existing Object

Place existing object reference. If asset not yet imported, caller must use asset feature first.

### FR-OBJ-002: Create Primitive

Create primitive object (cube, sphere, plane, etc.) at specified location.

### FR-OBJ-003: Set Transform

Set object location, rotation, and scale.

### FR-OBJ-004: Set Material

Assign material to object. Support PBR material properties.

### FR-OBJ-005: Manage Modifiers

Add, remove, or configure modifiers on object.

### FR-OBJ-006: Delete Object

Delete single object from scene. For bulk cleanup, use `scene` feature.

### FR-OBJ-007: Get Object Info

Return detailed information about object: name, type, transform, materials, modifiers.

## Boundary: Object vs Scene

- Object: single object operations
- Scene: scene-level/bulk operations

```
object.delete_object(object_ref)
scene.cleanup_scene(preserve_cameras=true)
```

## Boundary: Object vs Render

- Object: generic transform on any object including camera
- Render: camera-specific setup (lens, framing, active camera, depth of field)

For camera workflow, use `render.configure_camera`.
For direct generic transform, use `object.set_transform`.

## Error Categories

- `ObjectNotFoundError` — object reference invalid
- `TransformLockError` — transform constrained
- `ValidationError` — invalid transform/material parameters

## Events

- `object.created` — primitive created
- `object.placed` — existing object placed
- `object.transformed` — transform applied
- `object.deleted` — object removed

## Configuration Keys

- `object.default_primitive` — default primitive type
- `object.transform_units` — units for transform values

## QA Checklist

- [ ] Place existing object (not asset import)
- [ ] Create primitive at location
- [ ] Set transform (location, rotation, scale)
- [ ] Assign material with PBR properties
- [ ] Add/remove/configure modifiers
- [ ] Delete single object
- [ ] Get object info
- [ ] No overlap with asset (import) or scene (bulk cleanup)
