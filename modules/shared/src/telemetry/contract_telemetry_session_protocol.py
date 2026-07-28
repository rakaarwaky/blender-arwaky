"""Telemetry domain contract: session management protocol (ABC based).

Defines the protocol for maintaining random, unlinkable session identifiers
that survive restarts within a rotation window.

FR-TLM-003: Manage Analytics Sessions
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import SessionId


class TelemetrySessionProtocol(ABC):
    """Protocol for managing anonymous telemetry sessions."""

    @abstractmethod
    async def get_session_id(
        self,
        force_new: bool = False,
        consent_active: bool = True,
    ) -> SessionId:
        """Get current session ID or generate fresh one.

        FR-TLM-003: Session ID generated from collision-resistant random source.
        Persists across restarts within rotation window.
        Consent withdrawal deletes local session state entirely.

        Args:
            force_new: Whether to generate a new session ID.
            consent_active: Whether telemetry consent is active.

        Returns:
            Anonymous session identifier string.
        """
        pass

    @abstractmethod
    async def rotate_session(self) -> SessionId:
        """Rotate session, producing fresh identifier with no linkage.

        Returns:
            New session identifier string.
        """
        pass

    @abstractmethod
    async def clear_session(self) -> None:
        """Clear session state (e.g., on consent withdrawal)."""
        pass


# --- Merged from contract_telemetry_session_management.py ---

"""Contract: Telemetry session management port interface.

Defines the contract for managing anonymous analytics sessions.
Port layer — depends only on taxonomy entities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import SessionId, SuccessFlag


class TelemetrySessionManagementPort(ABC):
    """Port interface for telemetry session management."""

    @abstractmethod
    def get_session_id(self) -> SessionId:
        """Return the current anonymous session identifier.

        FR-TLM-003: The session ID persists for the entire application runtime.
        A new unique ID is generated on each application restart.
        """
        pass

    @abstractmethod
    def initialize_session(self) -> SuccessFlag:
        """Generate a new anonymous session identifier.

        FR-TLM-003: Called on application startup to create a fresh session.
        The identifier must be completely anonymous and not traceable to a user.
        """
        pass
