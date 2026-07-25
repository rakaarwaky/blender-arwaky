"""Agent: Object feature orchestrator.

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
from modules.shared.src.object.contract_object_operate_aggregate import ObjectOperateAggregate
from modules.shared.src.object.contract_place_asset_protocol import PlaceAssetProtocol
from modules.shared.src.object.contract_set_material_protocol import SetMaterialProtocol
from modules.shared.src.object.contract_set_transform_protocol import SetObjectTransformProtocol
from modules.shared.src.object.taxonomy_object_request_vo import (
    ApplyModifierRequestVO,
    CreatePrimitiveRequestVO,
    DeleteObjectRequestVO,
    GetObjectInfoRequestVO,
    PlaceAssetRequestVO,
    SetMaterialRequestVO,
    SetObjectTransformRequestVO,
)
from modules.shared.src.object.taxonomy_object_result_vo import (
    CreationResultVO,
    DeletionResultVO,
    MaterialResultVO,
    ModifierResultVO,
    ObjectInfoResultVO,
    PlacementResultVO,
    TransformResultVO,
)

logger = logging.getLogger("BlenderMCPServer")


class ObjectOrchestrator(ObjectOperateAggregate):
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
    ) -> None:
        self._place_asset = place_asset_cap
        self._create_primitive = create_primitive_cap
        self._set_transform = set_transform_cap
        self._set_material = set_material_cap
        self._apply_modifier = apply_modifier_cap
        self._delete_object = delete_object_cap
        self._get_object_info = get_object_info_cap

    # ─── Block 2: Aggregate Implementation ───────────────────

    async def place_asset(self, request: PlaceAssetRequestVO) -> PlacementResultVO:
        """Delegate asset placement to the capabilities layer."""
        logger.info("Orchestrating place_asset for %s", request.asset_id)
        return await self._place_asset.place_asset(request)

    async def create_primitive(self, request: CreatePrimitiveRequestVO) -> CreationResultVO:
        """Delegate primitive creation to the capabilities layer."""
        logger.info("Orchestrating create_primitive: %s", request.primitive_type)
        return await self._create_primitive.create_primitive(request)

    async def set_object_transform(
        self, request: SetObjectTransformRequestVO
    ) -> TransformResultVO:
        """Delegate transform update to the capabilities layer."""
        logger.info("Orchestrating set_object_transform for %s", request.object_name)
        return await self._set_transform.set_object_transform(request)

    async def set_material(self, request: SetMaterialRequestVO) -> MaterialResultVO:
        """Delegate material assignment to the capabilities layer."""
        logger.info("Orchestrating set_material for %s", request.object_name)
        return await self._set_material.set_material(request)

    async def apply_modifier(self, request: ApplyModifierRequestVO) -> ModifierResultVO:
        """Delegate modifier operation to the capabilities layer."""
        logger.info("Orchestrating apply_modifier for %s", request.modifier_name)
        return await self._apply_modifier.apply_modifier(request)

    async def delete_object(self, request: DeleteObjectRequestVO) -> DeletionResultVO:
        """Delegate object deletion to the capabilities layer."""
        logger.info("Orchestrating delete_object for %s", request.object_name)
        return await self._delete_object.delete_object(request)

    async def get_object_info(
        self, request: GetObjectInfoRequestVO
    ) -> ObjectInfoResultVO:
        """Delegate object info retrieval to the capabilities layer."""
        logger.info("Orchestrating get_object_info for %s", request.object_name)
        return await self._get_object_info.get_object_info(request)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @property
    def object_operate_capability(self) -> ObjectOperateAggregate:
        """Expose self as the object operate capability facade for dispatch.

        The orchestrator implements ObjectOperateAggregate, so all 7 methods
        are available through this property. This allows the action dispatcher
        to resolve ObjectOperateProtocol → object_operate_capability on the
        orchestrator and then call individual methods like place_asset().
        """
        return self

    def __repr__(self) -> str:
        return "ObjectOrchestrator()"
