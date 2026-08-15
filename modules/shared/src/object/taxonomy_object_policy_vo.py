"""Object domain policy Value Objects — configurable behavior rules for object operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

from ..common.taxonomy_core_vo import (
    SuccessFlag,
)


class NamingPolicy(Enum):
    """Rule for handling duplicate or requested object names."""

    REJECT = auto()  # Reject duplicate name
    UNIQUE_SUFFIX = auto()  # Automatically generate unique suffix
    OVERWRITE = auto()  # Overwrite existing object when explicitly allowed


class DeletionPolicy(Enum):
    """Rule for handling children, dependents, and protected objects during deletion."""

    DELETE_HIERARCHY = auto()  # Delete object with all children
    DETACH_CHILDREN = auto()  # Remove object but detach children
    REJECT_DEPENDENTS = auto()  # Reject deletion when dependents exist


class TransformMode(Enum):
    """Transform update mode for set transform operations."""

    ABSOLUTE = auto()  # Set to absolute values
    RELATIVE = auto()  # Add delta to existing values


class MaterialReusePolicy(Enum):
    """Rule for material creation and reuse."""

    REUSE_EXISTING = auto()  # Reuse material if name exists
    CREATE_NEW = auto()  # Always create new material


class ModifierAction(Enum):
    """Supported modifier actions."""

    ADD = auto()  # Add new modifier
    UPDATE = auto()  # Update existing modifier
    REMOVE = auto()  # Remove modifier
    APPLY_DESTRUCTIVE = auto()  # Apply modifier destructively


@dataclass(frozen=True)
class NamingPolicyVO:
    """Configured naming policy with optional explicit override flag."""

    policy: NamingPolicy = NamingPolicy.REJECT
    allow_override: SuccessFlag = field(default=SuccessFlag(False))


@dataclass(frozen=True)
class DeletionPolicyVO:
    """Configured deletion policy with confirmation requirements."""

    policy: DeletionPolicy = DeletionPolicy.DELETE_HIERARCHY
    require_confirmation: SuccessFlag = field(default=SuccessFlag(True))
    protected_categories: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PlacementPolicyVO:
    """Configured placement policy for asset/object placement."""

    preserve_identity: SuccessFlag = field(default=SuccessFlag(True))
    idempotent: SuccessFlag = field(default=SuccessFlag(False))
    overwrite_policy: NamingPolicy = NamingPolicy.REJECT


@dataclass(frozen=True)
class TransformPolicyVO:
    """Configured transform policy."""

    mode: TransformMode = TransformMode.ABSOLUTE
    respect_locks: SuccessFlag = field(default=SuccessFlag(True))
    preserve_omitted: SuccessFlag = field(default=SuccessFlag(True))


@dataclass(frozen=True)
class MaterialPolicyVO:
    """Configured material assignment policy."""

    reuse_policy: MaterialReusePolicy = MaterialReusePolicy.REUSE_EXISTING
    create_new_if_missing: SuccessFlag = field(default=SuccessFlag(True))
    slot_reference: int | None = None


@dataclass(frozen=True)
class ModifierPolicyVO:
    """Configured modifier action policy."""

    action: ModifierAction = ModifierAction.ADD
    require_confirmation: SuccessFlag = field(default=SuccessFlag(False))
