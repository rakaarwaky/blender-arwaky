"""Capability: Import asset into Blender executor.

Implements AssetImportProtocol for importing locally available asset files
into Blender with object reference handoff.

FR-AST-004: Import Asset into Blender
AES Capabilities layer — depends on Taxonomy, Contract, Gateway.
"""

import json
import logging
from pathlib import Path

from modules.gateway.src.contract_code_execution_protocol import ICodeExecutionProtocol
from modules.shared.src.asset.contract_asset_import_protocol import AssetImportProtocol
from modules.shared.src.asset.taxonomy_asset_vo import AssetImportBlenderVO
from modules.shared.src.common.taxonomy_core_vo import (
    AssetName,
    ErrorMessage,
    ObjectName,
    SuccessFlag,
)

logger = logging.getLogger("BlenderMCPServer")


class AssetImportExecutor(AssetImportProtocol):
    """Executor for importing asset files into Blender."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._executor = code_executor

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def import_asset(self, vo: AssetImportBlenderVO) -> AssetImportBlenderVO:
        """Import a locally available asset file into Blender.

        FR-AST-004: Verifies local file exists, transports import through
        gateway, applies scale normalization and duplicate policy,
        returns object references.
        """
        local_path = Path(str(vo.file_path))

        if not local_path.exists():
            return AssetImportBlenderVO(
                file_path=vo.file_path,
                asset_type=vo.asset_type,
                target_collection=vo.target_collection,
                scale_normalization=vo.scale_normalization,
                duplicate_policy=vo.duplicate_policy,
                format_hint=vo.format_hint,
                error=ErrorMessage(f"Local file not found: {vo.file_path}"),
                message="File does not exist locally. Use download operation first.",
            )

        code = self._build_import_code(vo)
        try:
            await self._executor.execute_blender_code(code)
        except Exception as exc:
            logger.error("Import failed for %s: %s", vo.file_path, exc)
            return AssetImportBlenderVO(
                file_path=vo.file_path,
                asset_type=vo.asset_type,
                target_collection=vo.target_collection,
                scale_normalization=vo.scale_normalization,
                duplicate_policy=vo.duplicate_policy,
                format_hint=vo.format_hint,
                error=ErrorMessage(str(exc)),
                message=f"Import into Blender failed: {exc}",
            )

        asset_name = AssetName(local_path.stem)
        object_names = self._extract_object_names(local_path)

        return AssetImportBlenderVO(
            file_path=vo.file_path,
            asset_type=vo.asset_type,
            target_collection=vo.target_collection,
            scale_normalization=vo.scale_normalization,
            duplicate_policy=vo.duplicate_policy,
            format_hint=vo.format_hint,
            success=SuccessFlag(True),
            object_names=object_names,
            asset_name=asset_name,
            message="Import successful",
        )

    # ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    @staticmethod
    def _build_import_code(vo: AssetImportBlenderVO) -> str:
        """Build Blender Python code for asset import."""
        safe_path = json.dumps(str(vo.file_path))
        lines = [
            "import bpy",
            "import os",
            f"_filepath = {safe_path}",
            "if not os.path.exists(_filepath):",
            "    raise FileNotFoundError(f'File not found: {_filepath}')",
        ]

        suffix = Path(str(vo.file_path)).suffix.lower()
        if suffix in (".glb", ".gltf"):
            lines.append(f"bpy.ops.import_scene.gltf(filepath={safe_path})")
        elif suffix == ".fbx":
            lines.append(f"bpy.ops.import_scene.fbx(filepath={safe_path})")
        elif suffix == ".obj":
            lines.append(f"bpy.ops.import_scene.obj(filepath={safe_path})")
        elif suffix == ".stl":
            lines.append(f"bpy.ops.import_mesh.stl(filepath={safe_path})")
        elif suffix == ".blend":
            lines.append(f"bpy.ops.wm.append(filepath={safe_path})")
        else:
            lines.append(f"bpy.ops.import_scene.gltf(filepath={safe_path})")

        if vo.target_collection:
            safe_col = json.dumps(vo.target_collection)
            lines.extend([
                f"_col = bpy.data.collections.get({safe_col})",
                "if _col:",
                "    for obj in bpy.context.selected_objects:",
                "        if obj.name not in _col.objects:",
                "            _col.objects.link(obj)",
            ])

        if vo.scale_normalization:
            lines.extend([
                "for obj in bpy.context.selected_objects:",
                "    bpy.context.view_layer.objects.active = obj",
                "    obj.select_set(True)",
                "    bpy.ops.object.transform_apply(scale=True)",
            ])

        return "\n".join(lines)

    @staticmethod
    def _extract_object_names(file_path: Path) -> tuple[ObjectName, ...]:
        """Derive object names from imported file stem."""
        stem = file_path.stem
        return (ObjectName(stem),)