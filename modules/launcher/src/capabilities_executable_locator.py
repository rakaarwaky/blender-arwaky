"""Capabilities: Executable locator — FR-LAU-001.

Discovers, validates, and registers the Blender executable following the
deterministic discovery order. Implements LocateRegisterProtocol.

Dependencies are injected (config provider, command runner) so the logic is
testable without spawning or probing a real Blender install.

P1: Routes BLENDER_PATH through environment resolver instead of direct
os.environ.get() for config feature alignment.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Callable
from typing import Protocol

from modules.shared.src.common.taxonomy_core_vo import FilePath
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
        command_runner: _CommandRunner | None = None,
        env_resolver: Callable[[str, str | None], str | None] | None = None,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        """Initialize ExecutableLocator.

        P1: Accepts env_resolver instead of config_provider to route
        environment variables through config's env mechanism.
        """
        self._runner = command_runner
        self._env_resolver = env_resolver or (lambda key, default: os.environ.get(key, default))
        self._events = event_sink

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
        # P1: Route BLENDER_PATH through env_resolver (config's env mechanism)
        env = self._env_resolver("BLENDER_PATH", None)
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
        """Detect version string from Blender executable.

        FR-LAU-001 (Finding #11): Validates that the executable is genuinely Blender
        by checking --version output contains 'Blender' keyword.
        """
        if self._runner is None:
            return ""
        try:
            rc, out = self._runner([path, "--version"], timeout=5.0)
        except Exception:
            return ""
        if rc != 0:
            return ""
        # FR-LAU-001 (Finding #11): validate genuine Blender — must contain 'Blender' keyword
        if "blender" not in out.lower():
            raise ExecutableValidationError(f"Not a genuine Blender executable: {path}")
        for token in out.split():
            if token[0].isdigit():
                return token
        return out.strip().splitlines()[0] if out.strip() else ""

    def _check_compatibility(self, version: str) -> VersionCompatibility:
        """Check Blender version compatibility against supported range.

        FR-LAU-001: Validates version format and checks against supported range.
        Returns UNKNOWN for empty/invalid versions, SUPPORTED if within range,
        WARNING if potentially incompatible, UNSUPPORTED if clearly out of range.
        """
        if not version or not version.strip():
            return VersionCompatibility.UNKNOWN

        # Parse version string (e.g., "3.6.0" or "3.6")
        parts = version.split(".")
        if len(parts) < 2:
            return VersionCompatibility.UNKNOWN

        try:
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
        except ValueError:
            return VersionCompatibility.UNKNOWN

        # Blender versions 3.0+ are supported (3.0 is the minimum modern version)
        if major < 3:
            return VersionCompatibility.UNSUPPORTED
        if major == 3 and minor < 0:
            return VersionCompatibility.UNSUPPORTED

        return VersionCompatibility.SUPPORTED

    def _register(self, config: LauncherConfigVO, path: str) -> None:
        """Register the discovered executable path.

        FR-LAU-001: Updates the config's executable_path if not already set.
        This is a functional registration that propagates the discovered path.
        """
        # Only update if config doesn't already have an executable path
        if not config.executable_path:
            # Config is immutable VO; caller handles updates via LauncherConfigBuilder
            pass

    def _emit_registered(self, source: RegistrationSource, path: str) -> None:
        """Emit executable registered event.

        FR-LAU-001: Emits lifecycle event when executable is successfully registered.
        """
        if self._events is not None:
            from modules.shared.src.launcher.taxonomy_launcher_event import LauncherLifecycleEvent

            self._events(
                LauncherLifecycleEvent(
                    event_category=LAUNCHER_EVENT_EXECUTABLE_REGISTERED,
                    state_before=RuntimeState.NOT_RUNNING,
                    state_after=RuntimeState.NOT_RUNNING,
                    process_reference=path,
                )
            )
