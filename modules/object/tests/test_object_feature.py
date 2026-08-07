"""End-to-end capability tests for the object feature (FRD FR-OBJ-001..007).

Exercises all 7 object capabilities through a mocked Blender code executor and
verifies FRD business rules hold. Run via pytest from repo root.

All aggregate/capability methods are ``async def``; with ``asyncio_mode = "auto"``
in pyproject.toml, async test functions are awaited automatically.

The Blender side is replaced by :class:`FakeBlenderExecutor`, which records the
generated code and returns scripted responses (or raises) so the pure-Python
business logic and VO construction can be verified without a live Blender.
"""

from __future__ import annotations

from typing import Any

from modules.object.src.capabilities_apply_modifier_executor import ApplyModifierExecutor
from modules.object.src.capabilities_create_primitive_executor import CreatePrimitiveExecutor
from modules.object.src.capabilities_delete_object_executor import DeleteObjectExecutor
from modules.object.src.capabilities_get_object_info_executor import GetObjectInfoExecutor
from modules.object.src.capabilities_place_asset_executor import PlaceAssetExecutor
from modules.object.src.capabilities_set_material_executor import SetMaterialExecutor
from modules.object.src.capabilities_set_transform_executor import SetTransformExecutor
from modules.object.src.root_object_container import ObjectContainer
from modules.shared.src.common.taxonomy_core_vo import (
    CoordinateList,
    ObjectName,
    PrimitiveType,
    Prompt,
    ScaleVector,
)
from modules.shared.src.object.contract_object_aggregate import IObjectAggregate
from modules.shared.src.object.taxonomy_object_error import (
    DeletionProtectionError,
    InvalidModifierTypeError,
    InvalidPrimitiveTypeError,
    ModifierActionConfirmationError,
    ObjectAmbiguityError,
    ObjectNotFoundError,
)
from modules.shared.src.object.taxonomy_object_vo import (
    ApplyModifierVO,
    CreatePrimitiveVO,
    DeleteObjectVO,
    GetObjectInfoVO,
    PlaceAssetVO,
    SetMaterialVO,
    SetObjectTransformVO,
)


class FakeBlenderExecutor:
    """Mock ICodeExecutionProtocol.

    ``responses`` is a FIFO queue; each entry is either a value to return or an
    Exception instance to raise. When the queue is empty, returns ``True``.
    """

    def __init__(self, responses: list[Any] | None = None) -> None:
        self._responses = list(responses or [])
        self.calls: list[Prompt] = []

    async def execute_blender_code(self, prompt: Prompt) -> Any:
        self.calls.append(prompt)
        resp = self._responses.pop(0) if self._responses else True
        if isinstance(resp, Exception):
            raise resp
        return resp


# ─── FR-OBJ-001: Place Existing Object ──────────────────────────────────────


async def test_fr_obj_001_places_existing_object_at_target_transform():
    ex = FakeBlenderExecutor()
    cap = PlaceAssetExecutor(ex)
    res = await cap.place_asset(
        PlaceAssetVO(
            asset_id="asset_1",
            object_name=ObjectName("Cube"),
            location=CoordinateList([1.0, 2.0, 3.0]),
            scale=ScaleVector([1.0, 1.0, 1.0]),
        )
    )
    assert res.success is True
    assert res.object_name == "Cube"
    # Blender placement code must have been generated and executed
    assert len(ex.calls) >= 2  # resolve + place


async def test_fr_obj_001_ambiguous_reference_raises_ambiguity_error():
    # Executor reports two matching objects -> ambiguity
    ex = FakeBlenderExecutor(responses=[{"matches": ["Cube.001", "Cube.002"]}])
    cap = PlaceAssetExecutor(ex)
    try:
        await cap.place_asset(PlaceAssetVO(asset_id="asset_1", object_name=ObjectName("Cube")))
        raise AssertionError("expected ObjectAmbiguityError")
    except ObjectAmbiguityError as e:
        assert len(e.matches) == 2


async def test_fr_obj_001_zero_scale_rejected_with_validation_error():
    # FR-OBJ-001: zero scale components are rejected (unless policy allows)
    ex = FakeBlenderExecutor()
    cap = PlaceAssetExecutor(ex)
    try:
        await cap.place_asset(
            PlaceAssetVO(
                asset_id="asset_1",
                object_name=ObjectName("Cube"),
                scale=ScaleVector([0.0, 1.0, 1.0]),
            )
        )
        raise AssertionError("expected ValueError for zero scale")
    except ValueError:
        pass


