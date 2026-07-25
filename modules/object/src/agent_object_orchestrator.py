"""Agent: Object feature orchestrator.

Coordinates object manipulation flows via the ObjectOperateAggregate contract.
Orchestration only — no business logic, no direct capability dependencies.
"""

import logging

from modules.shared.src.object.contract_object_operate_aggregate import ObjectOperateAggregate
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
    """Orchestrates object operations through the aggregate contract."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, aggregate: ObjectOperateAggregate) -> None:
        self._aggregate = aggregate

    # ─── Block 2: Aggregate Implementation ───────────────────

    async def place_asset(self, request: PlaceAssetRequestVO) -> PlacementResultVO:
        """Delegate asset placement to the capabilities layer."""
        logger.info("Orchestrating place_asset for %s", request.asset_id)
        return await self._aggregate.place_asset(request)

    async def create_primitive(self, request: CreatePrimitiveRequestVO) -> CreationResultVO:
        """Delegate primitive creation to the capabilities layer."""
        logger.info("Orchestrating create_primitive: %s", request.primitive_type)
        return await self._aggregate.create_primitive(request)

    async def set_object_transform(self, request: SetObjectTransformRequestVO) -> TransformResultVO:
        """Delegate transform update to the capabilities layer."""
        logger.info("Orchestrating set_object_transform for %s", request.object_name)
        return await self._aggregate.set_object_transform(request)

    async def set_material(self, request: SetMaterialRequestVO) -> MaterialResultVO:
        """Delegate material assignment to the capabilities layer."""
        logger.info("Orchestrating set_material for %s", request.object_name)
        return await self._aggregate.set_material(request)

    async def apply_modifier(self, request: ApplyModifierRequestVO) -> ModifierResultVO:
        """Delegate modifier operation to the capabilities layer."""
        logger.info("Orchestrating apply_modifier for %s", request.modifier_name)
        return await self._aggregate.apply_modifier(request)

    async def delete_object(self, request: DeleteObjectRequestVO) -> DeletionResultVO:
        """Delegate object deletion to the capabilities layer."""
        logger.info("Orchestrating delete_object for %s", request.object_name)
        return await self._aggregate.delete_object(request)

    async def get_object_info(self, request: GetObjectInfoRequestVO) -> ObjectInfoResultVO:
        """Delegate object info retrieval to the capabilities layer."""
        logger.info("Orchestrating get_object_info for %s", request.object_name)
        return await self._aggregate.get_object_info(request)

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return "ObjectOrchestrator()"
