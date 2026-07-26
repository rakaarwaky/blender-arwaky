"""BlenderArwaky shared domain types — taxonomy + contract layers.

Organized by domain:
- common/: Core cross-cutting
- object/: Object domain
- render/: Render domain
- job/: Job domain VOs
- telemetry/: Telemetry domain
- diagnostics/: Diagnostics observability protocols
"""

# MCP domain — Protocols (server lifecycle, discovery, execute, health, response)
from modules.mcp.src.contract_server_bootstrap import ServerBootstrapManagerAggregate

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
from .asset.contract_asset_download_protocol import AssetDownloadProtocol
from .asset.contract_asset_extract_protocol import AssetExtractProtocol
from .asset.contract_asset_import_protocol import AssetImportProtocol
from .asset.contract_asset_provider import AssetProviderPort
from .asset.contract_asset_provider_metadata_protocol import AssetProviderMetadataProtocol
from .asset.contract_asset_search_protocol import AssetSearchProtocol
from .asset.contract_import_export_protocol import ImportExportProtocol
from .asset.contract_polyhaven_api import PolyhavenApiPort
from .asset.contract_sketchfab_api import SketchfabApiPort

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

# CLI domain — Protocols (command routing, render output, error display)
from .cli.contract_cli_command_protocol import CliCommandProtocol
from .cli.contract_cli_error_protocol import CliErrorProtocol
from .cli.contract_cli_render_protocol import CliRenderProtocol

# Protocols (inbound behavior interfaces — Capabilities implement these)
from .common.contract_command_catalog import CommandCatalogPort
from .common.contract_execute_action_protocol import ExecuteActionProtocol
from .common.contract_workflow_protocol import WorkflowProtocol
from .common.taxonomy_app_config_vo import ApplicationConfig
from .common.taxonomy_bounding_box_vo import BoundingBox
from .common.taxonomy_command_catalog_constant import (
    ACTION_NAMES,
    COMMAND_CATALOG,
    CommandCatalog,
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
from .diagnostics.contract_audit_emission_protocol import AuditEmissionProtocol
from .diagnostics.contract_diagnostics_snapshot_protocol import DiagnosticsSnapshotProtocol

# Diagnostics domain — Protocols (health, metrics, audit, logging, snapshot)
from .diagnostics.contract_health_composition_protocol import HealthCompositionProtocol
from .diagnostics.contract_logging_policy_protocol import LoggingPolicyProtocol
from .diagnostics.contract_metrics_collection_protocol import MetricsCollectionProtocol
from .job.contract_job_cancel_protocol import JobCancelProtocol
from .job.contract_job_cleanup_protocol import JobCleanupProtocol
from .job.contract_job_monitor_protocol import JobMonitorProtocol
from .job.contract_job_tracker_protocol import JobTrackerProtocol

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

# === Dispatcher domain exports ===
from .dispatcher.contract_action_discovery_protocol import ActionDiscoveryProtocol
from .dispatcher.contract_background_submit_protocol import BackgroundSubmitProtocol
from .dispatcher.contract_catalog_registration_protocol import CatalogRegistrationProtocol
from .dispatcher.contract_request_validation_protocol import RequestValidationProtocol
from .dispatcher.contract_result_normalization_protocol import ResultNormalizationProtocol
from .dispatcher.contract_sync_dispatch_protocol import SyncDispatchProtocol
from .dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from .dispatcher.taxonomy_action_request_vo import ActionRequestVO
from .dispatcher.taxonomy_discovery_result_vo import DiscoveryResultVO
from .dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

# === Launcher domain exports ===
from .launcher.contract_launch_protocol import LaunchProtocol
from .launcher.contract_launcher_operate_aggregate import LauncherOperateAggregate
from .launcher.contract_locate_register_protocol import LocateRegisterProtocol
from .launcher.contract_persist_state_protocol import PersistStateProtocol
from .launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from .launcher.contract_shutdown_protocol import ShutdownProtocol
from .launcher.taxonomy_launcher_vo import (
    ExecutableReferenceVO,
    LauncherConfigVO,
    LaunchResultVO,
    PersistenceResultVO,
    RegistrationResultVO,
    RegistrationSource,
    RuntimeState,
    RuntimeStateVO,
    RuntimeStatusVO,
    ShutdownResultVO,
    StatusCheckResultVO,
    StatePersistenceResultVO,
    VersionCompatibility,
)

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
    CodeExecutionRequestVO,
    CodeExecutionResultVO,
    ConnectionState,
    ConnectionRequestVO,
    ConnectionResultVO,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationResultVO,
    SceneOperationVO,
    TransportRequestVO,
    TransportResponseVO,
    TransportType,
)

from .mcp.contract_server_discovery_protocol import ServerDiscoveryProtocol
from .mcp.contract_server_execute_protocol import ServerExecuteProtocol
from .mcp.contract_server_health_protocol import ServerHealthProtocol
from .mcp.contract_server_response_protocol import ServerResponseProtocol
from .object.contract_apply_modifier_protocol import ApplyModifierProtocol
from .object.contract_create_primitive_protocol import CreatePrimitiveProtocol
from .object.contract_delete_object_protocol import DeleteObjectProtocol
from .object.contract_get_object_info_protocol import GetObjectInfoProtocol
from .object.contract_object_operate_protocol import ObjectOperateProtocol
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
from .render.contract_camera_config_protocol import CameraConfigProtocol
from .render.contract_hdri_config_protocol import HdriConfigProtocol
from .render.contract_render_operate_protocol import RenderOperateProtocol
from .render.contract_viewport_capture import ViewportCapturePort
from .render.contract_viewport_capture_protocol import ViewportCaptureProtocol

