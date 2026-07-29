"""Capability: Asset import into Blender (FR-AST-004).

Implements AssetImportProtocol for importing locally available asset files
into Blender with object reference handoff.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from modules.shared.src.asset.contract_asset_import_protocol import AssetImportProtocol
from modules.shared.src.common.taxonomy_core_vo import (
    AssetCollectionName,
    AssetFormatHint,
    AssetType,
    FilePath,
)
from modules.shared.src.asset.utility.utility_file_format_detector import detect_format_by_magic
from modules.shared.src.gateway.contract_gateway_client_protocol import GatewayClientProtocol

logger = logging.getLogger("BlenderMCPServer")


class AssetImportCapability(AssetImportProtocol):
    """Asset import capability with object reference handoff.

    FR-AST-004: Transports import command through gateway feature,
    returns canonical object references, preserves license and
    attribution metadata. Responsibility ends at object reference
    handoff; subsequent manipulation belongs to object feature.
    """

    def __init__(
        self,
        gateway_client: GatewayClientProtocol | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            gateway_client: Gateway feature for Blender import transport.
            config_getter: Config feature for settings and policies.
        """
        self.gateway_client = gateway_client
        self.config_getter = config_getter

    async def import_asset(
        self,
        file_path: FilePath,
        asset_type: AssetType,
        target_collection: AssetCollectionName | None = None,
        scale_normalization: bool = False,
        duplicate_policy: str = "rename",
        format_hint: AssetFormatHint | None = None,
    ) -> dict[str, Any]:
        """Import a locally available asset file into Blender.

        FR-AST-004: File must exist locally before import. Import command
        transported through gateway feature. Supported formats depend on
        runtime capability. Scale normalization and duplicate handling
        policies applied. Result returns canonical object references.

        Args:
            file_path: Path to the local asset file.
            asset_type: Type of asset being imported.
            target_collection: Optional target collection name.
            scale_normalization: Whether to normalize scale to scene units.
            duplicate_policy: rename/reuse/replace/reject for duplicates.
            format_hint: Optional format hint for import plugin selection.

        Returns:
            Dict with success, object_names, asset_name, license_summary,
            and message.
        """
        # Validate file exists locally
        if not Path(file_path).exists():
            return {
                "success": False,
                "object_names": [],
                "asset_name": None,
                "license_summary": None,
                "message": f"Local file not found: {file_path}. Run download operation first.",
                "error": "missing_local_file",
            }

        # Validate file is not empty
        if Path(file_path).stat().st_size == 0:
            return {
                "success": False,
                "object_names": [],
                "asset_name": None,
                "license_summary": None,
                "message": f"File is empty: {file_path}",
                "error": "empty_file",
            }

        # Validate supported format (extension + magic bytes)
        if not self._is_supported_format(file_path, asset_type, format_hint):
            return {
                "success": False,
                "object_names": [],
                "asset_name": None,
                "license_summary": None,
                "message": f"Unsupported format for {asset_type} import",
                "error": "unsupported_format",
            }

        # Build import command for gateway
        import_command = self._build_import_command(
            file_path, asset_type, target_collection, scale_normalization, duplicate_policy, format_hint
        )

        # Transport through gateway
        try:
            result = await self.gateway_client.execute_command(import_command)
            return {
                "success": True,
                "object_names": result.get("object_names", []),
                "asset_name": result.get("asset_name"),
                "license_summary": result.get("license_summary"),
                "message": f"Imported {len(result.get('object_names', []))} objects from {file_path}",
                "import_timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except Exception as e:
            logger.error("Blender import failed for %s: %s", file_path, e)
            return {
                "success": False,
                "object_names": [],
                "asset_name": None,
                "license_summary": None,
                "message": f"Blender import failed: {e}",
                "error": str(e),
            }

    def _is_supported_format(
        self, file_path: str, asset_type: AssetType, format_hint: AssetFormatHint | None
    ) -> bool:
        """Check if file format is supported for import.

        Validates both the file extension and the actual content
        via magic bytes detection (FR-AST-004 / L04).
        """
        supported_formats = {
            "model": [".glb", ".gltf", ".fbx", ".obj", ".mtl", ".dae"],
            "texture": [".png", ".jpg", ".jpeg", ".exr", ".tga"],
            "hdri": [".hdr", ".exr"],
        }

        ext = Path(file_path).suffix.lower().lstrip(".")
        valid_formats = supported_formats.get(str(asset_type), [])

        # Extension check (fast path)
        if f".{ext}" in valid_formats:
            # L04: Also validate via magic bytes
            detected = detect_format_by_magic(file_path)
            if detected is not None and detected != ext and detected not in valid_formats:
                return False
            return True

        # No extension match — try magic bytes as fallback
        detected = detect_format_by_magic(file_path)
        if detected is not None and detected in valid_formats:
            return True

        # format_hint can override format detection
        if format_hint is not None:
            return True

        return False

    def _build_import_command(
        self,
        file_path: str,
        asset_type: AssetType,
        target_collection: AssetCollectionName | None,
        scale_normalization: bool,
        duplicate_policy: str,
        format_hint: AssetFormatHint | None,
    ) -> dict[str, Any]:
        """Build import command for gateway transport."""
        command = {
            "type": "import",
            "file_path": file_path,
            "asset_type": str(asset_type),
        }

        if target_collection:
            command["target_collection"] = target_collection

        if scale_normalization:
            command["scale_normalization"] = True

        if duplicate_policy != "rename":
            command["duplicate_policy"] = duplicate_policy

        if format_hint:
            command["format_hint"] = format_hint

        return command
