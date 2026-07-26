"""Handler: Import/Export file exchange operations.

Implements ImportExportProtocol for GLB import and model export operations.
Depends on ICodeExecutionProtocol for Blender code execution (not raw port).
"""

import logging

from modules.gateway.src.contract_code_execution_protocol import ICodeExecutionProtocol
from modules.shared.src.asset.contract_import_export_protocol import ImportExportProtocol
from modules.shared.src.asset.taxonomy_asset_vo import ExportModelVO, ImportGlbVO
from modules.shared.src.common.taxonomy_core_vo import ObjectName, Prompt

logger = logging.getLogger("BlenderMCPServer")


class ImportExportExecutor(ImportExportProtocol):
    """Business logic for file exchange operations."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def import_glb(self, request: ImportGlbVO) -> ImportGlbVO:
        """Import a GLB/GLTF file into the Blender scene.

        FR-IMP-001: Imports the specified file path, optionally renames
        the active object to the requested name.
        """
        logger.info("Importing GLB from %s", request.file_path)
        safe_path = ImportExportExecutor._safe_str(str(request.file_path))
        code = f"import bpy\nbpy.ops.import_scene.gltf(filepath={safe_path})\n"
        if request.object_name:
            safe_name = ImportExportExecutor._safe_str(str(request.object_name))
            code += f"imported_obj = bpy.context.active_object\nif imported_obj:\n    imported_obj.name = {safe_name}\n"
        try:
            await self._executor.execute_blender_code(Prompt(code))
            return ImportGlbVO(
                file_path=request.file_path,
                object_name=request.object_name or ObjectName("ImportedModel"),
                success=True,  # type: ignore[arg-type]
                message="Import successful",
            )
        except Exception as e:
            logger.error("Import failed: %s", e)
            raise RuntimeError(f"Import failed: {e}") from e

    async def export_model(self, request: ExportModelVO) -> ExportModelVO:
        """Export a Blender object to GLTF format.

        FR-IMP-002: Selects the named object and exports it to the specified path.
        """
        logger.info("Exporting model %s to %s", request.object_name, request.file_path)
        code = (
            "import bpy\n"
            f"obj = bpy.data.objects.get('{request.object_name}')\n"
            f"if obj:\n"
            "    bpy.ops.object.select_all(action='DESELECT')\n"
            "    obj.select_set(True)\n"
            "    bpy.context.view_layer.objects.active = obj\n"
            f"    bpy.ops.export_scene.gltf(filepath='{request.file_path}', use_selection=True)\n"
        )
        try:
            await self._executor.execute_blender_code(Prompt(code))
            return ExportModelVO(
                object_name=request.object_name,
                file_path=request.file_path,
                export_format=request.export_format,
                success=True,  # type: ignore[arg-type]
                message="Export successful",
            )
        except Exception as e:
            logger.error("Export failed: %s", e)
            raise RuntimeError(f"Export failed: {e}") from e

    # ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    @staticmethod
    def _safe_str(value: object) -> str:
        """Safely escape a string for inclusion in generated Python code."""
        import json

        return json.dumps(str(value))
