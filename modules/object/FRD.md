# FRD — object (Object Feature Module)

## System Overview

The object module handles all Blender object operations — creation, transformation, material assignment, modifier application, and deletion. It contains the object-specific capabilities, infrastructure adapters (Blender socket communication), and orchestrators.

```
modules/object/
├── blender_port.py              ← BlenderPort ABC (contract)
├── connection_port.py           ← BlenderConnectionPort ABC
├── connection_factory_port.py   ← BlenderConnectionFactoryPort ABC
├── code_execution_port.py       ← CodeExecutionPort ABC
├── object_operate_protocol.py   ← ObjectOperateProtocol ABC
├── blender_socket_adapter.py    ← BlenderPort implementation
├── blender_connection.py        ← TCP socket connection manager
├── code_execution_adapter.py    ← Code validation + execution
├── capabilities_object_operate_executor.py  ← Object manipulation logic
├── capabilities_import_export_executor.py   ← GLB/OBJ import/export
└── __init__.py
```

## Functional Requirements

### FR-001: Place Asset in Scene

- **Description**: Import and position a 3D asset at specified coordinates
- **Input**: PlaceAssetRequestVO (file_path, location, rotation, scale)
- **Output**: PlaceAssetResponseVO (success, object_name, message)
- **Business Rules**: File must exist; coordinates must be valid Vector3D; object name must be unique
- **Edge Cases**: File not found, invalid file format, name collision, zero scale
- **Error Handling**: AssetNotFoundError for missing files; ValidationError for invalid params

### FR-002: Create Primitive Object

- **Description**: Create a basic geometric primitive (cube, sphere, cylinder, etc.)
- **Input**: CreatePrimitiveRequestVO (primitive_type, location, name, size)
- **Output**: CreatePrimitiveResponseVO (success, object_name, message)
- **Business Rules**: Primitive type must be in ALLOWED_OBJECT_TYPES; name must be unique
- **Edge Cases**: Invalid primitive type, duplicate name, zero size
- **Error Handling**: ValidationError for invalid parameters

### FR-003: Set Object Transform

- **Description**: Modify location, rotation, or scale of an existing object
- **Input**: SetObjectTransformRequestVO (object_name, location, rotation, scale)
- **Output**: SetObjectTransformResponseVO (success, message)
- **Business Rules**: Object must exist; transform values must be valid Vector3D
- **Edge Cases**: Object not found, invalid transform values, locked transforms
- **Error Handling**: SceneValidationError for missing objects

### FR-004: Set Material

- **Description**: Assign or create a material for an object
- **Input**: SetMaterialRequestVO (object_name, material_name, color, metallic, roughness)
- **Output**: SetMaterialResponseVO (success, material_name, message)
- **Business Rules**: Object must exist; material properties must be in valid ranges
- **Edge Cases**: Object not found, invalid color values, material slot conflicts
- **Error Handling**: SceneValidationError for missing objects

### FR-005: Apply Modifier

- **Description**: Add or modify a modifier on an object
- **Input**: ApplyModifierRequestVO (object_name, modifier_type, parameters)
- **Output**: ApplyModifierResponseVO (success, message)
- **Business Rules**: Object must support modifiers; modifier type must be valid
- **Edge Cases**: Object type doesn't support modifiers, invalid modifier parameters
- **Error Handling**: SceneValidationError for incompatible objects

### FR-006: Delete Object

- **Description**: Remove an object from the scene
- **Input**: DeleteObjectRequestVO (object_name)
- **Output**: DeleteObjectResponseVO (success, message)
- **Business Rules**: Object must exist; cannot delete camera or light without confirmation
- **Edge Cases**: Object not found, last object in scene, linked objects
- **Error Handling**: SceneValidationError for missing objects

### FR-007: Get Object Info

- **Description**: Retrieve detailed information about a specific object
- **Input**: GetObjectInfoRequestVO (object_name)
- **Output**: GetObjectInfoResponseVO (success, object_info: BlenderObject)
- **Business Rules**: Object must exist; returns full BlenderObject entity
- **Edge Cases**: Object not found, deleted object reference
- **Error Handling**: SceneValidationError for missing objects

### FR-008: Import/Export GLB/OBJ

- **Description**: Import 3D models from GLB/OBJ files or export scene objects
- **Input**: ImportGlbRequestVO / ExportModelRequestVO
- **Output**: ImportGlbResponseVO / ExportModelResponseVO
- **Business Rules**: File paths must be valid; export format must be supported
- **Edge Cases**: File not found, unsupported format, write permission denied
- **Error Handling**: AssetNotFoundError, ValidationError

### FR-009: Blender Socket Connection

- **Description**: Manage TCP socket connection to Blender addon
- **Input**: Connection parameters (host, port)
- **Output**: Active socket connection
- **Business Rules**: Auto-reconnect on failure; timeout after 30 seconds
- **Edge Cases**: Blender not running, connection refused, timeout
- **Error Handling**: BlenderConnectionFailure with retry logic

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `place_asset` | PlaceAssetRequestVO | PlaceAssetResponseVO | Import and position asset |
| `create_primitive` | CreatePrimitiveRequestVO | CreatePrimitiveResponseVO | Create geometric primitive |
| `set_transform` | SetObjectTransformRequestVO | SetObjectTransformResponseVO | Modify object transform |
| `set_material` | SetMaterialRequestVO | SetMaterialResponseVO | Assign material |
| `apply_modifier` | ApplyModifierRequestVO | ApplyModifierResponseVO | Add/modify modifier |
| `delete_object` | DeleteObjectRequestVO | DeleteObjectResponseVO | Remove object |
| `get_object_info` | GetObjectInfoRequestVO | GetObjectInfoResponseVO | Get object details |
| `import_glb` | ImportGlbRequestVO | ImportGlbResponseVO | Import 3D model |
| `export_model` | ExportModelRequestVO | ExportModelResponseVO | Export scene object |

## Integration Points

- **Internal**: shared (taxonomy VOs, contracts), config (configuration)
- **External**: Blender addon (TCP socket), Blender Python API (bpy)

## Non-functional Requirements (Detailed)

- Performance: Object operations complete within 2 seconds
- Reliability: Socket reconnection within 5 seconds
- Security: Code execution validates against blocked patterns (os, sys, subprocess)

## Test Scenarios / QA Checklist

- [ ] Place asset at valid coordinates succeeds
- [ ] Place asset with missing file returns AssetNotFoundError
- [ ] Create primitive with valid type succeeds
- [ ] Create primitive with invalid type returns ValidationError
- [ ] Set transform on existing object succeeds
- [ ] Set transform on missing object returns SceneValidationError
- [ ] Delete object succeeds and removes from scene
- [ ] Import GLB from valid file succeeds
- [ ] Export to valid path succeeds
- [ ] Socket connection handles Blender restart gracefully

## Assumptions & Constraints

- Blender 3.0+ must be running with addon enabled
- TCP socket communication (not WebSocket)
- Code execution has 30-second timeout

## Glossary

- **BlenderObject**: Domain entity representing a Blender object with full state
- **PrimitiveType**: Enum of supported geometric primitives
- **Vector3D**: 3D coordinate/rotation/scale value object

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
