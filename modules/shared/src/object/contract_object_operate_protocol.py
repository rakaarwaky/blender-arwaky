"""Object domain contract: protocol re-exports.

Convenience aggregation of the individual object protocols so callers can
import them from one place. The canonical protocol definitions live in the
per-capability contract files (contract_*_protocol)."""

from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import ErrorString

from .contract_apply_modifier_protocol import ApplyModifierProtocol
from .contract_create_primitive_protocol import CreatePrimitiveProtocol
from .contract_delete_object_protocol import DeleteObjectProtocol
from .contract_get_object_info_protocol import GetObjectInfoProtocol
from .contract_object_operate_aggregate import ObjectOperateAggregate
from .contract_place_asset_protocol import PlaceAssetProtocol
from .contract_set_material_protocol import SetMaterialProtocol
from .contract_set_transform_protocol import SetObjectTransformProtocol

__all__ = [
    "ApplyModifierProtocol",
    "CreatePrimitiveProtocol",
    "DeleteObjectProtocol",
    "GetObjectInfoProtocol",
    "PlaceAssetProtocol",
    "SetMaterialProtocol",
    "SetObjectTransformProtocol",
    "ObjectOperateAggregate",
]
