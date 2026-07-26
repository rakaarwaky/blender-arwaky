"""Asset domain contract: import into Blender protocol (ABC based).

Defines the protocol for importing locally available asset files
into Blender with object reference handoff.

FR-AST-004: Import Asset into Blender
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    AssetType,
    FilePath,
    ObjectName,
)


class AssetImportProtocol(ABC):
    """Protocol for importing asset files into Blender.

    FR-AST-004: Transports import command through gateway feature,
    returns canonical object references, preserves license and
    attribution metadata. Responsibility ends at object reference
    handoff; subsequent manipulation belongs to object feature.
    """

    @abstractmethod
    async def import_asset(
        self,
        file_path: FilePath,
        asset_type: AssetType,
        target_collection: str | None = None,
        scale_normalization: bool = False,
        duplicate_policy: str = "rename",
        format_hint: str | None = None,
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
            Dict with success indicator, imported object references,
            imported asset metadata summary including license attribution,
            and message.
        """
        ...