async def test_fr_obj_001_object_not_found_raises():
    # FR-OBJ-001: object not found should raise ObjectNotFoundError
    # Need two ValueError responses: one for initial get, one for fallback pattern match
    ex = FakeBlenderExecutor(responses=[ValueError("Object not found in scene."), ValueError("Object not found in scene.")])
    cap = PlaceAssetExecutor(ex)
    try:
        await cap.place_asset(PlaceAssetVO(asset_id="asset_1", object_name=ObjectName("Missing")))
        raise AssertionError("expected ObjectNotFoundError")
    except ObjectNotFoundError:
        pass


async def test_fr_obj_001_place_with_rotation():
    # FR-OBJ-001: placement code should include rotation when provided
    # Need two responses: one for existence check, one for place code execution
    ex = FakeBlenderExecutor(responses=[True, True])
    cap = PlaceAssetExecutor(ex)
    res = await cap.place_asset(
        PlaceAssetVO(
            asset_id="asset_1",
            object_name=ObjectName("Cube"),
            location=CoordinateList([1.0, 2.0, 3.0]),
            rotation=CoordinateList([0.0, 0.0, 1.57]),
            scale=ScaleVector([1.0, 1.0, 1.0]),
        )
    )
    assert res.success is True
    # First call is resolve, second call is placement code with rotation
    code = str(ex.calls[1])
    assert "rotation_euler" in code


async def test_fr_obj_001_no_selected_objects_raises():
    # FR-OBJ-001: no object_name and no selected objects should raise ObjectNotFoundError
    ex = FakeBlenderExecutor(responses=[])  # Empty responses queue -> returns True, but we need to simulate no selection
    cap = PlaceAssetExecutor(ex)
    try:
        await cap.place_asset(PlaceAssetVO(asset_id="asset_1"))  # No object_name
        raise AssertionError("expected ObjectNotFoundError")
    except ObjectNotFoundError:
        pass


# ─── FR-OBJ-002: Create Primitive ───────────────────────────────────────────


def test_fr_obj_002_resolves_supported_primitive_op():
    assert CreatePrimitiveExecutor._resolve_primitive_op("sphere") == "bpy.ops.mesh.primitive_uv_sphere_add"
    assert CreatePrimitiveExecutor._resolve_primitive_op("camera") == "bpy.ops.object.camera_add"
    # Enum-style strings are normalized
    assert (
        CreatePrimitiveExecutor._resolve_primitive_op("primitivetype.sphere") == "bpy.ops.mesh.primitive_uv_sphere_add"
    )


def test_fr_obj_002_rejects_unsupported_primitive_type():
    assert CreatePrimitiveExecutor._resolve_primitive_op("not_a_thing") is None


async def test_fr_obj_002_create_primitive_returns_resolved_reference():
    ex = FakeBlenderExecutor(responses=["MySphere"])
    cap = CreatePrimitiveExecutor(ex)
    res = await cap.create_primitive(
        CreatePrimitiveVO(primitive_type=PrimitiveType("sphere"), name=ObjectName("MySphere"))
    )
    assert res.success is True
    assert res.object_name == "MySphere"
    assert len(ex.calls) == 2  # name existence check + creation code


async def test_fr_obj_002_invalid_primitive_type_raises():
    ex = FakeBlenderExecutor()
    cap = CreatePrimitiveExecutor(ex)
    try:
        await cap.create_primitive(CreatePrimitiveVO(primitive_type=PrimitiveType("bogus")))
        raise AssertionError("expected InvalidPrimitiveTypeError")
    except InvalidPrimitiveTypeError:
        pass


# ─── FR-OBJ-003: Set Transform ──────────────────────────────────────────────


async def test_fr_obj_003_sets_provided_transform_components():
    ex = FakeBlenderExecutor()
    cap = SetTransformExecutor(ex)
    res = await cap.set_object_transform(
        SetObjectTransformVO(
            object_name=ObjectName("Cube"),
            location=CoordinateList([1.0, 0.0, 0.0]),
            scale=ScaleVector([1.0, 1.0, 1.0]),
        )
    )
    assert res.success is True
    # Generated code sets location and scale but not rotation (omitted preserved)
    code = str(ex.calls[0])
    assert "obj.location =" in code
    assert "obj.scale =" in code


