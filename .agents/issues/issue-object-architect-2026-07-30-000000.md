# .agents/issues/issue-object-architect-2026-07-30-000000.md

# Issue: object — Architectural Review & Refactoring

## Summary
The `object` feature broadly follows the AES layering intent: shared taxonomy/contracts live in `modules/shared/src/object`, concrete executors live in `modules/object/src/capabilities_*`, orchestration lives in `agent_object_orchestrator.py`, and composition lives in `root_object_container.py`. However, the feature contains several critical runtime and architecture defects: unsafe/incorrect generated Blender code, incomplete FRD behavior, primitive-typed taxonomy error fields, a misnamed taxonomy error module, untyped dependency injection, duplicated helper logic across capabilities, and unused/dead constants. These issues reduce safety, FRD compliance, maintainability, and AES conformance. This issue should be addressed before the object feature can be considered stable for v1.7.0+.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Capabilities receive `code_executor: Any = None`, and root wires it as `object`. This creates an implicit, untyped dependency on the gateway execution mechanism instead of depending on a shared contract protocol. | `modules/object/src/capabilities_apply_modifier_executor.py:__init__`; `modules/object/src/capabilities_create_primitive_executor.py:__init__`; `modules/object/src/capabilities_delete_object_executor.py:__init__`; `modules/object/src/capabilities_get_object_info_executor.py:__init__`; `modules/object/src/capabilities_place_asset_executor.py:__init__`; `modules/object/src/capabilities_set_material_executor.py:__init__`; `modules/object/src/capabilities_set_transform_executor.py:__init__`; `modules/object/src/root_object_container.py:ObjectContainer.__init__` | Define or reuse a shared protocol such as `ICodeExecutionProtocol` in `modules/shared/src/gateway/contract_code_execution_protocol.py`, then type all capability constructors and the container against that protocol. |
| 2 | 🟡 WARNING | `ObjectContainer.wire()` contains an optional cross-module import for `ImportExportExecutor` from the object module itself. This couples the object composition root to an asset/import-export concern that is outside the object FRD scope. | `modules/object/src/root_object_container.py:wire` | Remove the local import. If import/export capability is required, inject it from a higher-level composition root through a shared contract protocol. If not required, delete the dead branch. |
| 3 | 🟢 INFO | `ObjectOrchestrator` stores `import_export_cap` and exposes `import_export_capability`, but no aggregate method consumes it. This is an architectural smell: the agent holds a capability that is not part of its aggregate contract. | `modules/object/src/agent_object_orchestrator.py:__init__`; `modules/object/src/agent_object_orchestrator.py:import_export_capability` | Remove the field/property, or formalize it by adding an aggregate method and contract if the feature truly belongs to object orchestration. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `taxonomy_object_error_vo.py` uses the `_vo` suffix but contains domain error classes. AES102 requires taxonomy suffixes to match content: errors should use `_error`. | `modules/shared/src/object/taxonomy_object_error_vo.py` | Rename to `taxonomy_object_error.py` and update all imports. |
| 2 | 🟢 INFO | `modules/shared/src/object/__init__.py` references `taxonomy_object_event_vo`. If that file contains domain events, its suffix should be `_event`, not `_vo`. | `modules/shared/src/object/__init__.py` | Inspect the module contents. If it defines events, rename to `taxonomy_object_event.py`. If it defines event value payloads only, document that clearly or split event types from VO types. |
| 3 | 🟢 INFO | `ObjectError` type alias is defined in the error taxonomy module but is not used in the provided snapshot. | `modules/shared/src/object/taxonomy_object_error_vo.py:ObjectError` | Remove if unused, or export/use it intentionally. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `DETAIL_LEVELS` is defined but never used. | `modules/object/src/capabilities_get_object_info_executor.py:DETAIL_LEVELS` | Remove the constant or implement detail-level handling using it. |
| 2 | 🟡 WARNING | `PROTECTED_CATEGORIES` is defined but never used; protected-category logic is hardcoded elsewhere. | `modules/object/src/capabilities_delete_object_executor.py:PROTECTED_CATEGORIES` | Remove the unused constant or refactor `_check_protected_categories()` to use it consistently. |
| 3 | 🟡 WARNING | The optional import block for `ImportExportExecutor` imports a module that does not exist in the object feature snapshot and silently falls back to `None`. This is effectively dead wiring. | `modules/object/src/root_object_container.py:wire` | Remove the block unless a concrete cross-module contract and injection path are implemented. |
| 4 | 🟢 INFO | `ObjectOrchestrator.import_export_capability` is not part of `IObjectOperateAggregate` and has no visible consumer. | `modules/object/src/agent_object_orchestrator.py:import_export_capability` | Remove if unused. |
| 5 | 🟢 INFO | `ObjectError` alias appears unused. | `modules/shared/src/object/taxonomy_object_error_vo.py:ObjectError` | Remove or use intentionally. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `_safe_str()` is duplicated across many capability executors. This violates DRY and increases the risk of inconsistent code-generation safety. AES305 duplication risk. | `capabilities_apply_modifier_executor.py:_safe_str`; `capabilities_create_primitive_executor.py:_safe_str`; `capabilities_delete_object_executor.py:_safe_str`; `capabilities_get_object_info_executor.py:_safe_str`; `capabilities_place_asset_executor.py:_safe_str`; `capabilities_set_material_executor.py:_safe_str`; `capabilities_set_transform_executor.py:_safe_str` | Extract to a shared utility module, e.g. `modules/shared/src/object/utility_blender_codegen.py` or `modules/shared/src/common/utility_code_builder.py`. |
| 2 | 🟡 WARNING | `_tuple_str()` is duplicated across place, create, and transform executors. | `capabilities_create_primitive_executor.py:_tuple_str`; `capabilities_place_asset_executor.py:_tuple_str`; `capabilities_set_transform_executor.py:_tuple_str` | Extract to shared utility. |
| 3 | 🟡 WARNING | `_validate_scale()` is duplicated across place and transform executors. | `capabilities_place_asset_executor.py:_validate_scale`; `capabilities_set_transform_executor.py:_validate_scale` | Extract to shared utility and add finite-value validation. |
| 4 | 🟡 WARNING | Capability files contain domain/catalog constants such as primitive maps, modifier maps, protected categories, and detail levels. These should live in taxonomy constants or configuration, not inside capability implementations. | `capabilities_create_primitive_executor.py:PRIMITIVE_OPS_MAP`; `capabilities_create_primitive_executor.py:NON_MESH_PRIMITIVES`; `capabilities_apply_modifier_executor.py:MODIFIER_TYPE_MAP`; `capabilities_delete_object_executor.py:PROTECTED_CATEGORIES`; `capabilities_get_object_info_executor.py:DETAIL_LEVELS` | Move stable catalog data to `taxonomy_object_constant.py` or configuration-backed taxonomy constants. Keep capabilities focused on execution. |
| 5 | 🟡 WARNING | Several VOs are missing typed fields required by the FRD, causing capabilities to use `getattr()` and ad-hoc defaults. Examples: `SetMaterialVO` lacks PBR fields; `ApplyModifierVO` lacks modifier parameters; `GetObjectInfoVO` detail level is output-oriented but not clearly input-controlled; transform mode and child/dependent deletion policy are not strongly modeled. | `modules/shared/src/object/taxonomy_object_vo.py:SetMaterialVO`; `ApplyModifierVO`; `GetObjectInfoVO`; `SetObjectTransformVO`; `DeleteObjectVO` | Add typed VO fields using branded/taxonomy types, e.g. `ColorRGBA`, `NormalizedFactor`, `ModifierParameters`, `TransformMode`, `ChildDeletionPolicy`. Validate in `__post_init__` where appropriate. |
| 6 | 🟢 INFO | Primitive and modifier catalogs include entries that may not be valid Blender enums or may be runtime-version dependent. | `capabilities_create_primitive_executor.py:PRIMITIVE_OPS_MAP`; `capabilities_apply_modifier_executor.py:MODIFIER_TYPE_MAP` | Validate against supported Blender versions and externalize version-specific catalogs to constants/config. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `GetObjectInfoExecutor._generate_info_code()` generates invalid Python: an `if` statement is inserted inside a dictionary literal before the dictionary is closed. This will fail at runtime for FR-OBJ-007. | `modules/object/src/capabilities_get_object_info_executor.py:_generate_info_code` | Close the dictionary literal before conditional mesh-statistics enrichment. See proposed fix below. |
| 2 | 🔴 CRITICAL | `CreatePrimitiveExecutor._resolve_name()` interpolates `base_name` directly into generated Python code without escaping. This is a code-injection risk and can also produce invalid code when names contain quotes. | `modules/object/src/capabilities_create_primitive_executor.py:_resolve_name` | Use `repr()`/shared safe-quoting utility for all user-provided strings embedded in generated Blender code. |
| 3 | 🔴 CRITICAL | `SetMaterialExecutor` validates PBR properties but the generated Blender code never applies `base_color`, `metallic`, `roughness`, or `alpha`. FR-OBJ-004 is therefore not functionally satisfied. | `modules/object/src/capabilities_set_material_executor.py:_generate_material_code` | Generate Principled BSDF node assignments for PBR properties. Add missing VO fields first. |
| 4 | 🟡 WARNING | `PlaceAssetExecutor._resolve_object()` can return the original request name instead of the resolved Blender object name. The fallback match logic also does not return the first unambiguous match. | `modules/object/src/capabilities_place_asset_executor.py:_resolve_object` | Return the actual resolved name from Blender execution result. Implement deterministic resolution: unique ID → exact name → qualified path/collection. |
| 5 | 🟡 WARNING | `CreatePrimitiveExecutor._resolve_name()` uses an incorrect existence-check query. It builds a set of booleans for suffixed names, does not map suffixes correctly, and does not check whether the base name itself already exists. | `modules/object/src/capabilities_create_primitive_executor.py:_resolve_name` | Generate code that checks the base name and iteratively finds the first unused candidate name. Return that candidate as `result`. |
| 6 | 🟡 WARNING | `SetTransformExecutor._check_locked_channels_code()` rejects the operation if any transform channel is locked, even when the request does not modify that channel. It also raises generic `ValueError` instead of taxonomy `TransformLockError`. | `modules/object/src/capabilities_set_transform_executor.py:_check_locked_channels_code` | Check only the channels being modified. Map Blender-side lock violations to `TransformLockError` in the capability. |
| 7 | 🟡 WARNING | `DeleteObjectExecutor.delete_object()` catches `BaseException` and converts broad execution failures into `ObjectNotFoundError`, potentially masking real execution errors. | `modules/object/src/capabilities_delete_object_executor.py:delete_object` | Catch `Exception` only where appropriate, re-raise taxonomy errors directly, and preserve underlying execution errors as `ExecutionError` or another domain error. |
| 8 | 🟡 WARNING | `DeleteObjectExecutor._generate_deletion_code()` uses `obj.children_objects`, which is not a Blender API attribute. The correct relationship accessor is `obj.children`. Child policy handling is also incomplete. | `modules/object/src/capabilities_delete_object_executor.py:_generate_deletion_code` | Use `obj.children`. Model child/dependent handling policies explicitly in `DeleteObjectVO` and implement delete-hierarchy/detach/reject behavior. |
| 9 | 🟡 WARNING | `ApplyModifierExecutor._generate_modifier_code()` uses `getattr(request, 'parameters', {})` and embeds `str(dict)` into generated code. `ApplyModifierVO` has no `parameters` field, and the generated parameter assignment is unsafe/invalid. | `modules/object/src/capabilities_apply_modifier_executor.py:_generate_modifier_code` | Add a typed `parameters` field to `ApplyModifierVO`, validate modifier parameters in the capability, and generate safe parameter assignment code. |
| 10 | 🟡 WARNING | `GetObjectInfoExecutor._generate_info_code()` assumes `obj.data.materials` exists for all object types and always reads Euler rotation. This can fail for non-mesh objects or objects using non-Euler rotation modes. | `modules/object/src/capabilities_get_object_info_executor.py:_generate_info_code` | Guard material access with `getattr(obj.data, 'materials', [])`, and handle rotation mode explicitly or return raw rotation mode metadata. |

