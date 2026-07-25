"""BlenderArwaky shared domain types — taxonomy + contract layers.

Organized by domain:
- common/: Core cross-cutting features
- config/: Application config
- scene/: Scene info,
- object/: Blender object
- render/: Render
- asset/: Import/export provider asset
- job/: Job state
- telemetry/: Event telemetry
"""

from . import (
    asset_io,
    asset_provider,
    common,
    config,
    job,
    object,
    render,
    scene,
    telemetry,
)

# Re-export all taxonomy types from domain folders for backward compatibility

# === Common domain exports ===
from .common.taxonomy_core_vo import (
    ActionName,
    AssetCount,
    AssetId,
    AssetIdList,
    AssetName,
    AssetType,
    AssetTypeFilter,
    BBoxIntegers,
    BlenderObjectList,
    BlenderVersion,
    CapabilityRef,
    CleanupMode,
    ConfigPath,
    ConfigValue,
    CoordinateList,
    CustomerUuid,
    Details,
    DirectoryPath,
    DomainRef,
    DurationMs,
    EnabledFlag,
    ErrorString,
    ExitCode,
    ExportFormat,
    FilePath,
    FormatRef,
    HdriId,
    ImageBytes,
    ImageFormat,
    IterationCount,
    JobId,
    JobState,
    LightStrength,
    MaterialName,
    MaxImageSize,
    MaxSize,
    ModifierName,
    NextPageToken,
    ObjectCount,
    ObjectId,
    ObjectIdList,
    ObjectName,
    ObjectType,
    ParentId,
    PlatformName,
    PortNumber,
    PrimitiveType,
    Progress,
    Prompt,
    ProviderName,
    PythonCode,
    RenderEngine,
    RenderSamples,
    RenderTime,
    ResolutionX,
    ResolutionY,
    ResultLimit,
    ResultUrl,
    RotationVector,
    RuleName,
    SampleCount,
    ScaleFactor,
    ScaleVector,
    SceneId,
    SceneRuleSetName,
    SearchQuery,
    SectionRef,
    ServerName,
    SessionId,
    SkillName,
    StatusString,
    StringList,
    SuccessFlag,
    TagList,
    TaskUuid,
    ThumbnailUrl,
    Timestamp,
    ToolName,
    UseDenoising,
    UserId,
    VersionString,
    WorkflowName,
)

from .common.taxonomy_domain_error import (
    AssetNotFoundError,
    BlenderConnectionFailure,
    BlenderMCPError,
    ConnectionError,
    ConnectionFailure,
    DomainError,
    ExecutionError,
    InvalidCommandError,
    ProviderError,
    SceneValidationError,
    ValidationError,
)

from .common.taxonomy_core_vo import ErrorMessage

from .common.taxonomy_command_catalog_constant import (
    ACTION_NAMES,
    COMMAND_CATALOG,
    CommandCatalog,
    CommandSpec,
)

from .common.taxonomy_vector3d_vo import Vector3D

from .common.taxonomy_bounding_box_vo import BoundingBox

from .common.taxonomy_app_config_vo import ApplicationConfig

# === Scene domain exports ===
from .scene.taxonomy_scene_info_vo import (
    RENDER_ENGINE_CYCLES,
    RENDER_ENGINE_EEVEE,
    SceneInfo,
)

from .scene.taxonomy_scene_request_vo import (
    CleanupSceneRequestVO,
    CleanupSceneResponseVO,
    GetSceneInfoRequestVO,
    GetSceneInfoResponseVO,
    SetupEnvironmentRequestVO,
    SetupEnvironmentResponseVO,
)

# === Object domain exports ===
from .object.taxonomy_blender_object_entity import (
    BlenderObject,
    create_object_id,
)

from .object.taxonomy_object_constant import (
    ALLOWED_OBJECT_TYPES,
    OBJECT_TYPE_ARMATURE,
    OBJECT_TYPE_CAMERA,
    OBJECT_TYPE_CURVE,
    OBJECT_TYPE_EMPTY,
    OBJECT_TYPE_FONT,
    OBJECT_TYPE_GPENCIL,
    OBJECT_TYPE_LATTICE,
    OBJECT_TYPE_LIGHT,
    OBJECT_TYPE_MESH,
    OBJECT_TYPE_META,
    OBJECT_TYPE_POINTCLOUD,
    OBJECT_TYPE_SURFACE,
    OBJECT_TYPE_VOLUME,
)

