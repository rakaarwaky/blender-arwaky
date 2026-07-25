"""Agent: Object feature orchestrator.

Coordinates Blender object manipulation — create, transform, material, modifier, delete.
"""

import logging
from typing import Any

from modules.shared.src.object.contract_object_operate_protocol import ObjectOperateProtocol
from modules.shared.src.object.taxonomy_object_request_vo import (
    ApplyModifierRequestVO,
    ApplyModifierResponseVO,
    CreatePrimitiveRequestVO,
    CreatePrimitiveResponseVO,
    DeleteObjectRequestVO,
    DeleteObjectResponseVO,
    GetObjectInfoRequestVO,
    GetObjectInfoResponseVO,
    PlaceAssetRequestVO,
    PlaceAssetResponseVO,
    SetMaterialRequestVO,
    SetMaterialResponseVO,
    SetObjectTransformRequestVO,
    SetObjectTransformResponseVO,
)

logger = logging.getLogger("BlenderMCPServer")


class ObjectOrchestrator:
    """Orchestrates object operations."""

    def __init__(self, executor: ObjectOperateProtocol):
        self._executor = executor

    async def place_asset(self, request: PlaceAssetRequestVO) -> PlaceAssetResponseVO:
        return await self._executor.place_asset(request)

    async def create_primitive(self, request: CreatePrimitiveRequestVO) -> CreatePrimitiveResponseVO:
        return await self._executor.create_primitive(request)

    async def set_transform(self, request: SetObjectTransformRequestVO) -> SetObjectTransformResponseVO:
        return await self._executor.set_transform(request)

    async def set_material(self, request: SetMaterialRequestVO) -> SetMaterialResponseVO:
        return await self._executor.set_material(request)

    async def apply_modifier(self, request: ApplyModifierRequestVO) -> ApplyModifierResponseVO:
        return await self._executor.apply_modifier(request)

    async def delete_object(self, request: DeleteObjectRequestVO) -> DeleteObjectResponseVO:
        return await self._executor.delete_object(request)

    async def get_object_info(self, request: GetObjectInfoRequestVO) -> GetObjectInfoResponseVO:
        return await self._executor.get_object_info(request)
