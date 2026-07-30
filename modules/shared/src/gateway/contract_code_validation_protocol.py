"""Gateway domain contract: code validation protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
Decouples gateway code execution from the security feature's contract layer.
FR-GWY-005: Code validation is delegated through this gateway-local protocol
so that capabilities depend only on their own feature's contracts.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.security.taxonomy_security_vo import CodeValidationVO


class CodeValidationProtocol(ABC):
    """Synchronous gateway-local abstraction for security code validation."""

    @abstractmethod
    def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Validate untrusted code before execution."""
        ...
