"""Object domain errors — typed exceptions for object operation failures.

AES102: Uses _error suffix (not _vo) since this file contains domain error classes.
AES401: Error fields use taxonomy-typed values instead of primitives.
"""

from __future__ import annotations

from ..common.taxonomy_core_vo import (
    ActionName,
    ChannelName,
    ErrorString,
    ModifierName,
    ObjectName,
    PrimitiveType,
    ProtectedCategory,
)
from ..common.taxonomy_domain_error import DomainError


class ObjectAmbiguityError(DomainError):
    """Raised when an object reference resolves to multiple matching objects."""

    def __init__(self, reference: ObjectName, matches: list[ObjectName]) -> None:
        super().__init__(ErrorString(f"Ambiguous object reference '{reference}': {len(matches)} matches"))
        self.reference = reference
        self.matches = matches


class ObjectNotFoundError(DomainError):
    """Raised when a requested object does not exist in the scene."""

    def __init__(self, reference: ObjectName) -> None:
        super().__init__(ErrorString(f"Object '{reference}' not found in scene"))
        self.reference = reference


class TransformLockError(DomainError):
    """Raised when attempting to modify a locked transform channel."""

    def __init__(self, channel: ChannelName) -> None:
        super().__init__(ErrorString(f"Transform channel '{channel}' is locked"))
        self.channel = channel


class MaterialAssignmentError(DomainError):
    """Raised when material assignment is incompatible with the object type."""

    def __init__(self, object_name: ObjectName, reason: ErrorString) -> None:
        super().__init__(ErrorString(f"Cannot assign material to '{object_name}': {reason}"))
        self.object_name = object_name
        self.reason = reason


class ModifierActionConfirmationError(DomainError):
    """Raised when a destructive modifier action requires explicit confirmation."""

    def __init__(self, modifier_name: ModifierName, action: ActionName) -> None:
        super().__init__(ErrorString(f"Destructive action '{action}' on modifier '{modifier_name}' requires confirmation"))
        self.modifier_name = modifier_name
        self.action = action


class DeletionProtectionError(DomainError):
    """Raised when attempting to delete a protected object without confirmation."""

    def __init__(self, object_name: ObjectName, protected_category: ProtectedCategory) -> None:
        super().__init__(ErrorString(f"Cannot delete protected object '{object_name}' (category: {protected_category})"))
        self.object_name = object_name
        self.protected_category = protected_category


class InvalidPrimitiveTypeError(DomainError):
    """Raised when an unsupported primitive type is requested."""

    def __init__(self, primitive_type: PrimitiveType) -> None:
        super().__init__(ErrorString(f"Invalid primitive type: '{primitive_type}'"))
        self.primitive_type = primitive_type


class InvalidModifierTypeError(DomainError):
    """Raised when an unsupported modifier type is requested."""

    def __init__(self, modifier_type: ModifierName) -> None:
        super().__init__(ErrorString(f"Invalid modifier type: '{modifier_type}'"))
        self.modifier_type = modifier_type
