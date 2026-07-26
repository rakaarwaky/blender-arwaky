"""Request validation capability — schema validation against catalog.

FR-DSP-003: Validate Action Request
- Validates action name exists in catalog
- Validates parameters against registered schema
- Generates tracking ID when absent
- Does not mutate request or catalog state
"""

import logging

from modules.shared.src.dispatcher.contract_request_validation_protocol import (
    RequestValidationProtocol,
)
from modules.shared.src.dispatcher.taxonomy_action_request_vo import ActionCommandVO

logger = logging.getLogger("BlenderMCPServer")


class RequestValidationExecutor(RequestValidationProtocol):
    """Concrete implementation for request validation.

    FR-DSP-003: Unknown action -> not found error; invalid params -> field-level detail.
    Generates tracking ID when absent. Does not mutate request or catalog state.
    Returns enriched same VO type (merged input+output pattern).
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, catalog: dict[str, any] = None) -> None:
        self._catalog = catalog or {}

    # ─── Block 2: Protocol Method Implementation ─────────────

    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO:
        """Validate an action request against the catalog.

        FR-DSP-003: Unknown action produces error; invalid params produce field-level detail.
        Generates tracking ID when absent. Does not mutate request or catalog state.
        Returns enriched same VO type with resolved_metadata and validated_tracking_id.
        """
        metadata = self._catalog.get(request.action_name)
        if metadata is None:
            raise ValueError(f"Unknown action: {request.action_name}")

        self._validate_parameters(request, metadata)

        validated = ActionCommandVO(
            action_name=request.action_name,
            parameters=request.parameters,
            execution_mode=request.execution_mode,
            timeout_override=request.timeout_override,
            confirmation_flag=request.confirmation_flag,
            tracking_id=request.tracking_id,
            resolved_metadata={
                "owning_feature_ref": metadata.owning_feature_ref,
                "default_timeout": metadata.default_timeout,
                "timeout_class": metadata.timeout_class,
                "idempotency_flag": metadata.idempotency_flag,
                "scene_mutation_flag": metadata.scene_mutation_flag,
                "background_eligibility_flag": metadata.background_eligibility_flag,
                "destructive_flag": metadata.destructive_flag,
                "read_only_flag": metadata.read_only_flag,
                "risk_level": metadata.risk_level,
            },
        )

        logger.debug(
            "Request validated: %s (tracking_id=%s)",
            request.action_name,
            validated.validated_tracking_id,
        )
        return validated

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _validate_parameters(self, request: ActionCommandVO, metadata: any) -> None:
        """Validate parameters against registered schema."""
        schema = getattr(metadata, "parameter_schema", {})

        required = schema.get("required", [])
        for field_name in required:
            if field_name not in request.parameters:
                raise ValueError(f"Missing required parameter: {field_name}")

        declared_params = set(schema.get("properties", {}).keys())
        extra = set(request.parameters.keys()) - declared_params - set(required)
        if extra:
            raise ValueError(f"Unknown extra parameters: {', '.join(sorted(extra))}")

    def __repr__(self) -> str:
        return f"RequestValidationExecutor(catalog={len(self._catalog)})"
