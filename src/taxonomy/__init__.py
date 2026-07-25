"""Taxonomy barrel: re-export all domain model entities, errors, and value objects.

All types are defined in modules/shared/src/ with proper AES taxonomy naming:
  taxonomy_<domain>_<vo|entity|error|event|constant>.py
This file provides backward-compatible imports for existing layer files.
"""

# Re-export everything from modules.shared.src (organized by domain)
from modules.shared.src import (
    ActionName,
    AssetCount,
    AssetId,
    AssetIdList,
    AssetMetadata,
    AssetName,
    AssetNotFoundError,
    AssetType,
    AssetTypeFilter,
    BBoxIntegers,
    BlenderConnectionFailure,
    BlenderMCPError,
    BlenderObject,
    BlenderObjectList,
    BlenderVersion,
    BoundingBox,
    CapabilityRef,
    CleanupMode,
    CommandCatalog,
    COMMAND_CATALOG,
    ConfigPath,
    ConfigValue,
    ConnectionError,
    ConnectionFailure,
    CoordinateList,
    CustomerUuid,
    Details,
    DirectoryPath,
    DomainError,
    DomainRef,
    DurationMs,
    EnabledFlag,
    ErrorString,
    ErrorMessage,
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
    JobStatus,
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
    ProviderError,
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
    SceneInfo,
    SceneRuleSetName,
    SceneValidationError,
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
    TelemetryEvent,
    ThumbnailUrl,
    Timestamp,
    ToolName,
    ValidationError,
    Vector3D,
    VersionString,
    WorkflowName,
)

# Scene request/response VOs
from modules.shared.src import (
    CleanupSceneRequestVO,
    CleanupSceneResponseVO,
    GetSceneInfoRequestVO,
    GetSceneInfoResponseVO,
    SetupEnvironmentRequestVO,
    SetupEnvironmentResponseVO,
)

