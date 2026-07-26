"""Object domain — taxonomy types and contracts.

Provides Value Objects, Entities, Events, Errors, Constants,
7 individual Protocol interfaces, and Aggregate facade.
"""

from . import (
    taxonomy_blender_object_entity,
    taxonomy_object_constant,
    taxonomy_object_error_vo,
    taxonomy_object_event_vo,
    taxonomy_object_policy_vo,
    taxonomy_object_vo,
)
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
    "ObjectOperateAggregate",
    "PlaceAssetProtocol",
    "SetMaterialProtocol",
    "SetObjectTransformProtocol",
    "taxonomy_blender_object_entity",
    "taxonomy_object_constant",
    "taxonomy_object_error_vo",
    "taxonomy_object_event_vo",
    "taxonomy_object_policy_vo",
    "taxonomy_object_vo",
]
