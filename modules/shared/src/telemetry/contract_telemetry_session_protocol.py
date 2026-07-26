"""Telemetry domain contract: session management protocol (ABC based).

Defines the protocol for maintaining random, unlinkable session identifiers
that survive restarts within a rotation window.

FR-TLM-003: Manage Analytics Sessions
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TelemetrySessionProtocol(ABC):
    """Protocol for managing anonymous telemetry sessions."""

    @abstractmethod
    async def get_session_id(
        self,
        force_new: bool = False,
        consent_active: bool = True,
    ) -> str:
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
    async def rotate_session(self) -> str:
        """Rotate session, producing fresh identifier with no linkage.

        Returns:
            New session identifier string.
        """
        pass

    @abstractmethod
    async def clear_session(self) -> None:
        """Clear session state (e.g., on consent withdrawal)."""
        pass
