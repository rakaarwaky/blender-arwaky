"""Object feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/object/)   → VOs, Entities, Events, Errors, Constants
  - Contract (shared/src/object/)   → 7 individual protocols + Aggregate ABCs
  - Capabilities (7 executors)      → One per FR operation
  - Agent                           → ObjectOrchestrator (implements Aggregate facade)
  - Root                            → ObjectContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_object_container
from .capabilities_apply_modifier_executor import ApplyModifierExecutor
from .capabilities_create_primitive_executor import CreatePrimitiveExecutor
from .capabilities_delete_object_executor import DeleteObjectExecutor
from .capabilities_get_object_info_executor import GetObjectInfoExecutor
from .capabilities_place_asset_executor import PlaceAssetExecutor
from .capabilities_set_material_executor import SetMaterialExecutor
from .capabilities_set_transform_executor import SetTransformExecutor
from .root_object_container import ObjectContainer, create_object_feature

__all__ = [
    "ApplyModifierExecutor",
    "CreatePrimitiveExecutor",
    "DeleteObjectExecutor",
    "GetObjectInfoExecutor",
    "ObjectContainer",
    "PlaceAssetExecutor",
    "SetMaterialExecutor",
    "SetTransformExecutor",
    "create_object_feature",
    "root_object_container",
]