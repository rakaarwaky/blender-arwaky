"""Root: Object feature composition container.

Wires concrete implementations to contracts and bootstraps the object module:
  Capabilities → Agent Orchestrator → (exposed as ObjectOperateAggregate)

This file is the composition root for the object feature. It instantiates
concrete implementations, connects them to protocol/aggregate contracts,
and provides the assembled aggregate for dependency injection by callers.
"""

from __future__ import annotations

import logging

from modules.shared.src.object.contract_object_operate_aggregate import ObjectOperateAggregate
from modules.shared.src.object.contract_object_operate_protocol import ObjectOperateProtocol

# Lazy imports to avoid circular deps — resolved at wiring time
from .agent_object_orchestrator import ObjectOrchestrator
from .capabilities_object_operate_executor import ObjectOperateExecutor

logger = logging.getLogger("BlenderMCPServer")


class ObjectContainer:
    """Dependency injection container for the object feature module.

    Wires:
      ICodeExecutionProtocol → ObjectOperateExecutor (implements ObjectOperateProtocol)
      ObjectOperateProtocol → ObjectOrchestrator (implements ObjectOperateAggregate)

    Exposes ObjectOperateAggregate as the facade for external consumers.
    """

    def __init__(self, code_executor: object) -> None:
        """Initialize the object feature container.

        Args:
            code_executor: An ICodeExecutionProtocol implementation for Blender code execution.
        """
        self._code_executor = code_executor
        self._executor: ObjectOperateProtocol | None = None
        self._orchestrator: ObjectOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire concrete implementations to contracts.

        Creates the capability → orchestrator chain:
          code_executor → ObjectOperateExecutor → ObjectOrchestrator
        """
        if self._wired:
            return

        logger.info("Wiring object feature module")

        # Capabilities layer — implements protocol
        self._executor = ObjectOperateExecutor(self._code_executor)

        # Agent layer — implements aggregate, depends on protocol
        self._orchestrator = ObjectOrchestrator(self._executor)

        self._wired = True
        logger.info("Object feature module wired successfully")

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

    @property
    def executor(self) -> ObjectOperateProtocol:
        """Return the raw ObjectOperateExecutor capability (for testing or direct access)."""
        if not self._wired:
            raise RuntimeError("ObjectContainer not wired — call wire() first")
        if self._executor is None:
            raise RuntimeError("Executor not initialized — call wire() first")
        return self._executor


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
