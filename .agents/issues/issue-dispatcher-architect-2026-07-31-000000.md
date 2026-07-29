# Additional Plan: Consolidate All Action Schemas into `taxonomy_dispatcher_constant.py`

If the goal is to move all `surface_*_action.py` files into **one taxonomy constant file**, the correct target is:

```text
modules/shared/src/dispatcher/taxonomy_dispatcher_constant.py
```

Then the old surface schema files should be removed.

---

## 1. Final File Name

Use:

```text
taxonomy_dispatcher_constant.py
```

Do **not** use:

```text
taxonomy_dispatcher_cosntant.py
```

The suffix must be:

```text
_constant.py
```

This satisfies the taxonomy naming rule under AES102.

---

## 2. Final File Location

The file must live in the shared taxonomy layer:

```text
modules/shared/src/dispatcher/taxonomy_dispatcher_constant.py
```

It should **not** remain inside:

```text
modules/dispatcher/src/
```

The current files are named as surface files, but their content is only static schema data. That data belongs in taxonomy constants, not in the surface layer.

---

## 3. The File Must Contain Only Constants

`taxonomy_dispatcher_constant.py` must not contain functions.

Do **not** move these functions into the taxonomy constant file:

```python
def get_action_schema(action: str): ...
```

```python
def validate_action_args(action: str, args: dict[str, Any]): ...
```

```python
def get_domain_actions(domain: str): ...
```

Taxonomy constants must be pure literal values only.

So the file should not contain:

```python
def ...
class ...
for ...
while ...
if __name__ == "__main__":
    ...
```

It should only contain constants such as:

```python
DISPATCHER_ACTION_SCHEMAS = {...}
```

---

## 4. Recommended Constant Structure

Use one main constant organized by domain.

Example:

```python
"""Dispatcher action schema constants.

Taxonomy layer:
  - Pure constants only.
  - No functions.
  - No validation.
  - No I/O.
  - No runtime mutation.
"""

DISPATCHER_ACTION_SCHEMAS = {
    "scene": {
        "get_scene_info": {
            "description": "Full scene metadata — object count, frame range, resolution, render engine",
            "parameters": {},
        },
        "cleanup_scene": {
            "description": "Remove objects from scene by mode",
            "parameters": {
                "mode": {
                    "type": "string",
                    "required": True,
                    "description": "Cleanup scope",
                    "enum": ["all", "objects", "meshes"],
                },
            },
        },
        "setup_environment": {
            "description": "Setup HDRI lighting for the scene",
            "parameters": {
                "hdri_id": {
                    "type": "string",
                    "required": True,
                    "description": "HDRI asset identifier",
                },
                "strength": {
                    "type": "number",
                    "required": False,
                    "description": "Light intensity multiplier",
                    "default": 1.0,
                },
            },
        },
    },
    "object": {
        "get_object_info": {
            "description": "Get details of a specific object — location, rotation, scale, modifiers, materials",
            "parameters": {
                "object_name": {
                    "type": "string",
                    "required": True,
                    "description": "Name of the target object",
                },
            },
        },
        "create_primitive": {
            "description": "Create a new primitive mesh object",
            "parameters": {
                "primitive_type": {
                    "type": "string",
                    "required": True,
                    "description": "Primitive shape",
                    "enum": ["SPHERE", "CUBE", "CYLINDER", "PLANE", "CONE", "TORUS"],
                },
                "location": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Position [x, y, z]",
                    "default": [0, 0, 0],
                },
                "scale": {
                    "type": "array[number]",
                    "required": False,
                    "description": "Scale [x, y, z]",
                    "default": [1, 1, 1],
                },
                "name": {
                    "type": "string",
                    "required": False,
                    "description": "Custom object name",
                },
            },
        },
    },
    "render": {
        "render": {
            "description": "Execute a full frame render",
            "parameters": {
                "output_path": {
                    "type": "string",
                    "required": True,
                    "description": "Output path for rendered image",
                },
                "resolution_x": {
                    "type": "integer",
                    "required": False,
                    "description": "Render width in pixels",
                    "default": 1920,
                },
                "resolution_y": {
                    "type": "integer",
                    "required": False,
                    "description": "Render height in pixels",
                    "default": 1080,
                },
            },
        },
    },
    "asset": {
        "import_glb": {
            "description": "Import a GLB/GLTF file into the scene",
            "parameters": {
                "file_path": {
                    "type": "string",
                    "required": True,
                    "description": "Path to the GLB/GLTF file",
                },
                "object_name": {
                    "type": "string",
                    "required": False,
                    "description": "Custom name for the imported object",
                },
            },
        },
    },
    "launcher": {
        "launch_blender": {
            "description": "Start Blender with integration component active",
            "parameters": {
                "mode": {
                    "type": "string",
                    "required": False,
                    "description": "Blender launch mode",
                    "enum": ["interface", "headless"],
                    "default": "headless",
                },
                "port": {
                    "type": "integer",
                    "required": False,
                    "description": "TCP port for addon communication",
                    "default": 9876,
                },
            },
        },
    },
    "job": {
        "get_task_status": {
            "description": "Query the progress and status of a background task",
            "parameters": {
                "task_id": {
                    "type": "string",
                    "required": True,
                    "description": "Task identifier returned from a previous submit action",
                },
            },
        },
    },
    "config": {
        "get_config": {
            "description": "Retrieve BlenderArwaky configuration settings",
            "parameters": {
                "key": {
                    "type": "string",
                    "required": False,
                    "description": "Specific config key to retrieve. Omit for all settings.",
                },
            },
        },
    },
}
```

