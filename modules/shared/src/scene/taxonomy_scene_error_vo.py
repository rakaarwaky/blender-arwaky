"""Scene domain error value objects — taxonomy errors.

Error types for scene management operations:
- SceneStateError: scene is in invalid state for requested operation
- ProtectionError: attempted to delete protected object without valid override or confirmation
- ValidationError: invalid cleanup mode, invalid preservation policy, invalid filter, or invalid request concept
- ConfirmationError: destructive operation requires confirmation but confirmation was not provided
- DelegatedDeletionError: object feature failed to delete one or more objects
- CleanupTimeoutError: scene inspection or cleanup exceeded configured time limit
- ConnectionError: gateway or Blender execution channel is unavailable

FR-SCN-001, FR-SCN-002: Error Categories
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SceneStateError(Exception):
    """Scene is in invalid state for requested operation.

    FR-SCN-001, FR-SCN-002: scene state error category.
    """

    object_name: str = ""
    detail: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        msg = f"Scene state error for object '{self.object_name}': {self.detail}" if self.object_name else f"Scene state error: {self.detail}"
        object.__setattr__(self, "__message__", msg)


@dataclass(frozen=True)
class ProtectionError(Exception):
    """Attempted to delete protected object without valid override or confirmation.

    FR-SCN-002: protection error category.
    """

    object_name: str = ""
    protection_reason: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        msg = f"Protection error for object '{self.object_name}': {self.protection_reason}" if self.object_name else f"Protection error: {self.protection_reason}"
        object.__setattr__(self, "__message__", msg)


@dataclass(frozen=True)
class ValidationError(Exception):
    """Invalid cleanup mode, preservation policy, filter, or request concept.

    FR-SCN-001, FR-SCN-002: validation error category.
    """

    detail: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        msg = f"Validation error: {self.detail}" if self.detail else "Validation error: invalid request"
        object.__setattr__(self, "__message__", msg)


@dataclass(frozen=True)
class ConfirmationError(Exception):
    """Destructive operation requires confirmation but confirmation was not provided.

    FR-SCN-002: confirmation error category.
    """

    object_name: str = ""
    detail: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        msg = f"Confirmation error for object '{self.object_name}': {self.detail}" if self.object_name else f"Confirmation error: {self.detail}"
        object.__setattr__(self, "__message__", msg)


@dataclass(frozen=True)
class DelegatedDeletionError(Exception):
    """Object feature failed to delete one or more objects.

    FR-SCN-002: delegated deletion error category.
    """

    object_name: str = ""
    detail: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        msg = f"Delegated deletion error for object '{self.object_name}': {self.detail}" if self.object_name else f"Delegated deletion error: {self.detail}"
        object.__setattr__(self, "__message__", msg)


@dataclass(frozen=True)
class CleanupTimeoutError(Exception):
    """Scene inspection or cleanup exceeded configured time limit.

    FR-SCN-001, FR-SCN-002: timeout error category.
    """

    operation: str = ""
    timeout_seconds: float = 0.0
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        msg = f"Cleanup/inspection timeout ({self.operation} exceeded {self.timeout_seconds}s)" if self.operation else f"Timeout error: {self.timeout_seconds}s"
        object.__setattr__(self, "__message__", msg)


@dataclass(frozen=True)
class ConnectionError(Exception):
    """Gateway or Blender execution channel is unavailable.

    FR-SCN-001, FR-SCN-002: connection error category.
    """

    detail: str = ""
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        msg = f"Connection error: {self.detail}" if self.detail else "Connection error: gateway or Blender execution channel unavailable"
        object.__setattr__(self, "__message__", msg)
