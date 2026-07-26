"""Action catalog metadata Value Object.

Represents a registered action's complete metadata profile including schema,
flags, timeouts, and usage examples. Immutable once registered.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ActionMetadataVO:
    """Action catalog entry — immutable registration metadata.

    Input (set by registering feature):
      - action_name, owning_feature_ref, description, parameter_schema, etc.

    Output (computed by dispatcher):
      - catalog_version, degraded flag
    """

    # Required fields
    action_name: str
    owning_feature_ref: str
    description: str
    parameter_schema: dict[str, Any]
    usage_examples: list[str]

    # Metadata flags and defaults
    default_timeout: float = 30.0
    timeout_class: str = "default"
    idempotency_flag: bool = False
    scene_mutation_flag: bool = False
    background_eligibility_flag: bool = False
    destructive_flag: bool = False
    read_only_flag: bool = False
    long_running_flag: bool = False
    risk_level: str = "medium"

    # Output fields (set by dispatcher)
    catalog_version: int = 0
    degraded: bool = False

    def __post_init__(self) -> None:
        """Validate registration constraints."""
        if not self.action_name:
            raise ValueError("action_name must not be empty")
        if not self.owning_feature_ref:
            raise ValueError("owning_feature_ref must not be empty")
        if self.default_timeout < 0:
            raise ValueError("default_timeout must be non-negative")
