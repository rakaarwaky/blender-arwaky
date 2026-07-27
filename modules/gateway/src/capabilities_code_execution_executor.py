"""Code execution capability — execute raw Python code with security validation.

FR-GWY-005: Execute Raw Python Code
- Validates code via security policy feature before transport
- Enforces execution timeout
- Truncates oversized output with truncation indicator
- Does not manage background task lifecycle
- Delegates security validation to security policy feature (ValidateCodeProtocol)
- Delegates code transport to gateway transport feature (TransportProtocol)
"""

import logging
import time

from modules.shared.src.gateway.contract_code_execution_protocol import (
    CodeExecutionProtocol,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    SecurityViolationError,
    TimeoutError,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    TransportMessageVO,
)
from modules.shared.src.security.contract_validate_code_protocol import (
    ValidateCodeProtocol,
)
from modules.shared.src.security.taxonomy_security_error import (
    CodeValidationError,
)
from modules.shared.src.security.taxonomy_security_vo import (
    CodeValidationVO,
)

logger = logging.getLogger("BlenderMCPServer")


class CodeExecutionExecutor(CodeExecutionProtocol):
    """Concrete implementation for raw Python code execution.

    FR-GWY-005: Validates via security policy before transport. Enforces timeout.
    Truncates oversized output. Does not manage background task lifecycle.
    Delegates security validation to ValidateCodeProtocol.
    Delegates code transport to TransportProtocol.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        security_policy: ValidateCodeProtocol,
        transport: TransportProtocol,
        max_output_bytes: int = 1_048_576,
        execution_timeout_seconds: float = 30.0,
    ) -> None:
        self._security_policy: ValidateCodeProtocol = security_policy
        self._transport: TransportProtocol = transport
        self._max_output_bytes: int = max_output_bytes
        self._execution_timeout_seconds: float = execution_timeout_seconds

    # ─── Block 2: Protocol Method Implementation ─────────────

    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
        """Execute raw Python code in Blender with security validation.

        FR-GWY-005: Validates code via security policy feature before transport.
        Enforces execution timeout. Truncates oversized output with indicator.
        Does not manage background task lifecycle.
        Delegates security validation to ValidateCodeProtocol.
        Delegates transport to TransportProtocol.
        """
        # Security validation — delegate to security policy feature
        self._validate_code(request)

        start_time = time.time()
        timeout = request.timeout_override_seconds or self._execution_timeout_seconds

        try:
            # Execute code via transport — delegates to TransportProtocol
            outcome = self._execute_via_transport(request, timeout)
            duration_ms = (time.time() - start_time) * 1000

            # Extract output from transport response
            output = outcome.payload.decode("utf-8") if outcome.payload else ""

            # Truncate output if too large
            truncated = False
            if len(output.encode("utf-8")) > self._max_output_bytes:
                output = output[: self._max_output_bytes]
                truncated = True

            logger.debug(
                "Code execution complete: status=%s, %.1fms, truncated=%s",
                outcome.status,
                duration_ms,
                truncated,
            )
            return CodeExecutionOutcomeVO(
                status=outcome.status,
                output=output[:500],  # Keep a reasonable slice for observability
                truncated=truncated,
                duration_ms=duration_ms,
                error_category=outcome.error,
                error_message=outcome.error,
            )

        except TimeoutError:
            logger.error("Code execution timed out after %.1fs", timeout)
            return CodeExecutionOutcomeVO(
                status="timeout",
                error_message=f"Execution timed out after {timeout}s",
                duration_ms=(time.time() - start_time) * 1000,
            )
        except SecurityViolationError:
            logger.error("Code execution blocked by security policy")
            raise
        except Exception as e:
            logger.error("Code execution failed: %s", e)
            return CodeExecutionOutcomeVO(
                status="error",
                error_category="runtime",
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _validate_code(self, request: CodeExecutionVO) -> None:
        """Validate code via security policy feature.

        FR-GWY-005: Gateway must never perform its own code validation policy decisions.
        Delegates to ValidateCodeProtocol (security policy feature).
        Raises SecurityViolationError on validation failure.
        """
        # Build security validation request
        security_request = CodeValidationVO(
            code_text=request.code,
            max_code_size=100_000,  # Maximum code size per FRD
            strict_mode=True,
            execution_context="gateway_code_execution",
        )

        # Delegate to security policy feature
        try:
            result = self._security_policy.validate_code(security_request)
            if not result.allowed:
                violation_descriptions = "; ".join(v.description for v in result.violations)
                raise SecurityViolationError(f"Code validation failed: {violation_descriptions}")
        except CodeValidationError as e:
            raise SecurityViolationError(f"Security policy validation error: {e}")

    def _execute_via_transport(self, request: CodeExecutionVO, timeout_seconds: float) -> TransportOutcomeVO:
        """Execute code in Blender runtime via transport.

        FR-GWY-005: Sends code via TransportProtocol with tracking ID.
        Enforces execution timeout. Returns structured outcome.
        """
        # Build transport message with code as payload
        tracking_id = request.tracking_id or str(hash(request.code))
        transport_request = TransportMessageVO(
            tracking_id=tracking_id,
            operation_class="code_execution",
            payload=request.code.encode("utf-8"),
            timeout_override_seconds=timeout_seconds,
        )

        # Send via transport — real socket communication via TransportProtocol
        return self._transport.send_request(transport_request)

    def __repr__(self) -> str:
        return (
            f"CodeExecutionExecutor(security={self._security_policy!r}, "
            f"transport={self._transport!r}, "
            f"max_output={self._max_output_bytes}, "
            f"timeout={self._execution_timeout_seconds})"
        )