## Violations
- **AES102 — Suffix/Prefix Rules**: `taxonomy_object_error_vo.py` uses `_vo` suffix but contains error classes. It should use `_error`.
- **AES305 — Duplication Code**: `_safe_str()`, `_tuple_str()`, and `_validate_scale()` are duplicated across multiple capability executors.
- **AES401 — Taxonomy Role**: `taxonomy_object_error_vo.py` error classes store primitive-typed fields such as `str` and `list[str]` directly. Error taxonomy fields should use taxonomy VOs/branded types.
- **AES405 — Agent Role**: `agent_object_orchestrator.py` uses `Any` for `import_export_cap` and `import_export_capability`. Agent code should use concrete contract types.
- **Potential AES503/AES505 risk**: `import_export_cap` is wired as an optional capability but is not consumed by the aggregate contract. If unused, it should be removed; if used, it must be formally wired and contract-defined.
- **No confirmed AES201 forbidden-import violations detected** in the provided object-feature snapshot.

## Action Items (For Developer)
- [ ] P0 Rename `modules/shared/src/object/taxonomy_object_error_vo.py` to `taxonomy_object_error.py` and update all imports.
- [ ] P0 Fix `GetObjectInfoExecutor._generate_info_code()` so generated Blender Python is syntactically valid.
- [ ] P0 Fix `CreatePrimitiveExecutor._resolve_name()` to escape user-provided names and correctly resolve unique names.
- [ ] P0 Implement actual PBR property assignment in `SetMaterialExecutor._generate_material_code()`.
- [ ] P1 Introduce a shared `ICodeExecutionProtocol` contract and replace all `code_executor: Any`/`object` annotations with the protocol type.
- [ ] P1 Extract duplicated code-generation and validation helpers into a shared utility module.
- [ ] P1 Move primitive/modifier/catalog constants into `taxonomy_object_constant.py` or configuration-backed taxonomy constants.
- [ ] P1 Add missing VO fields required by the FRD: material PBR properties, modifier parameters, transform mode, detail level input, deletion child/dependent policy, confirmation flags.
- [ ] P1 Replace primitive fields in object error classes with taxonomy/branded VO types.
- [ ] P1 Fix deterministic object resolution in `PlaceAssetExecutor`.
- [ ] P1 Fix locked-transform-channel handling to only reject modified locked channels and map failures to `TransformLockError`.
- [ ] P1 Fix delete-object child handling using `obj.children` and explicit policy behavior.
- [ ] P2 Remove unused constants, unused properties, and dead optional import wiring.
- [ ] P2 Validate primitive/modifier catalogs against supported Blender versions.

