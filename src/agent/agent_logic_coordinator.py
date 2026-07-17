"""
Shared logic base classes for agents and containers.
These are NOT agents (no IO) but provide shared logic to avoid duplication.

ARCHITECTURAL NOTE:
  ContainerLogic holds ONLY lazy-init state slots (None guards).
  It must NEVER import from agent_factory_registry — that would create a cycle:
    agent_logic_coordinator → agent_factory_registry → expert orchestrators
    → agent_logic_coordinator (CYCLE).
  All factory-calling properties are implemented in AgentDiContainer.
"""

import logging

from contract import AgentBaseContainerAggregate, ExpertBaseOrchestratorAggregate
from taxonomy import ApplicationConfigVo, ObjectName, SuccessFlag

logger = logging.getLogger("BlenderMCPServer.Agents")


class ExpertOrchestratorLogic(ExpertBaseOrchestratorAggregate):
    """Shared logic for all expert orchestrators."""

    def __init__(self, name: str):
        self.name = name
        self.logger = logger.getChild(name)

    def log_info(self, msg: str):
        self.logger.info(f"[{self.name}] {msg}")

    def log_error(self, msg: str):
        self.logger.error(f"[{self.name}] {msg}")

    def log_warning(self, msg: str):
        self.logger.warning(f"[{self.name}] {msg}")


class ContainerLogic(AgentBaseContainerAggregate):
    """
    Shared state scaffold for DI containers.

    Only declares lazy-init None slots — NO factory calls here.
    Subclasses (AgentDiContainer) are responsible for wiring factory properties.
    This ensures ContainerLogic stays import-cycle-free.
    """

    def _lazy_get(self, attr_name: str, factory_fn) -> object:
        val = getattr(self, attr_name)
        if val is None:
            val = factory_fn()
            setattr(self, attr_name, val)
        return val

    def __init__(self) -> None:
        # ── infrastructure slots ──────────────────────────────────────────────
        self._config: ApplicationConfigVo | None = None
        self._blender_conn: object | None = None
        self._blender_adapter: object | None = None
        self._polyhaven_adapter: object | None = None
        self._sketchfab_adapter: object | None = None
        self._telemetry_svc: object | None = None
        self._viewport_svc: object | None = None
        self._scene_svc: object | None = None
        self._code_svc: object | None = None
        self._blender_handler: object | None = None
        self._tel_config: object | None = None
        self._tel_decorator: object | None = None
        self._tel_api: object | None = None

        # ── capability slots ──────────────────────────────────────────────────
        self._blender_manager: object | None = None
        self._asset_manager: object | None = None
        self._workflow_manager: object | None = None
        self._object_operate_manager: object | None = None
        self._render_operate_manager: object | None = None
        self._import_export_manager: object | None = None
        self._execute_action_manager: object | None = None
        self._system_utils_helper: object | None = None
        self._workflow_orchestrator: object | None = None

        # ── expert slots ──────────────────────────────────────────────────────
        self._scene_expert: object | None = None
        self._asset_expert: object | None = None
        self._refinement_expert: object | None = None
        self._core_agent_orchestrator: object | None = None

        # ── surface-facing catalog ────────────────────────────────────────────
        self._command_catalog: object | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# AgentBaseContainer (merged from agent_base_container.py)
# ═══════════════════════════════════════════════════════════════════════════════


class AgentBaseContainer(ContainerLogic, AgentBaseContainerAggregate):
    """Base container handling infrastructure and capability managers."""

    _success_ref: SuccessFlag = SuccessFlag(True)

    def __init__(self) -> None:
        super().__init__()


# ═══════════════════════════════════════════════════════════════════════════════
# ExpertBaseOrchestrator (merged from expert_base_orchestrator.py)
# ═══════════════════════════════════════════════════════════════════════════════


class ExpertBaseOrchestrator(ExpertOrchestratorLogic, ExpertBaseOrchestratorAggregate):
    """Base expert agent."""

    _success_ref: SuccessFlag = SuccessFlag(True)
    _obj_ref: ObjectName = ObjectName("ref")

    def __init__(self, name: str = "ExpertBaseOrchestrator"):
        super().__init__(name)

    async def execute(self, *_args, **_kwargs) -> dict[str, object]:
        """Default execution logic."""
        return {"success": True, "message": "Base expert execution"}
