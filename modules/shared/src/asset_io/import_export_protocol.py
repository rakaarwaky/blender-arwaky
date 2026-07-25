"""Asset I/O domain contract: import/export protocol (ABC based)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_import_export_vo import (
    ExportModelRequestVO,
    ExportModelResponseVO,
    ImportGlbRequestVO,
    ImportGlbResponseVO,
)


class ImportExportProtocol(ABC):
    """Protocol interface for external file operations (GLB/OBJ)."""

    @abstractmethod
    async def import_glb(
        self, request: ImportGlbRequestVO
    ) -> ImportGlbResponseVO:
        """Import a 3D model into Blender."""
        pass

    @abstractmethod
    async def export_model(
        self, request: ExportModelRequestVO
    ) -> ExportModelResponseVO:
        """Export Blender objects to file."""
        pass