This is only a partial example. All action schemas from the old surface files should be moved here.

---

## 5. Do Not Use Loops in the Constant File

The current `surface_action_registry.py` contains logic like this:

```python
ALL_ACTIONS: dict[str, dict[str, Any]] = {}
ACTION_DOMAIN: dict[str, str] = {}

for domain, actions in [...]:
    for action_name, schema in actions.items():
        ALL_ACTIONS[action_name] = schema
        ACTION_DOMAIN[action_name] = domain
```

This must **not** be moved into `taxonomy_dispatcher_constant.py`.

Reason:

- constants must be pure literal values,
- no runtime logic is allowed,
- no loops are allowed,
- no dynamic structure building is allowed.

If a flattened index like `ALL_ACTIONS` is needed, build it in another layer, for example in a capability or bootstrap composition, not in taxonomy.

---

## 6. Do Not Move `get_action_schema()` into the Constant File

This function:

```python
def get_action_schema(action: str):
    return ALL_ACTIONS.get(action)
```

must not be placed inside `taxonomy_dispatcher_constant.py`.

If this behavior is still needed, move it to an appropriate capability, for example:

```text
modules/dispatcher/src/capabilities_action_discovery.py
```

or a new capability such as:

```text
modules/dispatcher/src/capabilities_action_schema_resolver.py
```

However, the better direction is to use the dispatcher catalog and discovery flow instead of creating another helper registry.

---

## 7. `validate_action_args()` Must Be Removed or Moved to Validation Capability

This function:

```python
def validate_action_args(action: str, args: dict[str, Any]) -> list[str]: ...
```

is validation logic.

The correct location is:

```text
modules/dispatcher/src/capabilities_request_validation.py
```

It must not be placed in taxonomy.

Recommended direction:

- remove `validate_action_args()` from the surface registry,
- let `RequestValidationExecutor` remain the main validator,
- if needed, add private helper methods inside `RequestValidationExecutor`.

The validation flow should be:

```python
RequestValidationExecutor.validate_request(ActionCommandVO(...))
```

not:

```python
surface_action_registry.validate_action_args(...)
```

---

## 8. The Constant File Must Not Construct `ActionMetadataVO`

