# FRD — object (Object Feature Module)

## System Overview

The object module handles all Blender object operations — creation, transformation, material assignment, modifier application, and deletion. It provides the object manipulate protocol and corresponding capability implementations. Import/export and socket connection are handled by separate modules (asset, server).

## Functional Requirements

### OBJ-001: Place Asset in Scene

- **Description**: Position an imported 3D asset at specified coordinates in the scene
- **Input**: PlaceAssetRequestVO (file_path, location, rotation, scale)
- **Output**: PlaceAssetResponseVO (success, object_name, message)
- **Business Rules**: Object must be imported first; coordinates must be valid Vector3D; object name must be unique
- **Edge Cases**: Object not found, invalid coordinates, name collision, zero scale
- **Error Handling**: SceneValidationError for missing objects; ValidationError for invalid params

### OBJ-002: Create Primitive Object

- **Description**: Create a basic geometric primitive (cube, sphere, cylinder, etc.)
- **Input**: CreatePrimitiveRequestVO (primitive_type, location, name, size)
- **Output**: CreatePrimitiveResponseVO (success, object_name, message)
- **Business Rules**: Primitive type must be in ALLOWED_OBJECT_TYPES; name must be unique
- **Edge Cases**: Invalid primitive type, duplicate name, zero size
- **Error Handling**: ValidationError for invalid parameters

### OBJ-003: Set Object Transform

- **Description**: Modify location, rotation, or scale of an existing object
- **Input**: SetObjectTransformRequestVO (object_name, location, rotation, scale)
- **Output**: SetObjectTransformResponseVO (success, message)
- **Business Rules**: Object must exist; transform values must be valid Vector3D
- **Edge Cases**: Object not found, invalid transform values, locked transforms
- **Error Handling**: SceneValidationError for missing objects

### OBJ-004: Set Material

- **Description**: Assign or create a material for an object
- **Input**: SetMaterialRequestVO (object_name, material_name, color, metallic, roughness)
- **Output**: SetMaterialResponseVO (success, material_name, message)
- **Business Rules**: Object must exist; material properties must be in valid ranges
- **Edge Cases**: Object not found, invalid color values, material slot conflicts
- **Error Handling**: SceneValidationError for missing objects

### OBJ-005: Apply Modifier

- **Description**: Add or modify a modifier on an object
- **Input**: ApplyModifierRequestVO (object_name, modifier_type, parameters)
- **Output**: ApplyModifierResponseVO (success, message)
- **Business Rules**: Object must support modifiers; modifier type must be valid
- **Edge Cases**: Object type doesn't support modifiers, invalid modifier parameters
- **Error Handling**: SceneValidationError for incompatible objects

### OBJ-006: Delete Object

- **Description**: Remove an object from the scene
- **Input**: DeleteObjectRequestVO (object_name)
- **Output**: DeleteObjectResponseVO (success, message)
- **Business Rules**: Object must exist; cannot delete camera or light without confirmation
- **Edge Cases**: Object not found, last object in scene, linked objects
- **Error Handling**: SceneValidationError for missing objects

### OBJ-007: Get Object Info

- **Description**: Retrieve detailed information about a specific object
- **Input**: GetObjectInfoRequestVO (object_name)
- **Output**: GetObjectInfoResponseVO (success, object_info: BlenderObject)
- **Business Rules**: Object must exist; returns full BlenderObject entity
- **Edge Cases**: Object not found, deleted object reference
- **Error Handling**: SceneValidationError for missing objects

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `place_asset` | PlaceAssetRequestVO | PlaceAssetResponseVO | Position imported asset |
| `create_primitive` | CreatePrimitiveRequestVO | CreatePrimitiveResponseVO | Create geometric primitive |
| `set_transform` | SetObjectTransformRequestVO | SetObjectTransformResponseVO | Modify object transform |
| `set_material` | SetMaterialRequestVO | SetMaterialResponseVO | Assign material |
| `apply_modifier` | ApplyModifierRequestVO | ApplyModifierResponseVO | Add/modify modifier |
| `delete_object` | DeleteObjectRequestVO | DeleteObjectResponseVO | Remove object |
| `get_object_info` | GetObjectInfoRequestVO | GetObjectInfoResponseVO | Get object details |

## Integration Points

- **Internal**: shared (taxonomy VOs, contracts), server (Blender connection)
- **External**: Blender Python API (bpy) — via server module

## Non-functional Requirements

- Performance: Object operations complete within 2 seconds
- Reliability: Delegates to server for Blender communication

## Test Scenarios / QA Checklist

- [ ] Place asset at valid coordinates succeeds
- [ ] Place asset with missing object returns SceneValidationError
- [ ] Create primitive with valid type succeeds
- [ ] Create primitive with invalid type returns ValidationError
- [ ] Set transform on existing object succeeds
- [ ] Set transform on missing object returns SceneValidationError
- [ ] Delete object succeeds and removes from scene
- [ ] Get info on existing object returns BlenderObject

## Assumptions & Constraints

- Blender 3.0+ must be running with addon enabled
- Object operations delegated to Blender via server module
- Import/export handled by asset module

## Glossary

- **BlenderObject**: Domain entity representing a Blender object with full state
- **PrimitiveType**: Enum of supported geometric primitives
- **Vector3D**: 3D coordinate/rotation/scale value object

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
- FRD server: [../server/FRD.md](../server/FRD.md)
- FRD asset: [../asset/FRD.md](../asset/FRD.md)
