"""Code execution capability — execute raw Python code with security validation.

FR-GWY-005: Execute Raw Python Code
- Validates code via security policy feature before transport
- Enforces execution timeout
- Truncates oversized output with truncation indicator
- Does not manage background task lifecycle
"""

import logging
import time

from modules.shared.src.gateway.contract_code_execution_protocol import (
    CodeExecutionProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    SecurityViolationError,
    TimeoutError,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
)

logger = logging.getLogger("BlenderMCPServer")


class CodeExecutionExecutor(CodeExecutionProtocol):
    """Concrete implementation for raw Python code execution.

    FR-GWY-005: Validates via security policy before transport. Enforces timeout.
    Truncates oversized output. Does not manage background task lifecycle.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, max_output_bytes: int = 1_048_576) -> None:
        self._max_output_bytes: int = max_output_bytes
        self._execution_timeout_seconds: float = 30.0

    # ─── Block 2: Protocol Method Implementation ─────────────

    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
        """Execute raw Python code in Blender with security validation.

        FR-GWY-005: Validates code via security policy feature before transport.
        Enforces execution timeout. Truncates oversized output with indicator.
        Does not manage background task lifecycle.
        """
        # Security validation (stub — delegates to security policy)
        self._validate_code(request)

        start_time = time.time()
        timeout = request.timeout_override_seconds or self._execution_timeout_seconds

        try:
            # Execute code via transport (stub — in real implementation, sends via socket)
            output = self._execute_in_blender(request.code, timeout)

            duration_ms = (time.time() - start_time) * 1000

            # Truncate output if too large
            truncated = False
            if len(output.encode("utf-8")) > self._max_output_bytes:
                output = output[:self._max_output_bytes]
                truncated = True

            logger.debug(
                "Code execution complete: status=%s, %.1fms, truncated=%s",
                "success", duration_ms, truncated,
            )
            return CodeExecutionOutcomeVO(
                status="success",
                output=output[:500],  # Keep a reasonable slice for observability
                truncated=truncated,
                duration_ms=duration_ms,
            )

        except TimeoutError:
            logger.error("Code execution timed out after %.1fs", timeout)
            return CodeExecutionOutcomeVO(
                status="timeout",
                error_message=f"Execution timed out after {timeout}s",
                duration_ms=(time.time() - start_time) * 1000,
            )
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
        Delegates to security policy feature.
        """
        # Stub: In real implementation, this would call security policy feature
        # For MVP, perform basic sanity checks
        if len(request.code) > 100_000:
            raise SecurityViolationError("Code size exceeds maximum allowed")

    def _execute_in_blender(self, code: str, timeout_seconds: float) -> str:
        """Execute code in Blender runtime via transport."""
        # Stub: In real implementation, this would send code via transport and receive output
        return "Execution completed successfully"

    def __repr__(self) -> str:
        return f"CodeExecutionExecutor(max_output={self._max_output_bytes}, timeout={self._execution_timeout_seconds})"
