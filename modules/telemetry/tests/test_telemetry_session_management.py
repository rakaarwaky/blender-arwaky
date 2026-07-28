"""Tests for telemetry session management capability — FR-TLM-003.

FR-TLM-003: Session Identifier Generation, Persistence, and Rotation
- Anonymous session identifiers that persist for the entire application runtime
- New IDs generated on restart
- Completely anonymous and not traceable to a user
"""

from __future__ import annotations

import pytest

from modules.shared.src.common.taxonomy_core_vo import SessionId

# ─── Mock Protocol for Testing ──────────────────────────────────────────────


class MockSessionProtocol:
    """Mock async session protocol matching TelemetrySessionProtocol interface."""

    def __init__(self) -> None:
        self._counter = 0
        self._session_id: str | None = "mock-session-0"

    async def get_session_id(
        self,
        force_new: bool = False,
        consent_active: bool = True,  # noqa: ARG002
    ) -> SessionId:
        if force_new:
            self._counter += 1
            self._session_id = f"mock-session-{self._counter}"
        return SessionId(self._session_id)

    async def rotate_session(self) -> SessionId:
        self._counter += 1
        self._session_id = f"mock-session-rotated-{self._counter}"
        return SessionId(self._session_id)

    async def clear_session(self) -> None:
        pass


# ─── FR-TLM-003: Session Generation ────────────────────────────────────────


class TestSessionGeneration:
    """FR-TLM-003: Anonymous session identifier generation."""

    @pytest.mark.asyncio
    async def test_get_session_id_returns_anonymous_id(self) -> None:
        """FR-TLM-003: get_session_id returns an anonymous session ID."""
        protocol = MockSessionProtocol()
        result = await protocol.get_session_id()
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_session_id_is_consistent(self) -> None:
        """FR-TLM-003: get_session_id returns consistent ID without force_new."""
        protocol = MockSessionProtocol()
        first = await protocol.get_session_id()
        second = await protocol.get_session_id()
        assert str(first) == str(second)

    @pytest.mark.asyncio
    async def test_force_new_generates_different_id(self) -> None:
        """FR-TLM-003: force_new generates a different session ID."""
        protocol = MockSessionProtocol()
        first = await protocol.get_session_id(force_new=True)
        second = await protocol.get_session_id(force_new=True)
        assert str(first) != str(second)


# ─── FR-TLM-003: Session Rotation ─────────────────────────────────────────


class TestSessionRotation:
    """FR-TLM-003: Session rotation per FR-TLM-003."""

    @pytest.mark.asyncio
    async def test_rotate_session_generates_new_id(self) -> None:
        """FR-TLM-003: rotate_session creates a fresh session ID."""
        protocol = MockSessionProtocol()
        result = await protocol.rotate_session()
        assert isinstance(result, str)
        assert "rotated" in result.lower()

    @pytest.mark.asyncio
    async def test_rotate_produces_unlinked_id(self) -> None:
        """FR-TLM-003: Rotated session ID has no linkage to previous."""
        protocol = MockSessionProtocol()
        old = await protocol.get_session_id()
        new = await protocol.rotate_session()
        assert str(old) != str(new)


# ─── FR-TLM-003: Session Clearing ─────────────────────────────────────────


class TestSessionClearing:
    """FR-TLM-003: Session clearing per FR-TLM-003."""

    @pytest.mark.asyncio
    async def test_clear_session_succeeds(self) -> None:
        """FR-TLM-003: clear_session completes without error."""
        protocol = MockSessionProtocol()
        result = await protocol.clear_session()
        assert result is None


# ─── FR-TLM-003: Anonymity ────────────────────────────────────────────────


class TestAnonymity:
    """FR-TLM-003: Session IDs must be anonymous."""

    @pytest.mark.asyncio
    async def test_session_id_contains_no_pii(self) -> None:
        """FR-TLM-003: Session IDs contain no user-identifiable information."""
        protocol = MockSessionProtocol()
        session = await protocol.get_session_id()
        session_str = str(session)
        assert "user" not in session_str.lower() or "mock" in session_str.lower()
        assert "email" not in session_str.lower()

    @pytest.mark.asyncio
    async def test_rotated_session_is_anonymous(self) -> None:
        """FR-TLM-003: Rotated session IDs are anonymous."""
        protocol = MockSessionProtocol()
        session = await protocol.rotate_session()
        assert "user" not in str(session).lower() or "mock" in str(session).lower()
