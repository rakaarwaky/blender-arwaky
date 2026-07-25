"""Import/Export operation request and response value objects."""

from __future__ import annotations

from dataclasses import dataclass

from ..common.taxonomy_core_vo import (
    ExportFormat,
    ObjectName,
    SuccessFlag,
)


@dataclass(frozen=True)
class ImportGlbRequestVO:
    """Request to import a GLB/GLTF model."""

    file_path: str
    object_name: ObjectName | None = None


@dataclass(frozen=True)
class ImportGlbResponseVO:
    """Response from a GLB import operation."""

    success: SuccessFlag
    object_name: ObjectName
    file_path: str
    message: str


@dataclass(frozen=True)
class ExportModelRequestVO:
    """Request to export a model."""

    object_name: ObjectName
    file_path: str
    export_format: ExportFormat | None = None


@dataclass(frozen=True)
class ExportModelResponseVO:
    """Response from an export operation."""

    success: SuccessFlag
    file_path: str
    object_name: ObjectName
    message: str