async def test_fr_obj_003_zero_scale_rejected_with_validation_error():
    # FR-OBJ-003: scale values must be finite and non-zero
    ex = FakeBlenderExecutor()
    cap = SetTransformExecutor(ex)
    try:
        await cap.set_object_transform(
            SetObjectTransformVO(
                object_name=ObjectName("Cube"),
                scale=ScaleVector([1.0, 0.0, 1.0]),
            )
        )
        raise AssertionError("expected ValueError for zero scale")
    except ValueError:
        pass


async def test_fr_obj_003_non_numeric_scale_rejected():
    ex = FakeBlenderExecutor()
    cap = SetTransformExecutor(ex)
    try:
        await cap.set_object_transform(
            SetObjectTransformVO(
                object_name=ObjectName("Cube"),
                scale=ScaleVector(["x", 1.0, 1.0]),  # type: ignore[arg-type]
            )
        )
        raise AssertionError("expected ValueError for non-numeric scale")
    except ValueError:
        pass


async def test_fr_obj_003_rotation_only_transform():
    # FR-OBJ-003: setting rotation only should not include location or scale in generated code
    ex = FakeBlenderExecutor()
    cap = SetTransformExecutor(ex)
    res = await cap.set_object_transform(
        SetObjectTransformVO(
            object_name=ObjectName("Cube"),
            rotation=CoordinateList([0.0, 0.0, 1.57]),
        )
    )
    assert res.success is True
    code = str(ex.calls[0])
    assert "rotation_euler" in code
    assert "obj.location =" not in code
    assert "obj.scale =" not in code


# ─── FR-OBJ-004: Set Material ───────────────────────────────────────────────


async def test_fr_obj_004_assigns_or_creates_material():
    ex = FakeBlenderExecutor()
    cap = SetMaterialExecutor(ex)
    res = await cap.set_material(SetMaterialVO(object_name=ObjectName("Cube"), material_name="RedMetal"))
    assert res.success is True
    assert res.material_name == "RedMetal"
    # Generated code creates the material when missing and assigns to a slot
    code = str(ex.calls[0])
    assert "bpy.data.materials.new" in code


# ─── FR-OBJ-005: Manage Modifiers ───────────────────────────────────────────


async def test_fr_obj_005_rejects_invalid_modifier_action():
    ex = FakeBlenderExecutor()
    cap = ApplyModifierExecutor(ex)
    import pytest

    with pytest.raises(ValueError):
        await cap.apply_modifier(
            ApplyModifierVO(object_name=ObjectName("Cube"), modifier_name="subsurf", action="explode")
        )


async def test_fr_obj_005_destructive_apply_requires_confirmation():
    ex = FakeBlenderExecutor()
    cap = ApplyModifierExecutor(ex)
    try:
        await cap.apply_modifier(
            ApplyModifierVO(object_name=ObjectName("Cube"), modifier_name="subsurf", action="apply")
        )
        raise AssertionError("expected ModifierActionConfirmationError")
    except ModifierActionConfirmationError:
        pass


async def test_fr_obj_005_invalid_modifier_type_raises():
    ex = FakeBlenderExecutor()
    cap = ApplyModifierExecutor(ex)
    try:
        await cap.apply_modifier(
            ApplyModifierVO(
                object_name=ObjectName("Cube"),
                modifier_name="not_real",
                action="add",
            )
        )
        raise AssertionError("expected InvalidModifierTypeError")
    except InvalidModifierTypeError:
        pass


async def test_fr_obj_005_add_modifier_succeeds():
    ex = FakeBlenderExecutor()
    cap = ApplyModifierExecutor(ex)
    res = await cap.apply_modifier(
        ApplyModifierVO(object_name=ObjectName("Cube"), modifier_name="subsurf", action="add")
    )
    assert res.success is True
    assert res.modifier_type == "SUBSURF"
    assert res.applied_destructively is False


async def test_fr_obj_005_remove_modifier_succeeds():
    # FR-OBJ-005: remove action should succeed without confirmation
    ex = FakeBlenderExecutor()
    cap = ApplyModifierExecutor(ex)
    res = await cap.apply_modifier(
        ApplyModifierVO(object_name=ObjectName("Cube"), modifier_name="subsurf", action="remove")
    )
    assert res.success is True
    assert res.modifier_type == "SUBSURF"
    assert res.applied_destructively is False


