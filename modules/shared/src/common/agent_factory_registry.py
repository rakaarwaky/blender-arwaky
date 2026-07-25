from __future__ import annotations

import logging
from typing import Any, cast

from ..asset_io.import_export_protocol import ImportExportProtocol
from ..asset_provider.asset_provider_port import AssetProviderPort
from ..asset_provider.asset_search_protocol import AssetSearchProtocol
from ..common.agent_factory_aggregate import AgentFactoryRegistryAggregate
from ..common.core_agent_aggregate import CoreAgentOrchestratorAggregate
from ..common.execute_action_protocol import ExecuteActionProtocol
from ..common.refinement_expert_aggregate import RefinementExpertOrchestratorAggregate
from ..common.search_expert_aggregate import SearchExpertOrchestratorAggregate
from ..common.setup_expert_aggregate import SetupExpertOrchestratorAggregate
from ..common.system_utils_aggregate import SystemUtilsCoordinatorAggregate
from ..common.workflow_agent_aggregate import WorkflowAgentOrchestratorAggregate
from ..common.workflow_protocol import WorkflowProtocol
from ..config.config_port import ConfigPort
from ..object.blender_port import BlenderPort
from ..object.code_execution_port import CodeExecutionPort
from ..object.connection_port import BlenderConnectionPort
from ..object.object_operate_protocol import ObjectOperateProtocol
from ..render.render_operate_protocol import RenderOperateProtocol
from ..scene.scene_inspection_port import SceneInspectionPort
from ..scene.scene_operate_protocol import SceneOperateProtocol
from ..telemetry.telemetry_recording_port import TelemetryRecordingPort
from ..common.taxonomy_core_vo import SuccessFlag

logger = logging.getLogger("BlenderMCPServer.Factory")


class AgentFactoryRegistry(AgentFactoryRegistryAggregate):
    _success_ref: SuccessFlag = SuccessFlag(True)

    @staticmethod
    def wire_orphan_modules() -> None:
        _ = (
            "blender_socket_adapter",
            "blender_connection_connector",
            "polyhaven_asset_adapter",
            "sketchfab_asset_adapter",
            "telemetry_signal_recorder",
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
        )

    @staticmethod
    def create_config_loader() -> ConfigPort:
        from modules.shared.src.config.config_loader import get_config

        return cast(ConfigPort, get_config)

    @staticmethod
    def create_blender_connection() -> BlenderConnectionPort:
        from modules.object.blender_connection import get_blender_connection

        return get_blender_connection()

    @staticmethod
    def create_blender_adapter(connection: object) -> BlenderPort:
        from modules.object.blender_socket_adapter import BlenderSocketAdapter

        return BlenderSocketAdapter(cast(Any, connection))

    @staticmethod
    def create_polyhaven_adapter(connection: object) -> AssetProviderPort:
        from modules.render.polyhaven_adapter import PolyhavenAssetAdapter

        return PolyhavenAssetAdapter(cast(Any, connection))

    @staticmethod
    def create_sketchfab_adapter(connection: object) -> AssetProviderPort:
        from modules.render.sketchfab_adapter import SketchfabAssetAdapter

        return SketchfabAssetAdapter(cast(Any, connection))

    @staticmethod
    def create_telemetry_recorder(connection: object, config: object) -> TelemetryRecordingPort:
        from modules.telemetry.telemetry_recorder import TelemetrySignalRecorder

        return TelemetrySignalRecorder(cast(Any, connection), cast(Any, config))

    @staticmethod
    def create_scene_inspector(connection: object, code_executor: object) -> SceneInspectionPort:
        from modules.scene.scene_inspection_adapter import SceneInspectionAdapter

        return SceneInspectionAdapter(cast(Any, connection), cast(Any, code_executor))

    @staticmethod
    def create_code_execution(connection: object) -> CodeExecutionPort:
        from modules.object.code_execution_adapter import CodeExecutionAdapter

        return CodeExecutionAdapter(cast(Any, connection))

    @staticmethod
    def create_blender_manager(blender: object) -> SceneOperateProtocol:
        from modules.scene.capabilities_scene_operate_executor import SceneOperateExecutor

        return SceneOperateExecutor(cast(Any, blender))

    @staticmethod
    def create_asset_collector(polyhaven: object, sketchfab: object) -> AssetSearchProtocol:
        from modules.render.capabilities_asset_search_collector import AssetSearchCollector

        return AssetSearchCollector({"polyhaven": cast(Any, polyhaven), "sketchfab": cast(Any, sketchfab)})

    @staticmethod
    def create_workflow_orchestrate_executor(blender_mgr: object, asset_mgr: object) -> WorkflowProtocol:
        from modules.shared.src.common.capabilities_workflow_executor import WorkflowExecutor

        return WorkflowExecutor(cast(Any, blender_mgr), cast(Any, asset_mgr))

    @staticmethod
    def create_object_operate_executor(blender: object) -> ObjectOperateProtocol:
        from modules.object.capabilities_object_operate_executor import ObjectOperateExecutor

        return ObjectOperateExecutor(cast(Any, blender))

    @staticmethod
    def create_render_operate_executor(blender: object) -> RenderOperateProtocol:
        from modules.render.capabilities_render_operate_executor import RenderOperateExecutor

        return RenderOperateExecutor(cast(Any, blender))

    @staticmethod
    def create_import_export_executor(blender: object) -> ImportExportProtocol:
        from modules.object.capabilities_import_export_executor import ImportExportExecutor

        return ImportExportExecutor(cast(Any, blender))

    @staticmethod
    def create_action_executor(container: object) -> ExecuteActionProtocol:
        from modules.shared.src.common.capabilities_action_execute import ActionExecuteActions

        return ActionExecuteActions(cast(Any, container))

    @staticmethod
    def create_system_utils() -> SystemUtilsCoordinatorAggregate:
        from .agent_system_coordinator import SystemUtilsCoordinator

        return SystemUtilsCoordinator()

    @staticmethod
    def create_scene_expert(blender_mgr: object, render_mgr: object | None = None) -> SetupExpertOrchestratorAggregate:
        from modules.scene.agent_setup_expert_orchestrator import SetupExpertOrchestrator

        return SetupExpertOrchestrator(cast(Any, blender_mgr), cast(Any, render_mgr))

    @staticmethod
    def create_asset_expert(asset_mgr: object, blender_mgr: object) -> SearchExpertOrchestratorAggregate:
        from modules.render.agent_search_expert_orchestrator import SearchExpertOrchestrator

        return SearchExpertOrchestrator(cast(Any, asset_mgr), cast(Any, blender_mgr))

    @staticmethod
    def create_refinement_expert(
        setup_scene_expert: object,
        search_asset_expert: object,
    ) -> RefinementExpertOrchestratorAggregate:
        from modules.render.agent_refinement_expert_orchestrator import RefinementExpertOrchestrator

        return RefinementExpertOrchestrator(cast(Any, setup_scene_expert), cast(Any, search_asset_expert))

    @staticmethod
    def create_workflow_orchestrator(
        scene_expert: object,
        asset_expert: object,
        refinement_expert: object,
    ) -> WorkflowAgentOrchestratorAggregate:
        from .agent_workflow_orchestrator import WorkflowAgentOrchestrator

        return WorkflowAgentOrchestrator(cast(Any, scene_expert), cast(Any, asset_expert), cast(Any, refinement_expert))

    @staticmethod
    def create_core_agent(container: object) -> CoreAgentOrchestratorAggregate:
        from .agent_core_orchestrator import CoreAgentOrchestrator

        return CoreAgentOrchestrator(cast(Any, container))