## Proposed Fixes / Reference Code

### File: `modules/shared/src/object/taxonomy_object_error.py`
Rename from `taxonomy_object_error_vo.py` and use taxonomy-typed fields.

```python
"""Object domain errors — typed exceptions for object operation failures."""

from __future__ import annotations

from ..common.taxonomy_core_vo import ErrorString, ObjectName
from ..common.taxonomy_domain_error import DomainError


class ObjectAmbiguityError(DomainError):
    """Raised when an object reference resolves to multiple matching objects."""

    def __init__(self, reference: ObjectName, matches: list[ObjectName]) -> None:
        super().__init__(ErrorString(f"Ambiguous object reference '{reference}': {len(matches)} matches"))
        self.reference = reference
        self.matches = matches


class ObjectNotFoundError(DomainError):
    """Raised when a requested object does not exist in the scene."""

    def __init__(self, reference: ObjectName) -> None:
        super().__init__(ErrorString(f"Object '{reference}' not found in scene"))
        self.reference = reference


class TransformLockError(DomainError):
    """Raised when attempting to modify a locked transform channel."""

    def __init__(self, channel: str) -> None:
        super().__init__(ErrorString(f"Transform channel '{channel}' is locked"))
        self.channel = channel
```

### File: `modules/shared/src/common/taxonomy_core_vo.py`
Add stronger branded types for object/material PBR values.

