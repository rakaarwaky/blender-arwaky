"""BlenderArwaky shared domain types — taxonomy + contract layers.

Organized by domain:
- common/: Core cross-cutting
- object/: Object domain
- render/: Render domain
- job/: Job domain VOs
- telemetry/: Telemetry domain
- diagnostics/: Diagnostics observability protocols
"""

from . import (
    asset,
    common,
    config,
    diagnostics,
    dispatcher,
    job,
    launcher,
    object,
    render,
    scene,
    telemetry,
)
from .asset.contract_asset_aggregate import IAssetAggregate
from .asset.contract_asset_download_protocol import AssetDownloadProtocol
from .asset.contract_asset_extract_protocol import AssetExtractProtocol
from .asset.contract_asset_import_protocol import AssetImportProtocol
from .asset.contract_asset_provider_protocol import AssetProviderProtocol
from .asset.contract_asset_search_protocol import AssetSearchProtocol

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
    AssetDownloadCacheVO,
    AssetDownloadVO,
    AssetExtractArchiveVO,
    AssetImportBlenderVO,
    AssetMetadataItem,
    AssetMetadataVO,
    AssetSearchVO,
    ExportModelVO,
    ImportGlbVO,
)

# Protocols (inbound behavior interfaces — Capabilities implement these)
from .common.contract_command_catalog_protocol import CommandCatalogProtocol
from .common.contract_execute_action_protocol import ExecuteActionProtocol
from .common.contract_workflow_protocol import WorkflowProtocol
from .common.taxonomy_bounding_box_vo import BoundingBox
from .common.taxonomy_command_catalog_constant import (
    ACTION_NAMES,
    COMMAND_CATALOG,
    CommandSpec,
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
    CoordinateList,
    CustomerUuid,
    Details,
    DirectoryPath,
    DomainRef,
    DurationMs,
    EnabledFlag,
    ErrorMessage,
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
    BlenderConnectionError,
    BlenderMCPError,
    DomainError,
    ExecutionError,
    InvalidCommandError,
    ProviderError,
    SceneValidationError,
    ValidationError,
)
from .common.taxonomy_vector3d_vo import Vector3D

# === Contract layer exports (organized by domain) ===
# Config domain — Protocols (inbound behavior interfaces)
from .config.contract_config_aggregate import IConfigAggregate
from .config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from .config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from .config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from .config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from .config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol

# Config domain — Constants
from .config.taxonomy_config_constant import (
    DEFAULT_POLICY_MODE,
    ENV_PREFIX_PRODUCT,
    MAX_CONFIG_SIZE_BYTES,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    PROJECT_MARKERS,
    REDACTION_PLACEHOLDER,
    SENSITIVE_KEY_PATTERNS,
)

# Config domain — Events
from .config.taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
    WorkspaceResolvedEvent,
)

# Config domain — Value Objects
from .config.taxonomy_config_vo import (
    RedactionRule,
    SettingsSnapshot,
    WorkspacePath,
)
from .diagnostics.contract_diagnostics_aggregate import IDiagnosticsAggregate

# === Dispatcher domain exports ===
from .dispatcher.contract_action_discovery_protocol import ActionDiscoveryProtocol
from .dispatcher.contract_background_submit_protocol import BackgroundSubmitProtocol
from .dispatcher.contract_catalog_registration_protocol import CatalogRegistrationProtocol
from .dispatcher.contract_request_validation_protocol import RequestValidationProtocol
from .dispatcher.contract_result_normalization_protocol import ResultNormalizationProtocol
from .dispatcher.contract_sync_dispatch_protocol import SyncDispatchProtocol
from .dispatcher.taxonomy_action_command_vo import ActionCommandVO
from .dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from .dispatcher.taxonomy_discovery_outcome_vo import DiscoveryOutcomeVO
from .dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

# === Gateway domain exports ===
from .gateway.contract_code_execution_protocol import CodeExecutionProtocol
from .gateway.contract_connection_protocol import ConnectionProtocol
from .gateway.contract_maintenance_protocol import ConnectionMaintenanceProtocol
from .gateway.contract_scene_queue_protocol import SceneQueueProtocol
from .gateway.contract_transport_protocol import TransportProtocol
from .gateway.taxonomy_gateway_error import (
    AuthenticationError,
    ChannelConflictError,
    ConnectionError,
    GatewayError,
    PayloadLimitError,
    ProtocolVersionMismatchError,
    SecurityViolationError,
    TimeoutError,
    TransportParseError,
)
from .gateway.taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    ConnectionConfigVO,
    ConnectionOutcomeVO,
    ConnectionState,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportOutcomeVO,
    TransportType,
)

# === Job domain exports ===
from .job.taxonomy_job_constant import (
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
)
from .job.taxonomy_job_vo import JobStatusSnapshot

