"""Security domain contract: validate path protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-001: Validate File Path Access.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import PathValidationVO


class ValidatePathProtocol(ABC):
    """Protocol interface for validating filesystem path access."""

    @abstractmethod
    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """Validate whether a filesystem path is allowed for the requested access mode."""
        ...