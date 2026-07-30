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
from modules.shared.src.launcher.contract_locate_register_protocol import LocateRegisterProtocol
from modules.shared.src.launcher.taxonomy_launcher_constant import LAUNCHER_EVENT_EXECUTABLE_REGISTERED
from modules.shared.src.launcher.taxonomy_launcher_error import ExecutableValidationError
from modules.shared.src.launcher.taxonomy_launcher_event import LauncherLifecycleEvent
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ExecutableReferenceVO,
    LauncherConfigVO,
    LauncherErrorCode,
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
    ) -> None:
        self._config_provider = config_provider or (lambda: LauncherConfigVO())
        self._runner = command_runner
        self._events = event_sink

    # ─── Block 2: Public Contract ────────────────────────────
    def locate_and_register(self, override: FilePath | None = None) -> RegistrationOutcomeVO:
        """Discover, validate, and register a Blender executable."""
        config = self._config_provider()
        candidates = self._build_candidate_order(config, override)
        if not candidates:
            return RegistrationOutcomeVO(
                registered=False,
                error_code=LauncherErrorCode.CONFIGURATION_ERROR,
                error_message="No candidate locations available",
            )

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

        return RegistrationOutcomeVO(
            registered=False,
            error_code=LauncherErrorCode.VALIDATION_ERROR,
            error_message="No valid Blender executable found",
        )

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
        if not version:
            return VersionCompatibility.UNKNOWN
        return VersionCompatibility.SUPPORTED

    def _register(self, _config: LauncherConfigVO, path: str) -> None:
        provider = self._config_provider
        setter = getattr(provider, "set_executable_path", None)
        if callable(setter):
            setter(path)

    def _emit_registered(self, source: RegistrationSource, path: str) -> None:
        events = getattr(self, "_events", None)
        if events is not None:
            events(
                LauncherLifecycleEvent(
                    event_category=LAUNCHER_EVENT_EXECUTABLE_REGISTERED,
                    state_before=RuntimeState.NOT_RUNNING,
                    state_after=RuntimeState.RUNNING_READY,
                    process_reference=path,
                    reason_summary=f"registered_from_{source.value}",
                )
            )