Do not do this inside `taxonomy_dispatcher_constant.py`:

```python
from .taxonomy_action_metadata_vo import ActionMetadataVO

ACTION_METADATA = ActionMetadataVO(...)
```

The constant file should contain literal data only.

This is allowed:

```python
DISPATCHER_ACTION_METADATA_SEED = {
    "get_scene_info": {
        "owning_feature_ref": "scene",
        "default_timeout": 30.0,
        "timeout_class": "default",
        "idempotency_flag": True,
        "scene_mutation_flag": False,
        "background_eligibility_flag": False,
        "destructive_flag": False,
        "read_only_flag": True,
        "long_running_flag": False,
        "risk_level": "low",
    },
}
```

Later, `ActionMetadataVO` objects can be constructed in a capability, root bootstrap, or owning-feature registration flow — not inside the taxonomy constant file.

---

## 9. Optional: Add Metadata Seed in the Same File

If you want the single file to become the complete source of dispatcher action data, you may also add metadata seed constants.

Example:

```python
DISPATCHER_ACTION_METADATA_SEED = {
    "scene": {
        "get_scene_info": {
            "owning_feature_ref": "scene",
            "default_timeout": 30.0,
            "timeout_class": "default",
            "idempotency_flag": True,
            "scene_mutation_flag": False,
            "background_eligibility_flag": False,
            "destructive_flag": False,
            "read_only_flag": True,
            "long_running_flag": False,
            "risk_level": "low",
        },
        "cleanup_scene": {
            "owning_feature_ref": "scene",
            "default_timeout": 60.0,
            "timeout_class": "default",
            "idempotency_flag": False,
            "scene_mutation_flag": True,
            "background_eligibility_flag": False,
            "destructive_flag": True,
            "read_only_flag": False,
            "long_running_flag": False,
            "risk_level": "high",
        },
    },
    "object": {
        "create_primitive": {
            "owning_feature_ref": "object",
            "default_timeout": 30.0,
            "timeout_class": "default",
            "idempotency_flag": False,
            "scene_mutation_flag": True,
            "background_eligibility_flag": False,
            "destructive_flag": False,
            "read_only_flag": False,
            "long_running_flag": False,
            "risk_level": "medium",
        },
    },
    "render": {
        "render": {
            "owning_feature_ref": "render",
            "default_timeout": 300.0,
            "timeout_class": "long",
            "idempotency_flag": False,
            "scene_mutation_flag": False,
            "background_eligibility_flag": True,
            "destructive_flag": False,
            "read_only_flag": True,
            "long_running_flag": True,
            "risk_level": "medium",
        },
    },
}
```

This is optional.

If the initial scope is only moving schemas, then this is enough:

```python
DISPATCHER_ACTION_SCHEMAS
```

---

## 10. Update the Shared Dispatcher `__init__.py`

File:

```text
modules/shared/src/dispatcher/__init__.py
```

If the constant will be used by other modules, export it.

Add:

```python
from .taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS
```

and:

```python
__all__ = [
    ...
    "DISPATCHER_ACTION_SCHEMAS",
]
```

If metadata seed is also added:

```python
from .taxonomy_dispatcher_constant import (
    DISPATCHER_ACTION_SCHEMAS,
    DISPATCHER_ACTION_METADATA_SEED,
)
```

then:

```python
__all__ = [
    ...
    "DISPATCHER_ACTION_SCHEMAS",
    "DISPATCHER_ACTION_METADATA_SEED",
]
```

---

## 11. Remove the Old Surface Files

After moving the schemas, delete:

```text
modules/dispatcher/src/surface_action_registry.py
modules/dispatcher/src/surface_asset_action.py
modules/dispatcher/src/surface_config_action.py
modules/dispatcher/src/surface_job_action.py
modules/dispatcher/src/surface_launcher_action.py
modules/dispatcher/src/surface_object_action.py
modules/dispatcher/src/surface_render_action.py
modules/dispatcher/src/surface_scene_action.py
```