from .object.taxonomy_object_request_vo import (
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

# === Asset provider domain exports ===
from .asset_provider.taxonomy_asset_constant import (
    ASSET_TYPE_HDRIS,
    ASSET_TYPE_MODELS,
    ASSET_TYPE_TEXTURES,
    PROVIDER_POLYHAVEN,
    PROVIDER_SKETCHFAB,
)

from .asset_provider.taxonomy_asset_data_vo import (
    AssetMetadata,
    ImportedAsset,
    create_asset_id,
    create_provider_name,
)

from .asset_provider.taxonomy_asset_request_vo import (
    AssetDownloadRequestVO,
    AssetDownloadResponseVO,
    AssetSearchRequestVO,
    AssetSearchResponseVO,
)

# === Render domain exports ===
from .render.taxonomy_render_request_vo import (
    GetScreenshotRequestVO,
    RenderRequestVO,
    RenderResponseVO,
    ScreenshotResponseVO,
)

# === Asset I/O domain exports ===
from .asset_io.taxonomy_import_export_vo import (
    ExportModelRequestVO,
    ExportModelResponseVO,
    ImportGlbRequestVO,
    ImportGlbResponseVO,
)

# === Job domain exports ===
from .job.taxonomy_job_state_constant import (
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
)

from .job.taxonomy_job_status_entity import (
    JobStatus,
    create_job_id,
    create_progress,
)

# === Telemetry domain exports ===
from .telemetry.taxonomy_event_constant import (
    EVENT_TYPE_CONNECTION,
    EVENT_TYPE_ERROR,
    EVENT_TYPE_PROMPT_SENT,
    EVENT_TYPE_STARTUP,
    EVENT_TYPE_TOOL_EXECUTION,
)

from .telemetry.taxonomy_telemetry_event import EventType, TelemetryEvent

# === Contract layer exports (organized by domain) ===

# Protocols (business behavior contracts)
from .scene.scene_operate_protocol import SceneOperateProtocol
from .object.object_operate_protocol import ObjectOperateProtocol
from .render.render_operate_protocol import RenderOperateProtocol
from .asset_io.import_export_protocol import ImportExportProtocol
from .asset_provider.asset_search_protocol import AssetSearchProtocol
from .common.workflow_protocol import WorkflowProtocol
from .common.execute_action_protocol import ExecuteActionProtocol

# Ports (infrastructure-facing contracts)
from .object.blender_port import BlenderPort
from .object.connection_port import BlenderConnectionPort
from .object.connection_factory_port import BlenderConnectionFactoryPort
from .object.code_execution_port import CodeExecutionPort
from .config.config_port import ConfigPort
from .common.command_catalog_port import CommandCatalogPort
from .scene.scene_inspection_port import SceneInspectionPort
from .render.viewport_capture_port import ViewportCapturePort
from .asset_provider.asset_provider_port import AssetProviderPort
from .asset_provider.sketchfab_api_port import SketchfabApiPort
from .asset_provider.polyhaven_api_port import PolyhavenApiPort
from .telemetry.telemetry_recording_port import TelemetryRecordingPort

# Aggregates (structural contracts for agents)
from .common.core_agent_aggregate import CoreAgentOrchestratorAggregate
from .common.agent_di_aggregate import AgentDiContainerAggregate
from .common.agent_factory_aggregate import AgentFactoryRegistryAggregate
from .common.agent_base_aggregate import AgentBaseContainerAggregate
from .common.expert_base_aggregate import ExpertBaseOrchestratorAggregate
from .common.workflow_agent_aggregate import WorkflowAgentOrchestratorAggregate
from .common.refinement_expert_aggregate import RefinementExpertOrchestratorAggregate
from .common.search_expert_aggregate import SearchExpertOrchestratorAggregate
from .common.setup_expert_aggregate import SetupExpertOrchestratorAggregate
from .common.server_bootstrap_aggregate import ServerBootstrapManagerAggregate
from .common.system_prompt_aggregate import SystemPromptManagerAggregate
from .common.system_utils_aggregate import SystemUtilsCoordinatorAggregate

__all__ = [
    # Domain folders
    "common",
    "scene",
    "object",
    "render",
    "asset_io",
    "asset_provider",
    "job",
    "telemetry",
    # Core Value Objects
    "UserId",
    "SceneId",
    "AssetId",
    "JobId",
    "HdriId",
    "ObjectId",
    "ParentId",
    "ObjectName",
    "AssetName",
    "ProviderName",
    "MaterialName",
    "ModifierName",
    "ActionName",
    "WorkflowName",
    "RuleName",
    "SceneRuleSetName",
    "ObjectType",
    "AssetType",
    "RenderEngine",
    "ImageFormat",
    "PrimitiveType",
    "ExportFormat",
    "JobState",
    "CleanupMode",
    "AssetTypeFilter",
    "Prompt",
    "ErrorString",
    "ErrorMessage",
    "SearchQuery",
    "NextPageToken",
    "ResultUrl",
    "ThumbnailUrl",
    "MaxSize",
    "IterationCount",
    "PortNumber",
    "SampleCount",
    "ResolutionX",
    "ResolutionY",
    "ObjectCount",
    "AssetCount",
    "RenderSamples",
    "MaxImageSize",
    "ResultLimit",
    "LightStrength",
    "RenderTime",
    "Progress",
    "EnabledFlag",
    "SuccessFlag",
    "UseDenoising",
    "StringList",
    "TagList",
    "AssetIdList",
    "CoordinateList",
    "ScaleVector",
    "RotationVector",
    "ObjectIdList",
    "SkillName",
    "SectionRef",
    "ServerName",
    "DomainRef",
    "FormatRef",
    "CapabilityRef",
    "ExitCode",
    "FilePath",
    "DirectoryPath",
    "ConfigPath",
    "ConfigValue",
    "CustomerUuid",
    "SessionId",
    "Timestamp",
    "VersionString",
    "PlatformName",
    "ToolName",
    "DurationMs",
    "BlenderVersion",
    "StatusString",
    "PythonCode",
    "TaskUuid",
    "ScaleFactor",
    "ImageBytes",
    "BBoxIntegers",
    "Details",
    "BlenderObjectList",
    # Rich Value Objects
    "Vector3D",
    "BoundingBox",
    "AssetMetadata",
    "ImportedAsset",
    "SceneInfo",
    "ApplicationConfig",
    # Entities
    "BlenderObject",
    "JobStatus",
    # Errors
    "BlenderMCPError",
    "DomainError",
    "SceneValidationError",
    "AssetNotFoundError",
    "ValidationError",
    "ConnectionError",
    "ConnectionFailure",
    "ProviderError",
    "ExecutionError",
    "BlenderConnectionFailure",
    "InvalidCommandError",
    # Events
    "EventType",
    "TelemetryEvent",
    # Constants
    "ASSET_TYPE_HDRIS",
    "ASSET_TYPE_TEXTURES",
    "ASSET_TYPE_MODELS",
    "PROVIDER_POLYHAVEN",
    "PROVIDER_SKETCHFAB",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "OBJECT_TYPE_MESH",
    "OBJECT_TYPE_CAMERA",
    "OBJECT_TYPE_LIGHT",
    "OBJECT_TYPE_EMPTY",
    "OBJECT_TYPE_ARMATURE",
    "OBJECT_TYPE_CURVE",
    "OBJECT_TYPE_SURFACE",
    "OBJECT_TYPE_META",
    "OBJECT_TYPE_FONT",
    "OBJECT_TYPE_LATTICE",
    "OBJECT_TYPE_GPENCIL",
    "OBJECT_TYPE_VOLUME",
    "ALLOWED_OBJECT_TYPES",
    "COMMAND_CATALOG",
    "CommandCatalog",
    "CommandSpec",
    "ACTION_NAMES",
    "RENDER_ENGINE_CYCLES",
    "RENDER_ENGINE_EEVEE",
    "EVENT_TYPE_STARTUP",
    "EVENT_TYPE_TOOL_EXECUTION",
    "EVENT_TYPE_PROMPT_SENT",
    "EVENT_TYPE_CONNECTION",
    "EVENT_TYPE_ERROR",
    # Factories
    "create_asset_id",
    "create_object_id",
    "create_job_id",
    "create_provider_name",
    "create_progress",
    # Contracts — Protocols
    "SceneOperateProtocol",
    "ObjectOperateProtocol",
    "RenderOperateProtocol",
    "ImportExportProtocol",
    "AssetSearchProtocol",
    "WorkflowProtocol",
    "ExecuteActionProtocol",
    # Contracts — Ports
    "BlenderPort",
    "BlenderConnectionPort",
    "BlenderConnectionFactoryPort",
    "CodeExecutionPort",
    "ConfigPort",
    "CommandCatalogPort",
    "SceneInspectionPort",
    "ViewportCapturePort",
    "AssetProviderPort",
    "SketchfabApiPort",
    "PolyhavenApiPort",
    "TelemetryRecordingPort",
    # Contracts — Aggregates
    "CoreAgentOrchestratorAggregate",
    "AgentDiContainerAggregate",
    "AgentFactoryRegistryAggregate",
    "AgentBaseContainerAggregate",
    "ExpertBaseOrchestratorAggregate",
    "WorkflowAgentOrchestratorAggregate",
    "RefinementExpertOrchestratorAggregate",
    "SearchExpertOrchestratorAggregate",
    "SetupExpertOrchestratorAggregate",
    "ServerBootstrapManagerAggregate",
    "SystemPromptManagerAggregate",
    "SystemUtilsCoordinatorAggregate",
]
