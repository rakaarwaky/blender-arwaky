"""Asset domain contract: import into Blender protocol (ABC based).

Defines the protocol for importing locally available asset files
into Blender with object reference handoff.

FR-AST-004: Import Asset into Blender
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_asset_vo import AssetImportBlenderVO


class AssetImportProtocol(ABC):
    """Protocol for importing asset files into Blender."""

    @abstractmethod
    async def import_asset(self, vo: AssetImportBlenderVO) -> AssetImportBlenderVO:
        """Import a locally available asset file into Blender.

        FR-AST-004: Transports import command through gateway feature,
        returns canonical object references, preserves license and
        attribution metadata. Responsibility ends at object reference
        handoff.
        """
        ...