# Object request/response VOs
from modules.shared.src.object.taxonomy_object_request_vo import (
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

# Render request/response VOs
from modules.shared.src.render.taxonomy_render_request_vo import (
    GetScreenshotRequestVO,
    RenderRequestVO,
    RenderResponseVO,
    ScreenshotResponseVO,
)

# Asset request/response VOs
from modules.shared.src.asset_provider.taxonomy_asset_request_vo import (
    AssetDownloadRequestVO,
    AssetDownloadResponseVO,
    AssetSearchRequestVO,
    AssetSearchResponseVO,
)

# Import/Export VOs
from modules.shared.src.asset_io.taxonomy_import_export_vo import (
    ExportModelRequestVO,
    ExportModelResponseVO,
    ImportGlbRequestVO,
    ImportGlbResponseVO,
)

# Asset constants
from modules.shared.src.asset_provider.taxonomy_asset_constant import (
    ASSET_TYPE_HDRIS,
    ASSET_TYPE_MODELS,
    ASSET_TYPE_TEXTURES,
    PROVIDER_POLYHAVEN,
    PROVIDER_SKETCHFAB,
)

# Object constants
from modules.shared.src.object.taxonomy_object_constant import (
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

# Job state constants
from modules.shared.src.job.taxonomy_job_state_constant import (
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
)

# Command catalog
from modules.shared.src.common.taxonomy_command_catalog_constant import (
    ACTION_NAMES,
    COMMAND_CATALOG,
    CommandSpec,
)

# Errors (ConnectionFailure alias for N818)
from modules.shared.src.common.taxonomy_domain_error import (
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

# Value objects
from modules.shared.src.common.taxonomy_vector3d_vo import Vector3D
from modules.shared.src.common.taxonomy_bounding_box_vo import BoundingBox
from modules.shared.src.asset_provider.taxonomy_asset_data_vo import (
    AssetMetadata,
    ImportedAsset,
    create_asset_id,
    create_provider_name,
)
from modules.shared.src.scene.taxonomy_scene_info_vo import SceneInfo
from modules.shared.src.common.taxonomy_app_config_vo import ApplicationConfig

# Entities
from modules.shared.src.object.taxonomy_blender_object_entity import (
    BlenderObject,
    create_object_id,
)
from modules.shared.src.job.taxonomy_job_status_entity import (
    JobStatus,
    create_job_id,
    create_progress,
)

# Events
from modules.shared.src.telemetry.taxonomy_telemetry_event import EventType, TelemetryEvent

# Backward-compatible aliases
ConnectionFailure = ConnectionError
ApplicationConfigVo = ApplicationConfig


class CommandCatalog:
    """Canonical command catalog wrapper for backward compatibility."""

    COMMAND_CATALOG = COMMAND_CATALOG

    @staticmethod
    def list_actions() -> list[str]:
        return ACTION_NAMES


list_actions = CommandCatalog.list_actions


__all__ = [
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
    # Branded IDs
    "UserId",
    "SceneId",
    "ObjectName",
    "AssetId",
    "JobId",
    "ProviderName",
    "HdriId",
    "ParentId",
    "ObjectId",
    # Text VOs
    "Prompt",
    "ActionName",
    "RenderEngine",
    "ErrorString",
    # Asset/Render/Image/Material VOs
    "AssetType",
    "ImageFormat",
    "PrimitiveType",
    "ExportFormat",
    "MaterialName",
    "ModifierName",
    "RuleName",
    "WorkflowName",
    "SceneRuleSetName",
    # Additional VOs
    "ObjectType",
    "AssetName",
    "JobState",
    "ResultUrl",
    "FilePath",
    "DirectoryPath",
    "CleanupMode",
    "SearchQuery",
    "AssetTypeFilter",
    "ResultLimit",
    "NextPageToken",
    "CoordinateList",
    "ScaleVector",
    "RotationVector",
    "AssetCount",
    "RenderSamples",
    "MaxImageSize",
    "RenderTime",
    "Details",
    "ObjectIdList",
    "BlenderObjectList",
    # Numeric VOs
    "MaxSize",
    "SampleCount",
    "IterationCount",
    "ResolutionX",
    "ResolutionY",
    "PortNumber",
    "ObjectCount",
    "LightStrength",
    # Flags
    "UseDenoising",
    "EnabledFlag",
    "SuccessFlag",
    # Surface-typed primitives
    "SkillName",
    "SectionRef",
    "ServerName",
    "DomainRef",
    "FormatRef",
    "CapabilityRef",
    "ExitCode",
    # Collections
    "AssetIdList",
    "StringList",
    "TagList",
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
    "ConfigPath",
    "ConfigValue",
    # Entity models
    "BlenderObject",
    "SceneInfo",
    "JobStatus",
    "AssetMetadata",
    "ImportedAsset",
    # Object type constants
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
    # Render engine constants
    "ASSET_TYPE_HDRIS",
    "ASSET_TYPE_TEXTURES",
    "ASSET_TYPE_MODELS",
    "PROVIDER_POLYHAVEN",
    "PROVIDER_SKETCHFAB",
    # Job state constants
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    # Progress
    "Progress",
    "ThumbnailUrl",
    # Factories
    "create_asset_id",
    "create_object_id",
    "create_job_id",
    "create_provider_name",
    "create_progress",
    # Rich value objects
    "Vector3D",
    "BoundingBox",
    # Telemetry
    "EventType",
    "TelemetryEvent",
    # Command Catalog Data
    "CommandCatalog",
    "COMMAND_CATALOG",
    "CommandSpec",
    "list_actions",
    # Application Configuration
    "ApplicationConfig",
    "ApplicationConfigVo",
    # Scene Request/Response VOs
    "CleanupSceneRequestVO",
    "CleanupSceneResponseVO",
    "GetSceneInfoRequestVO",
    "GetSceneInfoResponseVO",
    "SetupEnvironmentRequestVO",
    "SetupEnvironmentResponseVO",
    # Object Request/Response VOs
    "PlaceAssetRequestVO",
    "PlaceAssetResponseVO",
    "GetObjectInfoRequestVO",
    "GetObjectInfoResponseVO",
    "SetObjectTransformRequestVO",
    "SetObjectTransformResponseVO",
    "DeleteObjectRequestVO",
    "DeleteObjectResponseVO",
    "CreatePrimitiveRequestVO",
    "CreatePrimitiveResponseVO",
    "SetMaterialRequestVO",
    "SetMaterialResponseVO",
    "ApplyModifierRequestVO",
    "ApplyModifierResponseVO",
    # Render Request/Response VOs
    "GetScreenshotRequestVO",
    "ScreenshotResponseVO",
    "RenderRequestVO",
    "RenderResponseVO",
    # Asset Request/Response VOs
    "AssetSearchRequestVO",
    "AssetSearchResponseVO",
    "AssetDownloadRequestVO",
    "AssetDownloadResponseVO",
    # Import/Export VOs
    "ImportGlbRequestVO",
    "ImportGlbResponseVO",
    "ExportModelRequestVO",
    "ExportModelResponseVO",
]