```python
# Suggested additions
ColorRGBA = NewType("ColorRGBA", tuple[float, float, float, float])
NormalizedFactor = NewType("NormalizedFactor", float)
TransformMode = NewType("TransformMode", str)
DetailLevel = NewType("DetailLevel", str)
ModifierParameters = NewType("ModifierParameters", dict[str, Any])
ChildDeletionPolicy = NewType("ChildDeletionPolicy", str)
```

### File: `modules/shared/src/object/taxonomy_object_vo.py`
Add missing FRD-required fields and use stronger types.

```python
from ..common.taxonomy_core_vo import (
    AssetId,
    ColorRGBA,
    CoordinateList,
    DetailLevel,
    MaterialName,
    ModifierName,
    ModifierParameters,
    NormalizedFactor,
    ObjectCount,
    ObjectName,
    ObjectType,
    PrimitiveType,
    RotationVector,
    ScaleVector,
    SuccessFlag,
    TransformMode,
)


@dataclass(frozen=True)
class SetMaterialVO:
    """Set material — input and output in one VO."""

    # Input
    object_name: ObjectName
    material_name: MaterialName
    base_color: ColorRGBA | None = None
    metallic: NormalizedFactor | None = None
    roughness: NormalizedFactor | None = None
    alpha: NormalizedFactor | None = None
    slot_index: int | None = None

    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""


@dataclass(frozen=True)
class ApplyModifierVO:
    """Apply modifier — input and output in one VO."""

    # Input
    object_name: ObjectName
    modifier_name: ModifierName
    action: str = "add"
    confirmation: bool = False
    parameters: ModifierParameters | None = None

    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    modifier_type: ObjectType = field(default_factory=lambda: ObjectType(""))
    applied_destructively: SuccessFlag = field(default=SuccessFlag(False))
    message: str = ""


@dataclass(frozen=True)
class GetObjectInfoVO:
    """Get object info — input and output in one VO."""

    # Input
    object_name: ObjectName
    detail_level: DetailLevel = field(default_factory=lambda: DetailLevel("full"))

    # Output
    success: SuccessFlag = field(default=SuccessFlag(False))
    object_type: ObjectType | None = None
    location: CoordinateList | None = None
    rotation: RotationVector | None = None
    scale: ScaleVector | None = None
    parent_name: ObjectName | None = None
    collection_names: list[ObjectName] = field(default_factory=list)
    material_names: list[MaterialName] = field(default_factory=list)
    modifier_summaries: list[dict[str, Any]] = field(default_factory=list)
    visibility: bool = True
    message: str = ""
```

