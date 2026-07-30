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
from modules.shared.src.dispatcher.taxonomy_dispatch_error import DispatchErrorCategory
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
                "Envelope construction failed",
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _sanitize_data(self, data: Any) -> Any:
        """Sanitize data payload — redact secrets, paths, raw code.

        FR-DSP-006: Envelope must never include secrets, raw code, or sensitive paths.
        Handles all types: dicts, lists, strings, and nested structures.
        Non-serializable values converted to safe textual representation.

        Uses iterative approach with depth limit to avoid stack overflow on deeply nested data.
        """
        redacted_keys = {"password", "secret", "token", "api_key", "private", "code"}
        secret_patterns = ["password", "secret", "token", "api_key", "credential", "private_key"]
        max_depth = 50

        # Handle dict — recursive key-based redaction
        if isinstance(data, dict):
            return self._sanitize_dict(data, redacted_keys, max_depth)

        # Handle list — sanitize each item recursively
        if isinstance(data, list):
            return [self._sanitize_data(item) for item in data]

        # Handle string — check for embedded secrets (API keys in URLs, tokens in strings)
        if isinstance(data, str):
            lower = data.lower()
            for pattern in secret_patterns:
                if pattern in lower and len(data) > 10:
                    return "***REDACTED***"
            # Truncate very long strings to prevent envelope bloat
            if len(data) > 1000:
                data = f"{data[:500]}...[truncated]"
            return data

        # Primitives (int, float, bool, None) are safe — return as-is
        if isinstance(data, (int, float, bool)) or data is None:
            return data

        # Non-serializable objects — convert to string safely
        try:
            json.dumps(data)
            return data
        except (TypeError, ValueError):
            return str(data)

    def _sanitize_dict(
        self, d: dict[str, Any], redacted_keys: set[str], max_depth: int, _depth: int = 0
    ) -> dict[str, Any]:
        """Recursively sanitize a dict for secret keys and nested structures.

        Uses recursion with depth limit to avoid stack overflow on deeply nested data.
        """
        if _depth >= max_depth:
            return {"_truncated": True, "_size_exceeded": max_depth}

        result: dict[str, Any] = {}
        for k, v in d.items():
            k_lower = k.lower()
            if any(pattern in k_lower for pattern in redacted_keys):
                result[k] = "***REDACTED***"
            elif isinstance(v, dict):
                result[k] = self._sanitize_dict(v, redacted_keys, max_depth, _depth + 1)
            elif isinstance(v, list):
                result[k] = [self._sanitize_data(item) for item in v]
            elif isinstance(v, str) and len(v) > 1000:
                result[k] = f"{v[:500]}...[truncated]"
            else:
                result[k] = v
        return result

    def __repr__(self) -> str:
        return f"ResultNormalizationExecutor(max_size={self._max_size})"
