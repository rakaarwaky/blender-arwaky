"""Capabilities: Executable locator — FR-LAU-001.

Discovers, validates, and registers the Blender executable following the
deterministic discovery order. Implements LocateRegisterProtocol.

Dependencies are injected (config provider, command runner) so the logic is
testable without spawning or probing a real Blender install.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from typing import Protocol

from modules.shared.src.common.taxonomy_core_vo import FilePath
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.launcher.contract_locate_register_protocol import LocateRegisterProtocol
from modules.shared.src.launcher.taxonomy_launcher_constant import LAUNCHER_EVENT_EXECUTABLE_REGISTERED
from modules.shared.src.launcher.taxonomy_launcher_error import (
    ExecutableValidationError,
)
from modules.shared.src.launcher.taxonomy_launcher_event import LauncherLifecycleEvent
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ExecutableReferenceVO,
    LauncherConfigVO,
    RegistrationOutcomeVO,
    RegistrationSource,
    RuntimeState,
    VersionCompatibility,
)


class _CommandRunner(Protocol):
    """Runs a command and returns (returncode, stdout). DI boundary."""

    def __call__(self, args: list[str], timeout: float = 5.0) -> tuple[int, str]: ...


class ExecutableLocator(LocateRegisterProtocol):
    """Locates and registers the Blender executable per FR-LAU-001."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        config_provider: Callable[[], LauncherConfigVO] | None = None,
        command_runner: _CommandRunner | None = None,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
        redaction_rules: IRedactionRulesProtocol | None = None,
    ) -> None:
        self._config_provider = config_provider or (lambda: LauncherConfigVO())
        self._runner = command_runner
        self._events = event_sink
        self._redaction_rules = redaction_rules

    # ─── Block 2: Public Contract ────────────────────────────
    def locate_and_register(self, config: LauncherConfigVO, override: FilePath | None = None) -> RegistrationOutcomeVO:
        """Discover, validate, and register a Blender executable."""
        candidates = self._build_candidate_order(config, override)
        if not candidates:
            return RegistrationOutcomeVO(registered=False, error="No candidate locations available")

        for source, path in candidates:
            if not path or not os.path.exists(path):
                continue
            try:
                ref = self._validate(path)
            except ExecutableValidationError:
                continue
            self._register(config, path)
            self._emit_registered(source, path)
            return RegistrationOutcomeVO(executable=ref, source=source, registered=True)

        return RegistrationOutcomeVO(registered=False, error="No valid Blender executable found")

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _build_candidate_order(
        self, config: LauncherConfigVO, override: FilePath | None
    ) -> list[tuple[RegistrationSource, str]]:
        order: list[tuple[RegistrationSource, str]] = []
        if override:
            order.append((RegistrationSource.OVERRIDE, override))
        if config.executable_path:
            order.append((RegistrationSource.CONFIGURED, config.executable_path))
        env = os.environ.get("BLENDER_PATH")
        if env:
            order.append((RegistrationSource.ENVIRONMENT, env))
        for loc in config.search_locations:
            order.append((RegistrationSource.PLATFORM, loc))
        sys_path = shutil.which("blender")
        if sys_path:
            order.append((RegistrationSource.SYSTEM_PATH, sys_path))
        return order

    def _validate(self, path: str) -> ExecutableReferenceVO:
        # Resolve symlinks for canonical path (FR-LAU-001: normalized + symlink-safe)
        canonical = os.path.realpath(path)
        if not os.path.isfile(canonical) or not os.access(canonical, os.X_OK):
            raise ExecutableValidationError(f"Not an executable file: {canonical}")
        version = self._detect_version(canonical)
        compat = self._check_compatibility(version)
        return ExecutableReferenceVO(path=canonical, version_summary=version, compatibility=compat)

    def _detect_version(self, path: str) -> str:
        if self._runner is None:
            return ""
        try:
            rc, out = self._runner([path, "--version"], timeout=5.0)
        except Exception:
            return ""
        if rc != 0:
            return ""
        for token in out.split():
            if token[0].isdigit():
                return token
        return out.strip().splitlines()[0] if out.strip() else ""

    def _check_compatibility(self, version: str) -> VersionCompatibility:
        """Check version compatibility against configured supported_version_range.

        FR-LAU-001: Parses the supported_version_range from config (format: "X.Y+"
        meaning "minimum X.Y") and compares with detected version.

        Returns:
            SUPPORTED  — version meets or exceeds minimum requirement
            WARNING    — version is older than minimum but may still work
            UNSUPPORTED — version is significantly below minimum
            UNKNOWN    — no version string or no config range specified
        """
        if not version:
            return VersionCompatibility.UNKNOWN

        # Parse detected version (e.g., "3.6.0" -> [3, 6, 0])
        detected = self._parse_version(version)
        if detected is None:
            return VersionCompatibility.UNKNOWN

        config = self._config_provider()
        range_str = getattr(config, "supported_version_range", "") or ""

        if not range_str:
            # No range configured — assume supported (backward compat)
            return VersionCompatibility.SUPPORTED

        # Parse range string (format: "X.Y+" means minimum X.Y)
        min_version = self._parse_version_range(range_str)
        if min_version is None:
            return VersionCompatibility.UNKNOWN

        # Compare major versions for warning/unsupported verdicts
        major_diff = detected[0] - min_version[0] if len(detected) and len(min_version) else 0

        if major_diff > 0:
            # Future version — supported with warning
            return VersionCompatibility.WARNING
        elif major_diff == 0:
            # Same major — check minor/patch
            if tuple(detected[1:]) >= tuple(min_version[1:]):
                return VersionCompatibility.SUPPORTED
            return VersionCompatibility.WARNING
        else:
            # Older major version — unsupported
            return VersionCompatibility.UNSUPPORTED

    @staticmethod
    def _parse_version(version_str: str) -> tuple[int, ...] | None:
        """Parse a version string into a tuple of integers.

        Handles formats like "3.6", "3.6.0", "4.1.2".
        Returns None if parsing fails.
        """
        try:
            parts = version_str.strip().split(".")
            return tuple(int(p) for p in parts if p.isdigit()) or None
        except (IndexError, ValueError):
            return None

    @staticmethod
    def _parse_version_range(range_str: str) -> tuple[int, ...] | None:
        """Parse a version range string into minimum version tuple.

        Supports format "X.Y+" meaning "minimum X.Y".
        Strips trailing '+' and parses remaining version parts.
        Returns None if parsing fails.
        """
        range_str = range_str.strip().rstrip("+")
        return ExecutableLocator._parse_version(range_str)

    def _register(self, _config: LauncherConfigVO, path: str) -> None:
        provider = self._config_provider
        setter = getattr(provider, "set_executable_path", None)
        if callable(setter):
            setter(path)

    def _emit_registered(self, source: RegistrationSource, path: str) -> None:
        events = getattr(self, "_events", None)
        if events is None:
            return

        # FR-INT-008: Apply redaction rules for security compliance
        event = LauncherLifecycleEvent(
            event_category=LAUNCHER_EVENT_EXECUTABLE_REGISTERED,
            state_before=RuntimeState.NOT_RUNNING,
            state_after=RuntimeState.RUNNING_READY,
            process_reference=path,
            reason_summary=f"registered_from_{source.value}",
        )

        if self._redaction_rules is not None:
            # Redact sensitive data in event fields
            raw_data = {
                "process_reference": event.process_reference,
                "reason_summary": event.reason_summary,
            }
            redacted = self._redaction_rules.redact_dict(raw_data)
            event = LauncherLifecycleEvent(
                event_category=LAUNCHER_EVENT_EXECUTABLE_REGISTERED,
                state_before=RuntimeState.NOT_RUNNING,
                state_after=RuntimeState.RUNNING_READY,
                process_reference=redacted.get("process_reference", path),
                reason_summary=redacted.get("reason_summary", f"registered_from_{source.value}"),
            )

        events(event)
