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
from modules.shared.src.dispatcher.taxonomy_action_request_vo import ActionRequestVO
from modules.shared.src.dispatcher.taxonomy_validation_result_vo import ValidationResultVO

logger = logging.getLogger("BlenderMCPServer")


class RequestValidationExecutor(RequestValidationProtocol):
    """Concrete implementation for request validation.

    FR-DSP-003: Unknown action → not found error; invalid params → field-level detail.
    Generates tracking ID when absent. Does not mutate request or catalog state.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, catalog: dict[str, any] = None):
        self._catalog = catalog or {}

    # ─── Block 2: Protocol Method Implementation ─────────────

    def validate_request(self, request: ActionRequestVO) -> ValidationResultVO:
        """Validate an action request against the catalog.

        FR-DSP-003: Unknown action produces error; invalid params produce field-level detail.
        Generates tracking ID when absent. Does not mutate request or catalog state.
        """
        # 1. Check action exists in catalog
        metadata = self._catalog.get(request.action_name)
        if metadata is None:
            raise ValueError(f"Unknown action: {request.action_name}")

        # 2. Validate parameters against schema
        warnings = self._validate_parameters(request, metadata)

        # 3. Build enriched validation result
        validated = ValidationResultVO(
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
            "Request validated: %s (tracking_id=%s, warnings=%d)",
            request.action_name,
            validated.validated_tracking_id,
            len(warnings),
        )
        return validated

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _validate_parameters(self, request: ActionRequestVO, metadata: any) -> list[str]:
        """Validate parameters against registered schema.

        Returns list of warnings (strict mode rejects with error instead).
        """
        warnings: list[str] = []
        schema = getattr(metadata, "parameter_schema", {})

        # Check required fields
        required = schema.get("required", [])
        for field_name in required:
            if field_name not in request.parameters:
                raise ValueError(f"Missing required parameter: {field_name}")

        # Check extra parameters (strict mode)
        declared_params = set(schema.get("properties", {}).keys())
        extra = set(request.parameters.keys()) - declared_params - set(required)
        if extra:
            raise ValueError(f"Unknown extra parameters: {', '.join(sorted(extra))}")

        return warnings

    def __repr__(self) -> str:
        return f"RequestValidationExecutor(catalog={len(self._catalog)})"