These files should no longer be needed.

---

## 12. Make Sure No Old Imports Remain

Search for all old imports:

```text
surface_action_registry
surface_asset_action
surface_config_action
surface_job_action
surface_launcher_action
surface_object_action
surface_render_action
surface_scene_action
```

Example commands:

```bash
grep -rn "surface_action_registry" modules/
grep -rn "surface_asset_action" modules/
grep -rn "surface_config_action" modules/
grep -rn "surface_job_action" modules/
grep -rn "surface_launcher_action" modules/
grep -rn "surface_object_action" modules/
grep -rn "surface_render_action" modules/
grep -rn "surface_scene_action" modules/
```

All of these imports must be removed or replaced.

---

## 13. Replace Old Registry Usage

If previous code uses:

```python
from modules.dispatcher.src.surface_action_registry import ALL_ACTIONS
```

replace it with access to the taxonomy constant:

```python
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import (
    DISPATCHER_ACTION_SCHEMAS,
)
```

However, for runtime consumption, the better approach is not to access the constant directly from surface code.

Preferred flow:

```text
CLI/MCP
  ↓
IDispatcherAggregate.discover_actions()
  ↓
Dispatcher catalog
```

Not:

```text
CLI/MCP
  ↓
taxonomy_dispatcher_constant
```

For bootstrap or registration, accessing the constant is still reasonable.

---

## 14. Use the Constant for Catalog Registration

The constant can later be used to register actions into the dispatcher catalog.

Preferred flow:

```text
taxonomy_dispatcher_constant.py
  ↓
registration bootstrap / owning feature
  ↓
CatalogRegistrationExecutor.register_action(ActionMetadataVO)
  ↓
Dispatcher catalog
```

Example concept:

```python
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import (
    DISPATCHER_ACTION_SCHEMAS,
)
```

Then each action can be built as:

```python
ActionMetadataVO(
    action_name="create_primitive",
    owning_feature_ref="object",
    description=schema["description"],
    parameter_schema=schema["parameters"],
    usage_examples=[...],
    default_timeout=30.0,
    timeout_class="default",
    idempotency_flag=False,
    scene_mutation_flag=True,
    background_eligibility_flag=False,
    destructive_flag=False,
    read_only_flag=False,
    long_running_flag=False,
    risk_level="medium",
)
```

Then register it:

```python
dispatcher.register_action(metadata)
```

---

## 15. Do Not Let CLI/MCP Use Two Sources of Truth

After migration, avoid the old pattern:

```text
CLI/MCP uses surface_action_registry
Dispatcher uses CatalogRegistrationExecutor
```

It should become one source of truth:

```text
Dispatcher catalog = main source
```

The constant is only the raw material for registration.

Expected final result:

```text
taxonomy_dispatcher_constant.py
        ↓
ActionMetadataVO registration
        ↓
Dispatcher catalog
        ↓
discover_actions()
        ↓
CLI/MCP
```

---

## 16. AES Compliance Checklist

After migration, verify the following.

### AES101 — Naming

File:

```text
taxonomy_dispatcher_constant.py
```

follows:

```text
prefix_concept_suffix
```

with:

```text
prefix = taxonomy
concept = dispatcher
suffix = constant
```

---

### AES102 — Suffix

Suffix:

```text
_constant
```

is a valid taxonomy suffix.

---

### AES303 — Mandatory Definition

Constant files are exceptions, so they do not need to contain a class or struct.

However, they must still contain real constants.

---

### AES401 — Taxonomy Role

The file must contain constants only.

It must not contain:

```python
def ...
class ...
for ...
while ...
if __name__ == "__main__":
    ...
```

It must not perform I/O.

---

### AES201 — Import Boundary

A taxonomy constant must not import:

```text
capabilities_*
agent_*
surface_*
root_*
contract_*
```