# === Launcher domain exports ===
from .launcher.contract_launch_protocol import LaunchProtocol
from .launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate
from .launcher.contract_locate_register_protocol import LocateRegisterProtocol
from .launcher.contract_persist_state_protocol import PersistStateProtocol
from .launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from .launcher.contract_shutdown_protocol import ShutdownProtocol
from .launcher.taxonomy_launcher_vo import (
    ExecutableReferenceVO,
    LauncherConfigVO,
    LaunchOutcomeVO,
    PersistenceOutcomeVO,
    RegistrationOutcomeVO,
    RegistrationSource,
    RuntimeState,
    RuntimeStateVO,
    RuntimeStatusVO,
    ShutdownOutcomeVO,
    StatePersistenceOutcomeVO,
    StatusCheckOutcomeVO,
    VersionCompatibility,
)
from .object.contract_apply_modifier_protocol import ApplyModifierProtocol
from .object.contract_create_primitive_protocol import CreatePrimitiveProtocol
from .object.contract_delete_object_protocol import DeleteObjectProtocol
from .object.contract_get_object_info_protocol import GetObjectInfoProtocol
from .object.contract_place_asset_protocol import PlaceAssetProtocol
from .object.contract_set_material_protocol import SetMaterialProtocol
from .object.contract_set_transform_protocol import SetObjectTransformProtocol

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
from .render.contract_render_camera_config_protocol import IRenderCameraConfigProtocol
from .render.contract_render_hdri_config_protocol import IRenderHdriConfigProtocol
from .render.contract_render_scene_image_protocol import IRenderSceneImageProtocol
from .render.contract_render_viewport_capture_protocol import IRenderViewportCaptureProtocol

# === Render domain exports ===
from .render.taxonomy_render_vo import (
    CameraConfigVO,
    HdriConfigVO,
    RenderSceneVO,
    ViewportCaptureVO,
)

# Protocols (business behavior contracts)
from .scene.contract_scene_cleanup_protocol import ISceneCleanupProtocol
from .scene.contract_scene_inspection_protocol import ISceneInspectionProtocol
from .scene.taxonomy_scene_vo import (
    SceneCleanupVO,
    SceneInspectionVO,
)

# Telemetry domain — Protocols (recording, classification, session, enrichment)
from .telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationProtocol,
)
from .telemetry.contract_telemetry_enrichment_protocol import TelemetryEnrichmentProtocol
from .telemetry.contract_telemetry_recording_protocol import TelemetryRecordingProtocol
from .telemetry.contract_telemetry_session_protocol import TelemetrySessionProtocol

# === Telemetry domain exports ===
from .telemetry.taxonomy_event_constant import (
    EVENT_TYPE_CONNECTION,
    EVENT_TYPE_ERROR,
    EVENT_TYPE_PROMPT_SENT,
    EVENT_TYPE_STARTUP,
    EVENT_TYPE_TOOL_EXECUTION,
)
from .telemetry.taxonomy_telemetry_event import TelemetryCategory as _TelemetryCategory
from .telemetry.taxonomy_telemetry_event import TelemetryEvent

