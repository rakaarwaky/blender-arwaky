"""Gateway domain — Error types for transport, connection, and execution failures.

All errors use explicit typed classes — no bare strings.
"""

from __future__ import annotations


class GatewayError(Exception):
    """Base error for all gateway domain exceptions."""


class ConnectionError(GatewayError):
    """Connection failed, refused, or lost."""


class TimeoutError(GatewayError):
    """Transport timeout, execution timeout, or queue wait timeout exceeded."""


class ProtocolVersionMismatchError(GatewayError):
    """Protocol version incompatible between application and Blender bridge."""


class AuthenticationError(GatewayError):
    """Transport authentication failed."""


class ChannelConflictError(GatewayError):
    """Queue conflict, queue depth limit reached, or serialization contention."""


class SecurityViolationError(GatewayError):
    """Code validation failed, delegated through security policy feature."""


class TransportParseError(GatewayError):
    """Malformed frame or unparseable response content."""


class PayloadLimitError(GatewayError):
    """Request or response exceeded configured payload size."""
