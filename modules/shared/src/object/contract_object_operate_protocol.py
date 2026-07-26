"""Object domain contract: backward compatibility re-exports.

All individual protocols have been split into separate files for the
"1 capabilities = 1 FR" architecture. This file re-exports the old
monolithic protocol for backward compatibility with existing consumers.

New code should import from individual protocol files:
  - contract_place_asset_protocol
  - contract_create_primitive_protocol
  - contract_set_transform_protocol
  - contract_set_material_protocol
  - contract_apply_modifier_protocol
  - contract_delete_object_protocol
  - contract_get_object_info_protocol
"""

from __future__ import annotations

# Re-export all individual protocols for backward compatibility
from .contract_apply_modifier_protocol import ApplyModifierProtocol
from .contract_create_primitive_protocol import CreatePrimitiveProtocol
from .contract_delete_object_protocol import DeleteObjectProtocol
from .contract_get_object_info_protocol import GetObjectInfoProtocol

# Re-export aggregate facade as ObjectOperateProtocol for backward compatibility
from .contract_object_operate_aggregate import ObjectOperateAggregate as ObjectOperateProtocol
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
    "ObjectOperateProtocol",
]