### File: `modules/shared/src/common/utility_code_builder.py`
Extract shared code-generation helpers. Utility must remain stateless and depend only on taxonomy/stdlib.

```python
"""Stateless helpers for safely building generated Python code."""

from __future__ import annotations

import math

from .taxonomy_core_vo import CoordinateList, ScaleVector


def quote_string(value: str) -> str:
    """Safely embed a string into generated Python code."""
    return repr(value)


def tuple_str(coords: CoordinateList) -> str:
    """Format a 3-element sequence of floats for generated Python code."""
    return f"({coords[0]}, {coords[1]}, {coords[2]})"


def validate_finite_vector(vector: CoordinateList, field_name: str) -> None:
    """Validate that all vector components are finite numeric values."""
    for index, value in enumerate(vector):
        if not isinstance(value, (int, float)):
            raise ValueError(f"{field_name}[{index}] is not numeric: {value}")
        if not math.isfinite(float(value)):
            raise ValueError(f"{field_name}[{index}] is not finite: {value}")


def validate_scale(scale: ScaleVector) -> None:
    """Validate scale values are finite and non-zero."""
    for index, value in enumerate(scale):
        if not isinstance(value, (int, float)):
            raise ValueError(f"Scale component {index} is not numeric: {value}")
        if not math.isfinite(float(value)):
            raise ValueError(f"Scale component {index} is not finite: {value}")
        if value == 0:
            raise ValueError(f"Scale component {index} is zero — non-zero scale is required")
```

