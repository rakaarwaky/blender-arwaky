"""Asset I/O domain contract: import/export protocol (ABC based)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_asset_vo import ExportModelVO, ImportGlbVO


class ImportExportProtocol(ABC):
    """Protocol interface for external file operations (GLB/OBJ)."""

    @abstractmethod
    async def import_glb(self, request: ImportGlbVO) -> ImportGlbVO:
        """Import a 3D model into Blender."""
        ...

    @abstractmethod
    async def export_model(self, request: ExportModelVO) -> ExportModelVO:
        """Export Blender objects to file."""
        ...