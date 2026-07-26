"""Security domain contract: redact sensitive protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-004: Redact Sensitive Values.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import RedactionVO


class RedactSensitiveProtocol(ABC):
    """Protocol interface for detecting and redacting sensitive values."""

    @abstractmethod
    async def redact(self, request: RedactionVO) -> RedactionVO:
        """Detect and redact sensitive values from text or structured data."""
        ...