__all__ = [
    "asset",
    "common",
    "config",
    "diagnostics",
    "dispatcher",
    "job",
    "launcher",
    "object",
    "render",
    "scene",
    "telemetry",
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
    "Vector3D",
    "BoundingBox",
    "AssetMetadata",
    "AssetMetadataItem",
    "AssetMetadataVO",
    "ImportedAsset",
    "SceneInfo",
    "PlaceAssetVO",
    "GetObjectInfoVO",
    "SetObjectTransformVO",
    "DeleteObjectVO",
    "CreatePrimitiveVO",
    "SetMaterialVO",
    "ApplyModifierVO",
    "AssetSearchVO",
    "AssetDownloadVO",
    "AssetDownloadCacheVO",
    "AssetExtractArchiveVO",
    "AssetImportBlenderVO",
    "ImportGlbVO",
    "ExportModelVO",
    "GetScreenshotVO",
    "RenderVO",
    "CameraSetupVO",
    "HdriSetupVO",
    "CameraConfigVO",
    "HdriConfigVO",
    "BlenderObject",
    "JobStatusSnapshot",
    "BlenderMCPError",
    "DomainError",
    "SceneValidationError",
    "AssetNotFoundError",
    "ValidationError",
    "ProviderError",
    "ExecutionError",
    "BlenderConnectionError",
    "InvalidCommandError",
    "TelemetryEvent",
    "_TelemetryCategory",
    "ASSET_TYPE_HDRIS",
    "ASSET_TYPE_TEXTURES",
    "ASSET_TYPE_MODELS",
    "PROVIDER_POLYHAVEN",
    "PROVIDER_SKETCHFAB",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "IRenderCameraConfigProtocol",
    "IRenderHdriConfigProtocol",
    "IRenderSceneImageProtocol",
    "IRenderViewportCaptureProtocol",
    "RenderSceneVO",
    "ViewportCaptureVO",
    "ISceneCleanupProtocol",
    "ISceneInspectionProtocol",
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
    "OBJECT_TYPE_POINTCLOUD",
    "ALLOWED_OBJECT_TYPES",
    "COMMAND_CATALOG",
    "CommandSpec",
    "ACTION_NAMES",
    "RENDER_ENGINE_CYCLES",
    "RENDER_ENGINE_EEVEE",
    "EVENT_TYPE_STARTUP",
    "EVENT_TYPE_TOOL_EXECUTION",
    "EVENT_TYPE_PROMPT_SENT",
    "EVENT_TYPE_CONNECTION",
    "EVENT_TYPE_ERROR",
    "create_asset_id",
    "create_object_id",

    "create_provider_name",

    "SceneCleanupVO",
    "SceneInspectionVO",
    "PlaceAssetProtocol",
    "CreatePrimitiveProtocol",
    "SetObjectTransformProtocol",
    "SetMaterialProtocol",
    "ApplyModifierProtocol",
    "DeleteObjectProtocol",
    "GetObjectInfoProtocol",
    "AssetSearchProtocol",
    "AssetDownloadProtocol",
    "AssetExtractProtocol",
    "AssetImportProtocol",
    "AssetProviderProtocol",
    "IAssetAggregate",
    "WorkflowProtocol",
    "ExecuteActionProtocol",
    "CommandCatalogProtocol",

    "TelemetryClassificationProtocol",
    "TelemetryEnrichmentProtocol",
    "TelemetryRecordingProtocol",
    "TelemetrySessionProtocol",
    "IDiagnosticsAggregate",
    "IConfigAggregate",
    "ISettingsLoaderProtocol",
    "ISettingsRetrieverProtocol",
    "IWorkspaceResolverProtocol",
    "ISettingsMetadataProtocol",
    "IRedactionRulesProtocol",
    "SettingsSnapshot",
    "WorkspacePath",
    "RedactionRule",
    "SettingsLoadedEvent",
    "SettingsReloadEvent",
    "WorkspaceResolvedEvent",
    "SettingsValidationWarningEvent",
    "SENSITIVE_KEY_PATTERNS",
    "PROJECT_MARKERS",
    "MAX_CONFIG_SIZE_BYTES",
    "ENV_PREFIX_PRODUCT",
    "REDACTION_PLACEHOLDER",
    "POLICY_MODE_STRICT",
    "POLICY_MODE_PERMISSIVE",
    "DEFAULT_POLICY_MODE",
    "ActionDiscoveryProtocol",
    "BackgroundSubmitProtocol",
    "CatalogRegistrationProtocol",
    "RequestValidationProtocol",
    "ResultNormalizationProtocol",
    "SyncDispatchProtocol",
    "ActionMetadataVO",
    "ActionCommandVO",
    "DiscoveryOutcomeVO",
    "UnifiedResultEnvelopeVO",
    "LaunchProtocol",
    "ILauncherOperateAggregate",
    "LocateRegisterProtocol",
    "PersistStateProtocol",
    "RuntimeStatusProtocol",
    "ShutdownProtocol",
    "ExecutableReferenceVO",
    "LauncherConfigVO",
    "LaunchOutcomeVO",
    "PersistenceOutcomeVO",
    "RegistrationOutcomeVO",
    "RegistrationSource",
    "RuntimeState",
    "RuntimeStateVO",
    "RuntimeStatusVO",
    "ShutdownOutcomeVO",
    "StatusCheckOutcomeVO",
    "StatePersistenceOutcomeVO",
    "VersionCompatibility",
    "ConnectionProtocol",
    "ConnectionMaintenanceProtocol",
    "TransportProtocol",
    "SceneQueueProtocol",
    "CodeExecutionProtocol",
    "GatewayError",
    "ConnectionError",
    "TimeoutError",
    "ProtocolVersionMismatchError",
    "AuthenticationError",
    "ChannelConflictError",
    "SecurityViolationError",
    "TransportParseError",
    "PayloadLimitError",
    "ConnectionState",
    "TransportType",
    "ConnectionConfigVO",
    "ConnectionOutcomeVO",
    "ConnectionStatusVO",
    "TransportMessageVO",
    "TransportOutcomeVO",
    "SceneOperationVO",
    "SceneOperationOutcomeVO",
    "QueueStatusVO",
    "CodeExecutionVO",
    "CodeExecutionOutcomeVO",
]
