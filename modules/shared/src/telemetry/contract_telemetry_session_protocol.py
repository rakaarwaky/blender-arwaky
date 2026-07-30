"""Telemetry domain contract: session management protocol (ABC based).

FR-TLM-003: Manage Analytics Sessions
Session identifiers persist across restarts within rotation window.
Consent withdrawal deletes local session state entirely.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import (
    EnabledFlag,
    SessionId,
    SuccessFlag,
)


class TelemetrySessionProtocol(ABC):
    """Sync protocol for managing anonymous telemetry sessions."""

    @abstractmethod
    def get_session_id(self, consent_active: EnabledFlag) -> SessionId | None:
        """Get current session ID or generate fresh one.

        FR-TLM-003: Session ID generated from collision-resistant random source.
        Persists across restarts within rotation window.
        Returns None if consent is inactive.

        Args:
            consent_active: Whether telemetry consent is active.

        Returns:
            Anonymous session identifier or None.
        """
        ...

    @abstractmethod
    def initialize_session(self) -> SuccessFlag:
        """Generate a new anonymous session identifier.

        Called on application startup to create a fresh session.
        The identifier must be completely anonymous and not traceable to a user.
        """
        ...

    @abstractmethod
    def rotate_session(self) -> SessionId:
        """Rotate session, producing fresh identifier with no linkage.

        Returns:
            New session identifier string.
        """
        ...

    @abstractmethod
    def clear_session(self) -> None:
        """Clear session state (e.g., on consent withdrawal)."""
        ...
