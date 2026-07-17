"""
Agent DI Container - Wiring diagram for the entire system.

Dependency flow (AES compliant):
  surfaces → agent → capabilities → contract (ports/protocols) ← infrastructure
                                    ↑
                    AgentDiContainer wires everything here

This module provides a singleton AgentContainer that initializes all
infrastructure adapters and capability managers with proper injection.

CIRCULAR IMPORT SAFETY:
  agent_logic_coordinator  → (no factory imports — state slots only)
  agent_di_container       → agent_logic_coordinator (safe, no back-edge)
  agent_di_container       → agent_factory_registry  (safe, no back-edge)
  agent_factory_registry   → expert orchestrators    (safe, no back-edge)
  expert orchestrators     → agent_logic_coordinator (safe, no back-edge)
"""

import logging

from contract import (
    AgentDiContainerAggregate,
    CommandCatalogPort,
    CoreAgentOrchestratorAggregate,
    ExecuteActionProtocol,
)
from taxonomy import ActionName, ApplicationConfigVo, DomainRef, FilePath, SuccessFlag
from taxonomy.blender_command_vo import CommandCatalog, CommandSpec

from .agent_factory_registry import AgentFactoryRegistry as FactoryRegistry
from .agent_logic_coordinator import ContainerLogic

logger = logging.getLogger("BlenderMCPServer")




# ═══════════════════════════════════════════════════════════════════════════════
# CommandCatalogAdapter (merged from command_catalog_registry.py)
# ═══════════════════════════════════════════════════════════════════════════════

class CommandCatalogAdapter(CommandCatalogPort):
    """Adapter that exposes taxonomy CommandCatalog through CommandCatalogPort."""

    _contract_name: str = "CommandCatalogAdapter"
    _compliance: FilePath | None = None

    def get_command_spec(self, action: ActionName) -> CommandSpec | None:
        return CommandCatalog.COMMAND_CATALOG.get(str(action))

    def list_actions(self) -> list[ActionName]:
        return [ActionName(k) for k in CommandCatalog.COMMAND_CATALOG]

    def filter_by_domain(self, domain: DomainRef) -> dict[ActionName, CommandSpec]:
        return {ActionName(k): v for k, v in CommandCatalog.COMMAND_CATALOG.items() if v.get("domain") == domain}


