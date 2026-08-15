"""Bootstrap the dispatcher catalog from the canonical action schema constants."""

from __future__ import annotations

from collections.abc import Iterable

from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS


def _property_schema(raw: dict[str, object]) -> dict[str, object]:
    """Convert CLI/MCP schema type names to dispatcher validation types."""
    result = dict(raw)
    declared_type = result.get("type")
    if declared_type == "array[number]":
        result["type"] = "array"
    elif declared_type == "any":
        # RequestValidationExecutor treats unknown type names as intentionally open.
        result["type"] = "any"
    return result


def iter_action_metadata() -> Iterable[ActionMetadataVO]:
    """Yield valid metadata records for every canonical dispatcher action."""
    for domain, actions in DISPATCHER_ACTION_SCHEMAS.items():
        for action_name, raw_spec in actions.items():
            raw_parameters = raw_spec.get("parameters", {})
            parameters = raw_parameters if isinstance(raw_parameters, dict) else {}
            properties = {
                name: _property_schema(spec if isinstance(spec, dict) else {}) for name, spec in parameters.items()
            }
            required = [
                name for name, spec in parameters.items() if isinstance(spec, dict) and bool(spec.get("required"))
            ]
            raw_metadata = raw_spec.get("metadata", {})
            metadata = raw_metadata if isinstance(raw_metadata, dict) else {}
            read_only = action_name.startswith(
                ("get_", "inspect_", "validate_", "search_", "list_", "health_", "status")
            )
            destructive = action_name.startswith(("delete", "cleanup", "cancel", "shutdown", "set_config"))
            yield ActionMetadataVO(
                action_name=action_name,
                owning_feature_ref=domain,
                description=str(raw_spec.get("description", action_name)),
                parameter_schema={"type": "object", "properties": properties, "required": required},
                usage_examples=[f"{action_name}({', '.join(required)})"],
                default_timeout=float(metadata.get("default_timeout", 30.0)),
                timeout_class=str(metadata.get("timeout_class", "default")),
                idempotency_flag=bool(metadata.get("idempotency_flag", read_only)),
                scene_mutation_flag=bool(metadata.get("scene_mutation_flag", not read_only)),
                background_eligibility_flag=bool(metadata.get("background_eligibility_flag", False)),
                destructive_flag=bool(metadata.get("destructive_flag", destructive)),
                read_only_flag=bool(metadata.get("read_only_flag", read_only)),
                long_running_flag=bool(metadata.get("long_running_flag", False)),
                risk_level=str(metadata.get("risk_level", "high" if destructive else "medium")),
            )


def register_canonical_actions(registration: object) -> int:
    """Register all canonical action metadata and return the action count."""
    count = 0
    for metadata in iter_action_metadata():
        registration.register_action(metadata)
        count += 1
    return count
