"""BlenderArwaky shared domain types — taxonomy + contract layers.

Organized by domain:
- common/: Core cross-cutting
- object/: Object domain
- render/: Render domain
- job/: Job domain VOs
- telemetry/: Telemetry domain
"""

from . import (
    asset,
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

from .object.taxonomy_object_vo import (
    ApplyModifierVO,
    CreatePrimitiveVO,
    DeleteObjectVO,
    GetObjectInfoVO,
    PlaceAssetVO,
    SetMaterialVO,
    SetObjectTransformVO,
)


# === Render domain exports ===
from .render.taxonomy_render_vo import (
    CameraConfigVO,
    CameraSetupVO,
    GetScreenshotVO,
    HdriConfigVO,
    HdriSetupVO,
    RenderVO,
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

# === Asset domain exports ===
from .asset.taxonomy_asset_constant import (
    ASSET_TYPE_HDRIS,
    ASSET_TYPE_MODELS,
    ASSET_TYPE_TEXTURES,
    PROVIDER_POLYHAVEN,
    PROVIDER_SKETCHFAB,
)

from .asset.taxonomy_asset_data_vo import (
    AssetMetadata,
    ImportedAsset,
    create_asset_id,
    create_provider_name,
)

from .asset.taxonomy_asset_vo import (
    AssetDownloadVO,
    AssetSearchVO,
    ExportModelVO,
    ImportGlbVO,
)

# === Contract layer exports (organized by domain) ===

# Config domain — Protocols (inbound behavior interfaces)
from .config.contract_config_aggregate import IConfigAggregate
from .config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from .config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from .config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from .config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from .config.contract_redaction_rules_protocol import IRedactionRulesProtocol

# Config domain — Value Objects
from .config.taxonomy_config_vo import (
    RedactionRule,
    SensitiveKeyPattern,
    SettingsSnapshot,
    WorkspacePath,
)

# Config domain — Events
from .config.taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
    WorkspaceResolvedEvent,
)

# Config domain — Constants
from .config.taxonomy_config_constant import (
    DEFAULT_POLICY_MODE,
    ENV_PREFIX_LEGACY,
    ENV_PREFIX_PRODUCT,
    MAX_CONFIG_SIZE_BYTES,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    PROJECT_MARKERS,
    REDACTION_PLACEHOLDER,
    SENSITIVE_KEY_PATTERNS,
)

# Protocols (business behavior contracts)
from .scene.contract_scene_operate_protocol import SceneOperateProtocol
from .object.contract_object_operate_protocol import ObjectOperateProtocol
from .render.contract_render_operate_protocol import RenderOperateProtocol
from .asset.contract_asset_search_protocol import AssetSearchProtocol
from .asset.contract_import_export_protocol import ImportExportProtocol
from .common.contract_workflow_protocol import WorkflowProtocol
from .common.contract_execute_action_protocol import ExecuteActionProtocol

# Protocols (inbound behavior interfaces — Capabilities implement these)
from .common.contract_command_catalog import CommandCatalogPort
from .scene.contract_scene_inspection import SceneInspectionPort
from .render.contract_viewport_capture import ViewportCapturePort
from .asset.contract_asset_provider import AssetProviderPort
from .asset.contract_polyhaven_api import PolyhavenApiPort
from .asset.contract_sketchfab_api import SketchfabApiPort
from .telemetry.contract_telemetry_classification import TelemetryClassificationPort
from .telemetry.contract_telemetry_enrichment import TelemetryEnrichmentPort
from .telemetry.contract_telemetry_recording import TelemetryRecordingPort
from .telemetry.contract_telemetry_session_management import TelemetrySessionManagementPort

__all__ = [
    # Domain folders
    "common",
    "scene",
    "object",
    "render",
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
    "AssetMetadataItem",
    "AssetMetadataVO",
    "ImportedAsset",
    "SceneInfo",
    "ApplicationConfig",
    # Merged VOs
    "PlaceAssetVO",
    "GetObjectInfoVO",
    "SetObjectTransformVO",
    "DeleteObjectVO",
    "CreatePrimitiveVO",
    "SetMaterialVO",
    "ApplyModifierVO",
    "AssetSearchVO",
    "AssetDownloadVO",
    "ImportGlbVO",
    "ExportModelVO",
    "GetScreenshotVO",
    "RenderVO",
    "CameraSetupVO",
    "HdriSetupVO",
    "CameraConfigVO",
    "HdriConfigVO",
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
    "CommandCatalogPort",
    "SceneInspectionPort",
    "ViewportCapturePort",
    "AssetProviderPort",
    "SketchfabApiPort",
    "PolyhavenApiPort",
    "TelemetryClassificationPort",
    "TelemetryEnrichmentPort",
    "TelemetryRecordingPort",
    "TelemetrySessionManagementPort",
    # Contracts — Aggregates
    # Config domain — Aggregates
    "IConfigAggregate",
    # Config domain — Protocols
    "ISettingsLoaderProtocol",
    "ISettingsRetrieverProtocol",
    "IWorkspaceResolverProtocol",
    "ISettingsMetadataProtocol",
    "IRedactionRulesProtocol",
    # Config domain — Value Objects
    "SettingsSnapshot",
    "WorkspacePath",
    "RedactionRule",
    "SensitiveKeyPattern",
    # Config domain — Events
    "SettingsLoadedEvent",
    "SettingsReloadEvent",
    "WorkspaceResolvedEvent",
    "SettingsValidationWarningEvent",
    # Config domain — Constants
    "SENSITIVE_KEY_PATTERNS",
    "PROJECT_MARKERS",
    "MAX_CONFIG_SIZE_BYTES",
    "ENV_PREFIX_PRODUCT",
    "ENV_PREFIX_LEGACY",
    "REDACTION_PLACEHOLDER",
    "POLICY_MODE_STRICT",
    "POLICY_MODE_PERMISSIVE",
    "DEFAULT_POLICY_MODE",
]
