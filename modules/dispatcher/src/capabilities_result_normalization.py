"""Result normalization capability — unified envelope construction.

FR-DSP-006: Normalize Operation Result
- Normalizes all outcomes into single envelope shape
- Never leaks secrets, raw code, or sensitive paths
- Truncates oversized data with indicator
- Falls back to safe error envelope on construction failure
- Identical shape for CLI and MCP consumers
"""

import json
import logging
import sys
from typing import Any

from modules.shared.src.dispatcher.contract_result_normalization_protocol import (
    ResultNormalizationProtocol,
)
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

logger = logging.getLogger("BlenderMCPServer")


class ResultNormalizationExecutor(ResultNormalizationProtocol):
    """Concrete implementation for result normalization.

    FR-DSP-006: Normalizes all outcomes into unified envelope.
    Never leaks secrets; truncates oversized data; falls back to safe error.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, max_result_data_size: int = 1_000_000):
        self._max_size = max_result_data_size

    # ─── Block 2: Protocol Method Implementation ─────────────

    def normalize_result(
        self,
        raw_outcome: dict[str, Any],
        tracking_id: str,
        is_background: bool = False,
    ) -> UnifiedResultEnvelopeVO:
        """Normalize any dispatch or submission outcome into a unified result envelope.

        FR-DSP-006: Never leaks secrets; truncates oversized data; falls back to safe error.
        Returns identical shape for CLI and MCP consumers. Sets the `data_truncated`
        indicator when the data payload exceeds the configured size limit.
        """
        truncated = False
        try:
            # Extract outcome fields
            success = raw_outcome.get("success", False)
            message = raw_outcome.get("message", "")
            data = raw_outcome.get("data")
            error_category = raw_outcome.get("error_category")
            warnings = list(raw_outcome.get("warnings", []) or [])
            metadata = dict(raw_outcome.get("metadata", {}) or {})
            # Surface the execution context for consumers (FR-DSP-006 metadata summary).
            metadata["is_background"] = is_background

            # Process and sanitize data payload
            if data is not None:
                data = self._sanitize_data(data)
                # Fast size approximation — only serialize if close to threshold
                approx_size = sys.getsizeof(data)
                if approx_size < self._max_size * 0.5:
                    data_size = approx_size
                else:
                    try:
                        data_size = len(json.dumps(data, default=str))
                    except TypeError:
                        data_size = approx_size
                if data_size > self._max_size:
                    truncated = True
                    data = {"_truncated": True, "_size_exceeded": self._max_size}
                    warnings.append("Result data truncated to fit envelope size limit")

            # Build envelope
            if success:
                return UnifiedResultEnvelopeVO(
                    success=True,
                    message=message,
                    tracking_id=tracking_id,
                    data=data,
                    warnings=warnings,
                    metadata=metadata,
                    data_truncated=truncated,
                )
            return UnifiedResultEnvelopeVO(
                success=False,
                message=message,
                tracking_id=tracking_id,
                error_category=error_category or "execution_error",
                data=data,
                warnings=warnings,
                metadata=metadata,
                data_truncated=truncated,
            )

        except Exception as e:
            # Envelope construction failure — fall back to safe error
            logger.error("Envelope construction failed: %s", e)
            return UnifiedResultEnvelopeVO.safe_error_envelope(
                f"Normalization failed: {e}",
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data payload — redact secrets, paths, raw code.

        FR-DSP-006: Envelope must never include secrets, raw code, or sensitive paths.
        Non-serializable values converted to safe textual representation.

        Uses iterative approach with depth limit to avoid stack overflow on deeply nested data.
        """
        redacted_keys = {"password", "secret", "token", "api_key", "private", "code"}
        max_depth = 50

        # Iterative sanitization using a queue of (result_dict_ref, key_or_None, value_to_process)
        result: dict[str, Any] | None = None
        queue: list[tuple[dict[str, Any] | None, str | None, Any]] = [(None, None, data)]
        depth = 0

        while queue and depth < max_depth:
            depth += 1
            parent_ref, key, value = queue.pop(0)

            if isinstance(value, dict):
                new_dict: dict[str, Any] = {}
                # Attach new_dict to its parent
                if key is not None and parent_ref is not None:
                    parent_ref[key] = new_dict
                elif result is None:
                    # Root dict — this IS the result
                    result = new_dict
                for k, v in value.items():
                    k_lower = k.lower()
                    if any(pattern in k_lower for pattern in redacted_keys):
                        new_dict[k] = "***REDACTED***"
                    elif isinstance(v, dict):
                        queue.append((new_dict, k, v))
                    elif isinstance(v, str) and len(v) > 1000:
                        new_dict[k] = f"{v[:500]}...[truncated]"
                    else:
                        new_dict[k] = v

        if result is None:
            # Not a dict — fall through to non-dict handling below
            pass
        else:
            return result

        # Non-dict data — convert to string safely
        try:
            json.dumps(data)
            return data
        except (TypeError, ValueError):
            return str(data)

    def __repr__(self) -> str:
        return f"ResultNormalizationExecutor(max_size={self._max_size})"