async def test_fr_obj_005_update_modifier_succeeds():
    # FR-OBJ-005: update action should succeed without confirmation
    ex = FakeBlenderExecutor()
    cap = ApplyModifierExecutor(ex)
    res = await cap.apply_modifier(
        ApplyModifierVO(object_name=ObjectName("Cube"), modifier_name="subsurf", action="update")
    )
    assert res.success is True
    assert res.modifier_type == "SUBSURF"
    assert res.applied_destructively is False


async def test_fr_obj_005_apply_modifier_with_confirmation_succeeds():
    # FR-OBJ-005: apply with confirmation should succeed
    ex = FakeBlenderExecutor()
    cap = ApplyModifierExecutor(ex)
    res = await cap.apply_modifier(
        ApplyModifierVO(
            object_name=ObjectName("Cube"),
            modifier_name="subsurf",
            action="apply",
            confirmation=True,
        )
    )
    assert res.success is True
    assert res.applied_destructively is True


# ─── FR-OBJ-006: Delete Object ──────────────────────────────────────────────


async def test_fr_obj_006_deletes_existing_object():
    # exists-check True, protected-check False
    ex = FakeBlenderExecutor(responses=[True, False])
    cap = DeleteObjectExecutor(ex)
    res = await cap.delete_object(DeleteObjectVO(object_name=ObjectName("Cube")))
    assert res.success is True
    assert res.deleted_count == 1
    assert res.deleted_names == ["Cube"]


async def test_fr_obj_006_idempotent_deletion_returns_success_when_missing():
    # exists-check raises -> idempotent policy returns success
    ex = FakeBlenderExecutor(responses=[ValueError("not found")])
    cap = DeleteObjectExecutor(ex)
    res = await cap.delete_object(DeleteObjectVO(object_name=ObjectName("Cube"), idempotent=True))
    assert res.success is True
    assert res.deleted_count == 0


async def test_fr_obj_006_missing_object_without_idempotent_raises_not_found():
    ex = FakeBlenderExecutor(responses=[ValueError("not found")])
    cap = DeleteObjectExecutor(ex)
    try:
        await cap.delete_object(DeleteObjectVO(object_name=ObjectName("Cube")))
        raise AssertionError("expected ObjectNotFoundError")
    except ObjectNotFoundError:
        pass


async def test_fr_obj_006_protected_object_requires_confirmation():
    # exists True, protected True, no confirmation -> DeletionProtectionError
    ex = FakeBlenderExecutor(responses=[True, True])
    cap = DeleteObjectExecutor(ex)
    try:
        await cap.delete_object(DeleteObjectVO(object_name=ObjectName("Camera")))
        raise AssertionError("expected DeletionProtectionError")
    except DeletionProtectionError:
        pass


# ─── FR-OBJ-007: Get Object Info ────────────────────────────────────────────


async def test_fr_obj_007_returns_parsed_object_state():
    ex = FakeBlenderExecutor(
        responses=[
            {
                "name": "Cube",
                "type": "MESH",
                "location": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0],
                "parent_name": None,
                "collection_names": ["Collection"],
                "material_names": ["Mat"],
                "modifier_summaries": [{"name": "Subsurf", "type": "SUBSURF"}],
                "visibility": True,
            }
        ]
    )
    cap = GetObjectInfoExecutor(ex)
    res = await cap.get_object_info(GetObjectInfoVO(object_name=ObjectName("Cube")))
    assert res.success is True
    assert res.object_type == "MESH"
    assert res.material_names == ["Mat"]
    assert res.modifier_summaries[0]["name"] == "Subsurf"


async def test_fr_obj_007_non_dict_result_returns_basic_info():
    ex = FakeBlenderExecutor(responses=["not a dict"])
    cap = GetObjectInfoExecutor(ex)
    res = await cap.get_object_info(GetObjectInfoVO(object_name=ObjectName("Cube")))
    assert res.success is True
    assert res.object_name == "Cube"


# ─── Composition root smoke test ────────────────────────────────────────────


def test_object_container_wires_aggregate():
    container = ObjectContainer(FakeBlenderExecutor())
    container.wire()
    agg = container.aggregate
    assert isinstance(agg, IObjectAggregate)
