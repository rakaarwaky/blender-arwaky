"""Object feature orchestrator implementing ObjectOperateAggregate.

FR-OBJ-001: Place Existing Object — place_object() validates and places object from file
FR-OBJ-002: Create Primitive — create_primitive() spawns cube/sphere/cylinder/etc.
FR-OBJ-003: Set Transform — set_transform() applies position/rotation/scale to object
FR-OBJ-004: Set Material — set_material() applies material by name to object
FR-OBJ-005: Manage Modifiers — apply_modifier() adds/removes/modifies object modifiers
FR-OBJ-006: Delete Object — delete_object() removes object with protection checks
FR-OBJ-007: Get Object Info — get_object_info() returns object metadata and state

Coordinates object manipulation flows via the ObjectOperateAggregate contract.
Orchestration only — no business logic, depends on individual capability protocols.

Structure:
  1. Constants & imports
  2. ObjectOrchestrator — implements aggregate, delegates to 7 individual protocols
"""

import logging

from modules.shared.src.object.contract_apply_modifier_protocol import ApplyModifierProtocol
from modules.shared.src.object.contract_create_primitive_protocol import CreatePrimitiveProtocol
from modules.shared.src.object.contract_delete_object_protocol import DeleteObjectProtocol
from modules.shared.src.object.contract_get_object_info_protocol import GetObjectInfoProtocol
from modules.shared.src.object.contract_object_operate_aggregate import IObjectOperateAggregate
from modules.shared.src.object.contract_place_asset_protocol import PlaceAssetProtocol
from modules.shared.src.object.contract_set_material_protocol import SetMaterialProtocol
from modules.shared.src.object.contract_set_transform_protocol import SetObjectTransformProtocol
from modules.shared.src.object.taxonomy_object_vo import (
    ApplyModifierVO,
    CreatePrimitiveVO,
    DeleteObjectVO,
    GetObjectInfoVO,
    PlaceAssetVO,
    SetMaterialVO,
    SetObjectTransformVO,
)

logger = logging.getLogger("BlenderMCPServer")


class ObjectOrchestrator(IObjectOperateAggregate):
    """Orchestrates object operations through 7 individual capability protocols."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        place_asset_cap: PlaceAssetProtocol,
        create_primitive_cap: CreatePrimitiveProtocol,
        set_transform_cap: SetObjectTransformProtocol,
        set_material_cap: SetMaterialProtocol,
        apply_modifier_cap: ApplyModifierProtocol,
        delete_object_cap: DeleteObjectProtocol,
        get_object_info_cap: GetObjectInfoProtocol,
        import_export_cap: object | None = None,
    ) -> None:
        self._place_asset = place_asset_cap
        self._create_primitive = create_primitive_cap
        self._set_transform = set_transform_cap
        self._set_material = set_material_cap
        self._apply_modifier = apply_modifier_cap
        self._delete_object = delete_object_cap
        self._get_object_info = get_object_info_cap
        self._import_export_cap = import_export_cap

    # ─── Block 2: Aggregate Implementation ───────────────────

    async def place_asset(self, request: PlaceAssetVO) -> PlaceAssetVO:
        logger.info("Orchestrating place_asset for %s", request.asset_id)
        return await self._place_asset.place_asset(request)

    async def create_primitive(self, request: CreatePrimitiveVO) -> CreatePrimitiveVO:
        logger.info("Orchestrating create_primitive: %s", request.primitive_type)
        return await self._create_primitive.create_primitive(request)

    async def set_object_transform(self, request: SetObjectTransformVO) -> SetObjectTransformVO:
        logger.info("Orchestrating set_object_transform for %s", request.object_name)
        return await self._set_transform.set_object_transform(request)

    async def set_material(self, request: SetMaterialVO) -> SetMaterialVO:
        logger.info("Orchestrating set_material for %s", request.object_name)
        return await self._set_material.set_material(request)

    async def apply_modifier(self, request: ApplyModifierVO) -> ApplyModifierVO:
        logger.info("Orchestrating apply_modifier for %s", request.modifier_name)
        return await self._apply_modifier.apply_modifier(request)

    async def delete_object(self, request: DeleteObjectVO) -> DeleteObjectVO:
        logger.info("Orchestrating delete_object for %s", request.object_name)
        return await self._delete_object.delete_object(request)

    async def get_object_info(self, request: GetObjectInfoVO) -> GetObjectInfoVO:
        logger.info("Orchestrating get_object_info for %s", request.object_name)
        return await self._get_object_info.get_object_info(request)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────

    @property
    def object_operate_capability(self) -> IObjectOperateAggregate:
        return self

    @property
    def import_export_capability(self) -> object:
        return self._import_export_cap

    def __repr__(self) -> str:
        return "ObjectOrchestrator()"
