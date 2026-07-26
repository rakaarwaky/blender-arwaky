"""Contract: Telemetry session management port interface.

Defines the contract for managing anonymous analytics sessions.
AES Port layer — depends only on taxonomy entities.
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