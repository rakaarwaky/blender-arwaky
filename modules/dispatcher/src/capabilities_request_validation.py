"""Request validation capability — schema validation against catalog.

FR-DSP-003: Validate Action Request
- Validates action name exists in catalog
- Validates parameters against registered schema (types, ranges, lengths, enums, size)
- Enforces execution-mode compatibility, destructive confirmation, timeout-override bounds
- Generates tracking ID when absent
- Does not mutate request or catalog state
"""

import json
import logging
from typing import Any

from modules.shared.src.dispatcher.contract_request_validation_protocol import (
    RequestValidationProtocol,
)
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_dispatch_error import (
    DispatchError,
    DispatchErrorCategory,
)

logger = logging.getLogger("BlenderMCPServer")

# FR-DSP-003 / Configuration Keys — conservative operational defaults.
DEFAULT_TIMEOUT: float = 30.0
MAX_TIMEOUT_OVERRIDE: float = 3600.0
MAX_PAYLOAD_SIZE: int = 1_000_000
DESTRUCTIVE_CONFIRMATION_ENFORCED: bool = True


class RequestValidationExecutor(RequestValidationProtocol):
    """Concrete implementation for request validation.

    FR-DSP-003: Unknown action -> not found error; invalid params -> field-level detail.
    Enforces execution mode, destructive confirmation, and timeout-override bounds.
    Generates tracking ID when absent. Does not mutate request or catalog state.
    Returns enriched same VO type with resolved_metadata, validation_warnings, and
    validated_tracking_id.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        catalog: dict[str, Any] | None = None,
        unknown_parameter_policy: str = "strict",
        max_payload_size: int = MAX_PAYLOAD_SIZE,
        max_timeout_override: float = MAX_TIMEOUT_OVERRIDE,
        destructive_confirmation_enforced: bool = DESTRUCTIVE_CONFIRMATION_ENFORCED,
    ) -> None:
        self._catalog: dict[str, Any] = catalog if catalog is not None else {}
        self._unknown_parameter_policy = unknown_parameter_policy
        self._max_payload_size = max_payload_size
        self._max_timeout_override = max_timeout_override
        self._destructive_confirmation_enforced = destructive_confirmation_enforced

    # ─── Block 2: Protocol Method Implementation ─────────────

    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO:
        """Validate an action request against the catalog.

        FR-DSP-003: Unknown action produces not-found error; invalid params produce
        field-level detail. Enforces mode compatibility, destructive confirmation, and
        timeout bounds. Generates tracking ID when absent. Does not mutate catalog state.
        """
        metadata = self._catalog.get(request.action_name)
        if metadata is None:
            raise DispatchError(
                f"Unknown action: {request.action_name}", DispatchErrorCategory.NOT_FOUND
            )

        warnings: list[str] = []
        self._validate_parameters(request, metadata, warnings)

        # Execution-mode compatibility (FR-DSP-003)
        exec_mode = request.execution_mode
        if exec_mode == "background" and not metadata.background_eligibility_flag:
            raise DispatchError(
                f"Action '{request.action_name}' does not support background execution mode",
                DispatchErrorCategory.UNSUPPORTED,
            )

        # FR-DSP-003: Sync mode requires non-background-only action (warn if background-only)
        if exec_mode == "sync" and metadata.background_eligibility_flag and not metadata.read_only_flag:
            warnings.append(
                f"Action '{request.action_name}' is background-only; consider using background mode"
            )

        # Destructive confirmation enforcement (FR-DSP-003)
        if (
            metadata.destructive_flag
            and self._destructive_confirmation_enforced
            and not request.confirmation_flag
        ):
            raise DispatchError(
                f"Destructive action '{request.action_name}' requires explicit confirmation",
                DispatchErrorCategory.CONFIRMATION,
            )

        # Timeout-override bounds (FR-DSP-003)
        if request.timeout_override is not None and (
            request.timeout_override < 0
            or request.timeout_override > self._max_timeout_override
        ):
            raise DispatchError(
                f"Timeout override {request.timeout_override} out of bounds "
                f"[0, {self._max_timeout_override}]",
                DispatchErrorCategory.TIMEOUT,
            )

        resolved_metadata = {
            "owning_feature_ref": metadata.owning_feature_ref,
            "default_timeout": metadata.default_timeout,
            "timeout_class": metadata.timeout_class,
            "idempotency_flag": metadata.idempotency_flag,
            "scene_mutation_flag": metadata.scene_mutation_flag,
            "background_eligibility_flag": metadata.background_eligibility_flag,
            "destructive_flag": metadata.destructive_flag,
            "read_only_flag": metadata.read_only_flag,
            "risk_level": metadata.risk_level,
        }

        validated = ActionCommandVO(
            action_name=request.action_name,
            parameters=request.parameters,
            execution_mode=request.execution_mode,
            timeout_override=request.timeout_override,
            confirmation_flag=request.confirmation_flag,
            tracking_id=request.tracking_id,
            resolved_metadata=resolved_metadata,
            validation_warnings=list(warnings),
        )

        logger.debug(
            "Request validated: %s (tracking_id=%s)",
            request.action_name,
            validated.validated_tracking_id,
        )
        return validated

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _validate_parameters(
        self, request: ActionCommandVO, metadata: Any, warnings: list[str]
    ) -> None:
        """Validate parameters against the registered schema (FR-DSP-003)."""
        schema = getattr(metadata, "parameter_schema", {}) or {}
        properties = schema.get("properties", {}) or {}
        required = schema.get("required", []) or []

        # Required fields present
        for field_name in required:
            if field_name not in request.parameters:
                raise DispatchError(
                    f"Missing required parameter: {field_name}", DispatchErrorCategory.VALIDATION
                )

        # Unknown extra parameters (strict vs tolerant)
        declared_params = set(properties.keys())
        extra = set(request.parameters.keys()) - declared_params - set(required)
        if extra:
            if self._unknown_parameter_policy == "strict":
                raise DispatchError(
                    f"Unknown extra parameters: {', '.join(sorted(extra))}",
                    DispatchErrorCategory.VALIDATION,
                )
            warnings.append(
                f"Unknown extra parameters ignored: {', '.join(sorted(extra))}"
            )

        # Per-field type / range / length / enum validation
        for field_name, value in request.parameters.items():
            field_def = properties.get(field_name)
            if field_def is None:
                continue  # required-only field or already handled unknown above
            self._validate_field(field_name, value, field_def)

        # Payload size limit (FR-DSP-003)
        try:
            payload_size = len(json.dumps(request.parameters, default=str))
        except TypeError:
            payload_size = 0
        if payload_size > self._max_payload_size:
            raise DispatchError(
                f"Parameter payload size {payload_size} exceeds limit {self._max_payload_size}",
                DispatchErrorCategory.VALIDATION,
            )

    def _validate_field(self, field_name: str, value: Any, field_def: dict[str, Any]) -> None:
        """Validate a single parameter value against its schema definition."""
        declared_type = field_def.get("type")
        if declared_type:
            self._check_type(field_name, value, declared_type)

        # Numeric range
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in field_def and value < field_def["minimum"]:
                raise DispatchError(
                    f"Parameter '{field_name}' value {value} below minimum {field_def['minimum']}",
                    DispatchErrorCategory.VALIDATION,
                )
            if "maximum" in field_def and value > field_def["maximum"]:
                raise DispatchError(
                    f"Parameter '{field_name}' value {value} above maximum {field_def['maximum']}",
                    DispatchErrorCategory.VALIDATION,
                )

        # String length
        if isinstance(value, str):
            if "minLength" in field_def and len(value) < field_def["minLength"]:
                raise DispatchError(
                    f"Parameter '{field_name}' length {len(value)} below minLength "
                    f"{field_def['minLength']}",
                    DispatchErrorCategory.VALIDATION,
                )
            if "maxLength" in field_def and len(value) > field_def["maxLength"]:
                raise DispatchError(
                    f"Parameter '{field_name}' length {len(value)} above maxLength "
                    f"{field_def['maxLength']}",
                    DispatchErrorCategory.VALIDATION,
                )

        # Enumerated allowed values
        if "enum" in field_def and value not in field_def["enum"]:
            raise DispatchError(
                f"Parameter '{field_name}' value {value!r} not in allowed set "
                f"{field_def['enum']}",
                DispatchErrorCategory.VALIDATION,
            )

    def _check_type(self, field_name: str, value: Any, declared_type: str) -> None:
        """Check a parameter value against its declared primitive type."""
        if isinstance(value, bool) and declared_type != "boolean":
            raise DispatchError(
                f"Parameter '{field_name}' must be {declared_type}, got bool",
                DispatchErrorCategory.VALIDATION,
            )

        type_map: dict[str, Any] = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected = type_map.get(declared_type)
        if expected is None:
            return
        if not isinstance(value, expected):
            raise DispatchError(
                f"Parameter '{field_name}' must be {declared_type}, got {type(value).__name__}",
                DispatchErrorCategory.VALIDATION,
            )

    def __repr__(self) -> str:
        return f"RequestValidationExecutor(catalog={len(self._catalog)})"
