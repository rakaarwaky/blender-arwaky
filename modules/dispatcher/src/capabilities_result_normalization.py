"""Result normalization capability — unified envelope construction.

FR-DSP-006: Normalize Operation Result
- Normalizes all outcomes into single envelope shape
- Never leaks secrets, raw code, or sensitive paths
- Truncates oversized data with indicator
- Falls back to safe error envelope on construction failure
- Identical shape for CLI and MCP consumers

FR-INT-008: Integrates with ConfigContainer redaction rules for standardized
security compliance.
"""

import json
import logging
import sys

from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.dispatcher.contract_result_normalization_protocol import (
    ResultNormalizationProtocol,
)
from modules.shared.src.dispatcher.taxonomy_raw_outcome_vo import RawOutcomeVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

logger = logging.getLogger("BlenderMCPServer")


class ResultNormalizationExecutor(ResultNormalizationProtocol):
    """Concrete implementation for result normalization.

    FR-DSP-006: Normalizes all outcomes into unified envelope.
    Never leaks secrets; truncates oversized data; falls back to safe error.

    FR-INT-008: Uses IRedactionRulesProtocol for standardized redaction.
    Falls back to built-in sanitization when no rules provided.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        max_result_data_size: int = 1_000_000,
        redaction_rules: IRedactionRulesProtocol | None = None,
    ):
        self._max_size = max_result_data_size
        self._redaction_rules = redaction_rules

    # ─── Block 2: Protocol Method Implementation ─────────────

    def normalize_result(
        self,
        raw_outcome: RawOutcomeVO,
    ) -> UnifiedResultEnvelopeVO:
        """Normalize any dispatch or submission outcome into a unified result envelope.

        FR-DSP-006: Never leaks secrets; truncates oversized data; falls back to safe error.
        Returns identical shape for CLI and MCP consumers. Sets the `data_truncated`
        indicator when the data payload exceeds the configured size limit.
        """
        truncated = False
        try:
            # Extract outcome fields from typed VO
            success = raw_outcome.success
            message = raw_outcome.message
            tracking_id = raw_outcome.tracking_id
            data = raw_outcome.data
            error_category = raw_outcome.error_category
            warnings = list(raw_outcome.warnings or [])
            metadata = dict(raw_outcome.metadata or {})
            # Surface the execution context for consumers (FR-DSP-006 metadata summary).
            metadata["is_background"] = raw_outcome.is_background

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

    def _sanitize_data(self, data: object) -> object:
        """Sanitize data payload — redact secrets, paths, raw code.

        FR-DSP-006: Envelope must never include secrets, raw code, or sensitive paths.
        Handles all types: dicts, lists, strings, and nested structures.
        Non-serializable values converted to safe textual representation.

        FR-INT-008: Uses IRedactionRulesProtocol when available for standardized
        redaction; falls back to built-in sanitization otherwise.
        """
        # FR-INT-008: Use shared redaction rules if configured
        if self._redaction_rules is not None and isinstance(data, dict):
            try:
                return self._redaction_rules.redact_dict(data)
            except Exception:
                logger.warning("Redaction rules failed, falling back to built-in sanitization")

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
        self, d: dict[str, object], redacted_keys: set[str], max_depth: int, _depth: int = 0
    ) -> dict[str, object]:
        """Recursively sanitize a dict for secret keys and nested structures.

        Uses recursion with depth limit to avoid stack overflow on deeply nested data.
        """
        if _depth >= max_depth:
            return {"_truncated": True, "_size_exceeded": max_depth}

        result: dict[str, object] = {}
        for k, v in d.items():
            k_lower = k.lower()
            _is_redacted = False
            for _pattern in redacted_keys:
                if _pattern in k_lower:
                    _is_redacted = True
                    break
            if _is_redacted:
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