Ideally, this file does not need any imports at all.

If it only contains dictionary literals, it is safer without imports.

---

### AES506 — Surface Orphan

After deleting the old surface files, the surface orphan issue is removed.

There will no longer be unclear files like:

```text
surface_*_action.py
```

without a clear surface consumer.

---

## 17. Risk of Using One Large File

Because all actions are placed into one file, watch AES301:

```text
Default maximum file limit: 1000 lines
```

For the current schemas, one file is likely still safe.

But if the action catalog grows and the file exceeds 1000 lines, split it into:

```text
taxonomy_dispatcher_scene_constant.py
taxonomy_dispatcher_object_constant.py
taxonomy_dispatcher_render_constant.py
taxonomy_dispatcher_asset_constant.py
taxonomy_dispatcher_launcher_constant.py
taxonomy_dispatcher_job_constant.py
taxonomy_dispatcher_config_constant.py
```

Then use one index constant file:

```text
taxonomy_dispatcher_constant.py
```

For now, if the goal is simplicity, one file is acceptable.

---

## 18. Short Action Plan

You can use this as the action-item list:

```markdown
- [ ] P0 Create `modules/shared/src/dispatcher/taxonomy_dispatcher_constant.py`.
- [ ] P0 Move all schemas from `surface_*_action.py` into literal constants in that file.
- [ ] P0 Ensure the constant file contains no functions, loops, classes, or I/O.
- [ ] P0 Delete `modules/dispatcher/src/surface_action_registry.py`.
- [ ] P0 Delete all `modules/dispatcher/src/surface_*_action.py` files.
- [ ] P1 Update `modules/shared/src/dispatcher/__init__.py` if the constant needs to be exported.
- [ ] P1 Use the constant as the source for action registration.
- [ ] P1 Ensure action validation is handled only by `RequestValidationExecutor`.
- [ ] P1 Ensure CLI/MCP retrieve action lists through `IDispatcherAggregate.discover_actions()`.
- [ ] P2 Run verification for imports, naming, taxonomy role, and surface orphan rules.
```

---

## 19. Recommended Final Structure

Minimal final structure:

```text
modules/shared/src/dispatcher/
├── __init__.py
├── contract_action_discovery_protocol.py
├── contract_background_submit_protocol.py
├── contract_catalog_registration_protocol.py
├── contract_dispatcher_aggregate.py
├── contract_request_validation_protocol.py
├── contract_result_normalization_protocol.py
├── contract_sync_dispatch_protocol.py
├── taxonomy_action_command_vo.py
├── taxonomy_action_metadata_vo.py
├── taxonomy_dispatcher_constant.py
├── taxonomy_discovery_outcome_vo.py
└── taxonomy_unified_result_envelope_vo.py
```

And the old surface files inside dispatcher should be gone:

```text
modules/dispatcher/src/surface_action_registry.py        ← delete
modules/dispatcher/src/surface_asset_action.py           ← delete
modules/dispatcher/src/surface_config_action.py          ← delete
modules/dispatcher/src/surface_job_action.py             ← delete
modules/dispatcher/src/surface_launcher_action.py        ← delete
modules/dispatcher/src/surface_object_action.py          ← delete
modules/dispatcher/src/surface_render_action.py          ← delete
modules/dispatcher/src/surface_scene_action.py           ← delete
```

---

## Conclusion

The best plan is:

```text
Move all action schemas into:
modules/shared/src/dispatcher/taxonomy_dispatcher_constant.py

Content should only be:
DISPATCHER_ACTION_SCHEMAS = { ... }

Do not move:
- get_action_schema()
- validate_action_args()
- ALL_ACTIONS loop
- ACTION_DOMAIN loop

Then delete all surface_*_action.py files and surface_action_registry.py.
```

This makes the action schemas clean taxonomy constants, keeps them in one file, satisfies AES rules, and removes the orphan surface-schema subsystem.
