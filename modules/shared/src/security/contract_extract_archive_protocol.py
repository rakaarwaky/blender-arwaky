"""Security domain contract: extract archive protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-002: Safely Extract Archive.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import ArchiveExtractionVO


class ExtractArchiveProtocol(ABC):
    """Protocol interface for validating archive extraction safety."""

    @abstractmethod
    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """Validate and guard archive extraction against safety policy."""
        ...