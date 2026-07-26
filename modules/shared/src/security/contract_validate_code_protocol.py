"""Security domain contract: validate code protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-003: Validate Untrusted Code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import CodeValidationVO


class ValidateCodeProtocol(ABC):
    """Protocol interface for validating untrusted code before execution."""

    @abstractmethod
    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Validate untrusted code using static analysis and blocked construct policy."""
        ...