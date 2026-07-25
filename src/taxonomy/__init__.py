"""Taxonomy barrel: re-export all domain model entities, errors, and value objects.

All types are defined in modules/shared/src/blender_arwaky/ with proper AES prefixes.
This file provides backward-compatible imports for existing layer files.
"""

# Core types (NewType branded primitives)
from modules.shared.src.blender_arwaky.constant_core_types import *  # noqa: F401 F403

# Asset type & provider constants
from modules.shared.src.blender_arwaky.constant_asset_types import (  # noqa: F401
    ASSET_TYPE_HDRIS,
    ASSET_TYPE_MODELS,
    ASSET_TYPE_TEXTURES,
    PROVIDER_POLYHAVEN,
    PROVIDER_SKETCHFAB,
    create_provider_name,
)

# Object type constants
from modules.shared.src.blender_arwaky.constant_object_types import (  # noqa: F401
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

# Job state constants & factories
from modules.shared.src.blender_arwaky.constant_job_states import (  # noqa: F401
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    create_job_id,
    create_progress,
)

# Event type constant
from modules.shared.src.blender_arwaky.constant_event_type import EventType  # noqa: F401

# Command catalog
from modules.shared.src.blender_arwaky.constant_command_catalog import (  # noqa: F401
    COMMAND_CATALOG,
    CommandCatalog,
)

# Errors (ConnectionFailure renamed to ConnectionError per N818)
from modules.shared.src.blender_arwaky.error_domain_error import (  # noqa: F401
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
from modules.shared.src.blender_arwaky.vo_vector3d import Vector3D  # noqa: F401
from modules.shared.src.blender_arwaky.vo_bounding_box import BoundingBox  # noqa: F401
from modules.shared.src.blender_arwaky.vo_asset_data import (  # noqa: F401
    AssetMetadata,
    ImportedAsset,
    create_asset_id,
)
from modules.shared.src.blender_arwaky.vo_scene_info import SceneInfo  # noqa: F401
from modules.shared.src.blender_arwaky.vo_app_config import ApplicationConfig  # noqa: F401

# Entities
from modules.shared.src.blender_arwaky.entity_blender_object import (  # noqa: F401
    BlenderObject,
    create_object_id,
)
from modules.shared.src.blender_arwaky.entity_job_status import JobStatus  # noqa: F401

# Events
from modules.shared.src.blender_arwaky.event_telemetry import TelemetryEvent  # noqa: F401

# Backward-compatible aliases
ConnectionFailure = ConnectionError  # type: ignore[misc]  # noqa: A003
ApplicationConfigVo = ApplicationConfig  # type: ignore[misc]  # noqa: A003
CommandSpec = dict[str, any]  # type: ignore[misc]  # noqa: F405

__all__ = [
    # Errors
    "BlenderMCPError",
    "DomainError",
    "SceneValidationError",
    "AssetNotFoundError",
    "ValidationError",
    "ConnectionError",
    "ConnectionFailure",  # deprecated alias
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
    # New VOs added to fix AES006 primitive violations
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
    "ALLOWED_OBJECT_TYPES",
    # Render engine constants
    "RENDER_ENGINE_CYCLES",
    "RENDER_ENGINE_EEVEE",
    # Asset/Provider constants
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
    "create_job_id",
    "create_provider_name",
    "create_object_id",
    "create_progress",
    "create_float_triplet",
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
    # Application Configuration
    "ApplicationConfig",
    "ApplicationConfigVo",  # deprecated alias
]