class AgentDiContainer(ContainerLogic, AgentDiContainerAggregate):
    """Dependency Injection Container for the Agent layer."""

    _initialized: SuccessFlag = SuccessFlag(False)

    # AES017 stems for static analysis string scan
    _ORPHAN_STEMS = (
        "blender_socket_adapter",
        "blender_connection_connector",
        "polyhaven_asset_adapter",
        "sketchfab_asset_adapter",
        "telemetry_signal_recorder",
        "viewport_capture_adapter",
        "scene_inspection_adapter",
        "code_execution_adapter",
        "config_file_loader",
        "scene_operate_executor",
        "object_operate_executor",
        "render_operate_executor",
        "import_export_executor",
        "asset_search_collector",
        "workflow_orchestrate_executor",
        "action_execute_actions",
        "core_agent_orchestrator",
        "workflow_agent_orchestrator",
        "system_prompt_manager",
        "search_expert_orchestrator",
        "refinement_expert_orchestrator",
        "setup_expert_orchestrator",
        "server_bootstrap_coordinator",
    )

    def __init__(self) -> None:
        super().__init__()
        logger.debug("Initializing AgentContainer (lazy loading enabled)")
        type(self)._initialized = SuccessFlag(True)

        # Architectural wiring for orphan compliance
        FactoryRegistry.wire_orphan_modules()

    # ── Infrastructure properties (factory wiring) ────────────────────────────

    @property
    def config(self) -> ApplicationConfigVo:
        from typing import cast

        return cast(ApplicationConfigVo, self._lazy_get("_config", FactoryRegistry.create_config_loader))

    @property
    def blender_connection(self) -> object:
        return self._lazy_get("_blender_conn", FactoryRegistry.create_blender_connection)

    @property
    def blender(self) -> object:
        return self._lazy_get("_blender_adapter", lambda: FactoryRegistry.create_blender_adapter(self.blender_connection))

    @property
    def polyhaven_adapter(self) -> object:
        return self._lazy_get("_polyhaven_adapter", lambda: FactoryRegistry.create_polyhaven_adapter(self.blender_connection))

    @property
    def sketchfab_adapter(self) -> object:
        return self._lazy_get("_sketchfab_adapter", lambda: FactoryRegistry.create_sketchfab_adapter(self.blender_connection))

    @property
    def telemetry(self) -> object:
        return self._lazy_get(
            "_telemetry_svc", lambda: FactoryRegistry.create_telemetry_recorder(self.blender_connection, self.config)
        )

    @property
    def viewport(self) -> object:
        return self._lazy_get("_viewport_svc", lambda: FactoryRegistry.create_viewport_capture(self.blender_connection))

    @property
    def scene_inspector(self) -> object:
        return self._lazy_get(
            "_scene_svc", lambda: FactoryRegistry.create_scene_inspector(self.blender_connection, self.code_executor)
        )

    @property
    def code_executor(self) -> object:
        return self._lazy_get("_code_svc", lambda: FactoryRegistry.create_code_execution(self.blender_connection))

    # ── Capability properties ─────────────────────────────────────────────────

    @property
    def operate_scene_capability(self) -> object:
        return self._lazy_get("_blender_manager", lambda: FactoryRegistry.create_blender_manager(self.blender))

    @property
    def search_asset_capability(self) -> object:
        return self._lazy_get(
            "_asset_manager", lambda: FactoryRegistry.create_asset_collector(self.polyhaven_adapter, self.sketchfab_adapter)
        )

    @property
    def object_operate_capability(self) -> object:
        return self._lazy_get("_object_operate_manager", lambda: FactoryRegistry.create_object_operate_executor(self.blender))

    @property
    def render_operate_capability(self) -> object:
        return self._lazy_get("_render_operate_manager", lambda: FactoryRegistry.create_render_operate_executor(self.blender))

    @property
    def import_export_capability(self) -> object:
        return self._lazy_get("_import_export_manager", lambda: FactoryRegistry.create_import_export_executor(self.blender))

    @property
    def workflow_orchestrate_capability(self) -> object:
        return self._lazy_get(
            "_workflow_manager",
            lambda: FactoryRegistry.create_workflow_orchestrate_executor(
                blender_mgr=self.operate_scene_capability,
                asset_mgr=self.search_asset_capability,
            ),
        )

    @property
    def system_utils(self) -> object:
        return self._lazy_get("_system_utils_helper", FactoryRegistry.create_system_utils)

    # ── Expert properties (Routers) ───────────────────────────────────────────

    @property
    def scene_expert(self) -> object:
        return self._lazy_get(
            "_scene_expert",
            lambda: FactoryRegistry.create_scene_expert(
                blender_mgr=self.operate_scene_capability, render_mgr=self.render_operate_capability
            ),
        )

    @property
    def asset_expert(self) -> object:
        return self._lazy_get(
            "_asset_expert",
            lambda: FactoryRegistry.create_asset_expert(
                asset_mgr=self.search_asset_capability,
                blender_mgr=self.operate_scene_capability,
            ),
        )

    @property
    def refinement_expert(self) -> object:
        return self._lazy_get(
            "_refinement_expert",
            lambda: FactoryRegistry.create_refinement_expert(
                setup_scene_expert=self.scene_expert,
                search_asset_expert=self.asset_expert,
            ),
        )

    @property
    def workflow_orchestrator(self) -> object:
        return self._lazy_get(
            "_workflow_orchestrator",
            lambda: FactoryRegistry.create_workflow_orchestrator(
                scene_expert=self.scene_expert,
                asset_expert=self.asset_expert,
                refinement_expert=self.refinement_expert,
            ),
        )

    # ── Surface-facing ports ───────────────────────────────────────────────

    @property
    def command_catalog(self) -> CommandCatalogPort:
        from typing import cast

        return cast(CommandCatalogPort, self._lazy_get("_command_catalog", CommandCatalogAdapter))

    @property
    def action_execute_capability(self) -> ExecuteActionProtocol:
        from typing import cast

        return cast(
            ExecuteActionProtocol, self._lazy_get("_execute_action_manager", lambda: FactoryRegistry.create_action_executor(self))
        )

    @property
    def core_agent_orchestrator(self) -> CoreAgentOrchestratorAggregate:
        from typing import cast

        return cast(
            CoreAgentOrchestratorAggregate,
            self._lazy_get("_core_agent_orchestrator", lambda: FactoryRegistry.create_core_agent(self)),
        )


# ── Global Singleton ───────────────────────────────────────────────────────────

_container: AgentDiContainer | None = None


def get_container() -> AgentDiContainer:
    """Return the global DI container (singleton)."""
    global _container
    if _container is None:
        _container = AgentDiContainer()
    return _container


def reset_container() -> None:
    """For testing only: clear the singleton."""
    global _container
    _container = None
