"""BlenderArwaky shared domain types — taxonomy layer.

Organized by domain:
- common/: Core VOs, errors, constants (cross-cutting)
- scene/: Scene info and request/response VOs
- object/: Blender object entity, constants, request/response VOs
- render/: Render request/response VOs
- asset_io/: Import/export request/response VOs
- asset_provider/: Asset constants and provider VOs
- job/: Job state constants and status entity
- telemetry/: Event constants and telemetry event entity
"""

from . import (
    asset_io,
    asset_provider,
    common,
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
    DomainError,
    ExecutionError,
    InvalidCommandError,
    ProviderError,
    SceneValidationError,
    ValidationError,
)

from .common.taxonomy_command_catalog_constant import (
    ACTION_NAMES,
    COMMAND_CATALOG,
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
]