### File: `modules/object/src/capabilities_get_object_info_executor.py`
Fix invalid generated Python.

```python
def _generate_info_code(self, request: GetObjectInfoVO) -> str:
    lines = [
        "import bpy",
        f"obj = bpy.data.objects.get({quote_string(str(request.object_name))})",
        'if obj is None:\n    raise ValueError("Object not found in scene.")',
        "info = {",
        "    'name': obj.name,",
        "    'type': obj.type,",
        "    'location': [obj.location.x, obj.location.y, obj.location.z],",
        "    'rotation': [obj.rotation_euler[0], obj.rotation_euler[1], obj.rotation_euler[2]],",
        "    'scale': [obj.scale.x, obj.scale.y, obj.scale.z],",
        "    'parent_name': obj.parent.name if obj.parent else None,",
        "    'collection_names': [col.name for col in obj.users_collection],",
        "    'material_names': [mat.name for mat in getattr(obj.data, 'materials', []) if mat],",
        "    'modifier_summaries': [{'name': mod.name, 'type': mod.type} for mod in obj.modifiers],",
        "    'visibility': obj.visible_get(),",
        "    'mesh_statistics': None,",
        "}",
        "if obj.type == 'MESH' and obj.data:",
        "    mesh = obj.data",
        "    info['mesh_statistics'] = {",
        "        'vertex_count': len(mesh.vertices),",
        "        'edge_count': len(mesh.edges),",
        "        'face_count': len(mesh.polygons),",
        "    }",
        "result = info",
    ]
    return "\n".join(lines)
```

### File: `modules/object/src/capabilities_create_primitive_executor.py`
Fix unsafe name interpolation and incorrect uniqueness logic.

```python
async def _resolve_name(self, request: CreatePrimitiveVO) -> str:
    if not request.name:
        return f"Primitive_{id(request)}"

    base_name = str(request.name)
    check_code = (
        "import bpy\n"
        f"base = {quote_string(base_name)}\n"
        "existing = set(bpy.data.objects.keys())\n"
        "candidate = base\n"
        "suffix = 1\n"
        "while candidate in existing:\n"
        "    candidate = f'{base}.{suffix:03d}'\n"
        "    suffix += 1\n"
        "result = candidate\n"
    )

    resolved = await self._executor.execute_blender_code(Prompt(check_code))
    return str(resolved)
```

### File: `modules/object/src/capabilities_set_material_executor.py`
Apply PBR properties in generated Blender code.