# === Render domain exports ===
from .render.taxonomy_render_vo import (
    CameraConfigVO,
    CameraSetupVO,
    GetScreenshotVO,
    HdriConfigVO,
    HdriSetupVO,
    RenderVO,
)
from .scene.contract_scene_inspection import SceneInspectionPort

# Protocols (business behavior contracts)
from .scene.contract_scene_operate_protocol import SceneOperateProtocol

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
from .telemetry.contract_telemetry_classification import TelemetryClassificationPort

# Telemetry domain — Protocols (recording, classification, session, enrichment)
from .telemetry.contract_telemetry_classification_protocol import TelemetryClassificationProtocol
from .telemetry.contract_telemetry_enrichment import TelemetryEnrichmentPort
from .telemetry.contract_telemetry_enrichment_protocol import TelemetryEnrichmentProtocol
from .telemetry.contract_telemetry_recording import TelemetryRecordingPort
from .telemetry.contract_telemetry_recording_protocol import TelemetryRecordingProtocol
from .telemetry.contract_telemetry_session_management import TelemetrySessionManagementPort
from .telemetry.contract_telemetry_session_protocol import TelemetrySessionProtocol

# === Telemetry domain exports ===
from .telemetry.taxonomy_event_constant import (
    EVENT_TYPE_CONNECTION,
    EVENT_TYPE_ERROR,
    EVENT_TYPE_PROMPT_SENT,
    EVENT_TYPE_STARTUP,
    EVENT_TYPE_TOOL_EXECUTION,
)
from .telemetry.taxonomy_telemetry_event import EventType, TelemetryEvent

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
    "PlaceAssetProtocol",
    "CreatePrimitiveProtocol",
    "SetObjectTransformProtocol",
    "SetMaterialProtocol",
    "ApplyModifierProtocol",
    "DeleteObjectProtocol",
    "GetObjectInfoProtocol",
    "JobTrackerProtocol",
    "JobMonitorProtocol",
    "JobCancelProtocol",
    "JobCleanupProtocol",
    "RenderOperateProtocol",
    "ViewportCaptureProtocol",
    "CameraConfigProtocol",
    "HdriConfigProtocol",
    "ImportExportProtocol",
    "AssetSearchProtocol",
    "AssetDownloadProtocol",
    "AssetExtractProtocol",
    "AssetImportProtocol",
    "AssetProviderMetadataProtocol",
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
    # MCP domain — Protocols (server lifecycle, discovery, execute, health, response)
    "ServerBootstrapManagerAggregate",
    "ServerDiscoveryProtocol",
    "ServerExecuteProtocol",
    "ServerHealthProtocol",
    "ServerResponseProtocol",
    # CLI domain — Protocols (command routing, render output, error display)
    "CliCommandProtocol",
    "CliRenderProtocol",
    "CliErrorProtocol",
    # Telemetry domain — Protocols (recording, classification, session, enrichment)
    "TelemetryClassificationProtocol",
    "TelemetryEnrichmentProtocol",
    "TelemetryRecordingProtocol",
    "TelemetrySessionProtocol",
    # Diagnostics domain — Protocols (health, metrics, audit, logging, snapshot)
    "HealthCompositionProtocol",
    "MetricsCollectionProtocol",
    "AuditEmissionProtocol",
    "LoggingPolicyProtocol",
    "DiagnosticsSnapshotProtocol",
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
    "REDACTION_PLACEHOLDER",
    "POLICY_MODE_STRICT",
    "POLICY_MODE_PERMISSIVE",
    "DEFAULT_POLICY_MODE",
    # Dispatcher domain — Protocols
    "ActionDiscoveryProtocol",
    "BackgroundSubmitProtocol",
    "CatalogRegistrationProtocol",
    "RequestValidationProtocol",
    "ResultNormalizationProtocol",
    "SyncDispatchProtocol",
    # Dispatcher domain — Value Objects
    "ActionMetadataVO",
    "ActionRequestVO",
    "DiscoveryResultVO",
    "UnifiedResultEnvelopeVO",
    # Launcher domain — Protocols
    "LaunchProtocol",
    "LauncherOperateAggregate",
    "LocateRegisterProtocol",
    "PersistStateProtocol",
    "RuntimeStatusProtocol",
    "ShutdownProtocol",
    # Launcher domain — Value Objects & Enums
    "ExecutableReferenceVO",
    "LauncherConfigVO",
    "LaunchResultVO",
    "PersistenceResultVO",
    "RegistrationResultVO",
    "RegistrationSource",
    "RuntimeState",
    "RuntimeStateVO",
    "RuntimeStatusVO",
    "ShutdownResultVO",
    "StatusCheckResultVO",
    "StatePersistenceResultVO",
    "VersionCompatibility",
    # Gateway domain — Protocols
    "ConnectionProtocol",
    "ConnectionMaintenanceProtocol",
    "TransportProtocol",
    "SceneQueueProtocol",
    "CodeExecutionProtocol",
    # Gateway domain — Errors
    "GatewayError",
    "ConnectionError",
    "TimeoutError",
    "ProtocolVersionMismatchError",
    "AuthenticationError",
    "ChannelConflictError",
    "SecurityViolationError",
    "TransportParseError",
    "PayloadLimitError",
    # Gateway domain — Value Objects & Enums
    "ConnectionState",
    "TransportType",
    "ConnectionRequestVO",
    "ConnectionResultVO",
    "ConnectionStatusVO",
    "TransportRequestVO",
    "TransportResponseVO",
    "SceneOperationVO",
    "SceneOperationResultVO",
    "QueueStatusVO",
    "CodeExecutionRequestVO",
    "CodeExecutionResultVO",
]
