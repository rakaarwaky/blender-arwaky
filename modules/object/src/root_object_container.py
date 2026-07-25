"""Root: Object feature composition container.

Wires concrete implementations to contracts and bootstraps the object module:
  Capabilities (7 individual) → Agent Orchestrator → (exposed as ObjectOperateAggregate)

This file is the composition root for the object feature. It instantiates
concrete implementations, connects them to protocol/aggregate contracts,
and provides the assembled aggregate for dependency injection by callers.

Structure:
  1. Constants & imports
  2. ObjectContainer — wires 7 individual capabilities to aggregate
"""

import logging

from modules.shared.src.object.contract_object_operate_aggregate import ObjectOperateAggregate

# Lazy imports to avoid circular deps — resolved at wiring time
from .agent_object_orchestrator import ObjectOrchestrator
from .capabilities_apply_modifier_executor import ApplyModifierExecutor
from .capabilities_create_primitive_executor import CreatePrimitiveExecutor
from .capabilities_delete_object_executor import DeleteObjectExecutor
from .capabilities_get_object_info_executor import GetObjectInfoExecutor
from .capabilities_place_asset_executor import PlaceAssetExecutor
from .capabilities_set_material_executor import SetMaterialExecutor
from .capabilities_set_transform_executor import SetTransformExecutor

logger = logging.getLogger("BlenderMCPServer")


class ObjectContainer:
    """Dependency injection container for the object feature module.

    Wires 7 individual capability protocols to their executors,
    then assembles them into the ObjectOrchestrator aggregate facade.

    Capabilities → Agent Orchestrator → (exposed as ObjectOperateAggregate)
    """

    def __init__(self, code_executor: object) -> None:
        """Initialize the object feature container.

        Args:
            code_executor: An ICodeExecutionProtocol implementation for Blender code execution.
        """
        self._code_executor = code_executor
        self._orchestrator: ObjectOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire 7 individual capability executors to the orchestrator.

        Creates the capability → orchestrator chain for each FR:
          code_executor → PlaceAssetExecutor, CreatePrimitiveExecutor, ...
          All 7 → ObjectOrchestrator (implements ObjectOperateAggregate)
        """
        if self._wired:
            return

        logger.info("Wiring object feature module (7 individual capabilities)")

        # Capabilities layer — each implements its own protocol
        place_asset_cap = PlaceAssetExecutor(self._code_executor)
        create_primitive_cap = CreatePrimitiveExecutor(self._code_executor)
        set_transform_cap = SetTransformExecutor(self._code_executor)
        set_material_cap = SetMaterialExecutor(self._code_executor)
        apply_modifier_cap = ApplyModifierExecutor(self._code_executor)
        delete_object_cap = DeleteObjectExecutor(self._code_executor)
        get_object_info_cap = GetObjectInfoExecutor(self._code_executor)

        # Agent layer — implements aggregate, depends on all 7 protocols
        self._orchestrator = ObjectOrchestrator(
            place_asset_cap=place_asset_cap,
            create_primitive_cap=create_primitive_cap,
            set_transform_cap=set_transform_cap,
            set_material_cap=set_material_cap,
            apply_modifier_cap=apply_modifier_cap,
            delete_object_cap=delete_object_cap,
            get_object_info_cap=get_object_info_cap,
        )

        self._wired = True
        logger.info("Object feature module wired successfully (7 capabilities)")

    @property
    def aggregate(self) -> ObjectOperateAggregate:
        """Return the assembled ObjectOperateAggregate facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired:
            raise RuntimeError("ObjectContainer not wired — call wire() first")
        if self._orchestrator is None:
            raise RuntimeError("Orchestrator not initialized — call wire() first")
        return self._orchestrator


def create_object_feature(
    code_executor: object,
) -> ObjectOperateAggregate:
    """Factory function to create and wire the object feature module.

    Convenience function for top-level entry points that need the aggregate.

    Args:
        code_executor: An ICodeExecutionProtocol implementation for Blender code execution.

    Returns:
        The assembled ObjectOperateAggregate ready for use.
    """
    container = ObjectContainer(code_executor)
    container.wire()
    return container.aggregate