```python
def _generate_material_code(self, request: SetMaterialVO) -> str:
    lines = [
        "import bpy",
        f"obj = bpy.data.objects.get({quote_string(str(request.object_name))})",
        'if obj is None:\n    raise ValueError("Object not found in scene.")',
        'if obj.type != "MESH":\n    raise ValueError(f"Object {obj.name!r} is not a mesh; cannot set material.")',
        f"mat = bpy.data.materials.get({quote_string(str(request.material_name))})",
        "if not mat:",
        f"    mat = bpy.data.materials.new(name={quote_string(str(request.material_name))})",
        "mat.use_nodes = True",
        "bsdf = mat.node_tree.nodes.get('Principled BSDF')",
    ]

    if request.base_color is not None:
        lines.append(f"if bsdf:\n    bsdf.inputs['Base Color'].default_value = {tuple(request.base_color)}")

    if request.metallic is not None:
        lines.append(f"if bsdf:\n    bsdf.inputs['Metallic'].default_value = {float(request.metallic)}")

    if request.roughness is not None:
        lines.append(f"if bsdf:\n    bsdf.inputs['Roughness'].default_value = {float(request.roughness)}")

    if request.alpha is not None:
        lines.append(f"if bsdf:\n    bsdf.inputs['Alpha'].default_value = {float(request.alpha)}")

    lines.extend(
        [
            "if len(obj.data.materials) == 0:",
            "    obj.data.materials.append(mat)",
            "else:",
            "    obj.data.materials[0] = mat",
        ]
    )

    return "\n".join(lines)
```

### File: `modules/object/src/capabilities_delete_object_executor.py`
Use correct Blender child accessor and avoid broad exception masking.

```python
# In generated deletion code:
lines.append(
    "# Detach children before removal; replace with policy-driven behavior later\n"
    "for child in obj.children:\n"
    "    child.parent = None\n"
)
```

```python
# In delete_object(): replace BaseException handling with narrower handling.
except ObjectNotFoundError:
    raise
except ValueError as e:
    if getattr(request, "idempotent", False):
        return DeleteObjectVO(
            object_name=request.object_name,
            success=SuccessFlag(True),
            deleted_count=0,
            deleted_names=[],
            message="Object not found — idempotent deletion policy enabled",
        )
    raise ObjectNotFoundError(request.object_name) from e
except Exception as e:
    logger.error("Existence check failed for object %s: %s", request.object_name, e)
    raise
```

### File: `modules/object/src/agent_object_orchestrator.py`
Remove `Any` usage or replace with concrete protocol.

```python
# Preferred if a shared import/export protocol exists:
from modules.shared.src.asset.contract_import_export_protocol import (
    IImportExportProtocol,
)


def __init__(
    self,
    place_asset_cap: PlaceAssetProtocol,
    create_primitive_cap: CreatePrimitiveProtocol,
    set_transform_cap: SetObjectTransformProtocol,
    set_material_cap: SetMaterialProtocol,
    apply_modifier_cap: ApplyModifierProtocol,
    delete_object_cap: DeleteObjectProtocol,
    get_object_info_cap: GetObjectInfoProtocol,
    import_export_cap: IImportExportProtocol | None = None,
) -> None: ...
```

```python
# If no formal import/export contract is used by the object aggregate, remove it:
def __init__(
    self,
    place_asset_cap: PlaceAssetProtocol,
    create_primitive_cap: CreatePrimitiveProtocol,
    set_transform_cap: SetObjectTransformProtocol,
    set_material_cap: SetMaterialProtocol,
    apply_modifier_cap: ApplyModifierProtocol,
    delete_object_cap: DeleteObjectProtocol,
    get_object_info_cap: GetObjectInfoProtocol,
) -> None: ...
```

### File: `modules/object/src/root_object_container.py`
Inject cross-module capabilities from a higher-level root instead of importing them inside the object container.

```python
class ObjectContainer:
    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        import_export_cap: IImportExportProtocol | None = None,
    ) -> None:
        self._code_executor = code_executor
        self._import_export_cap = import_export_cap
        self._orchestrator: ObjectOrchestrator | None = None
        self._wired: bool = False
```

```python
# If import/export is not part of object FRD scope, remove it entirely:
self._orchestrator = ObjectOrchestrator(
    place_asset_cap=place_asset_cap,
    create_primitive_cap=create_primitive_cap,
    set_transform_cap=set_transform_cap,
    set_material_cap=set_material_cap,
    apply_modifier_cap=apply_modifier_cap,
    delete_object_cap=delete_object_cap,
    get_object_info_cap=get_object_info_cap,
)
```