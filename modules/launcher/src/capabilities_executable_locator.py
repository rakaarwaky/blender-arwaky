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

from modules.shared.src.launcher.contract_locate_register_protocol import LocateRegisterProtocol
from modules.shared.src.launcher.taxonomy_launcher_error import (
    ExecutableValidationError,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ExecutableReferenceVO,
    LauncherConfigVO,
    RegistrationOutcomeVO,
    RegistrationSource,
    VersionCompatibility,
)


class _CommandRunner(Protocol):
    """Runs a command and returns (returncode, stdout). DI boundary."""

    def __call__(self, args: list[str], timeout: float = 5.0) -> tuple[int, str]:
        ...


class ExecutableLocator(LocateRegisterProtocol):
    """Locates and registers the Blender executable per FR-LAU-001."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        config_provider: Callable[[], LauncherConfigVO] | None = None,
        command_runner: _CommandRunner | None = None,
    ) -> None:
        self._config_provider = config_provider or (lambda: LauncherConfigVO())
        self._runner = command_runner

    # ─── Block 2: Public Contract ────────────────────────────
    def locate_and_register(self, config: LauncherConfigVO, override: str | None = None) -> RegistrationOutcomeVO:
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
            return RegistrationOutcomeVO(executable=ref, source=source, registered=True)

        return RegistrationOutcomeVO(registered=False, error="No valid Blender executable found")

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _build_candidate_order(self, config: LauncherConfigVO, override: str | None) -> list[tuple[RegistrationSource, str]]:
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
        if not os.path.isfile(path) or not os.access(path, os.X_OK):
            raise ExecutableValidationError(f"Not an executable file: {path}")
        version = self._detect_version(path)
        compat = self._check_compatibility(version)
        return ExecutableReferenceVO(path=path, version_summary=version, compatibility=compat)

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

    def _register(self, config: LauncherConfigVO, path: str) -> None:
        provider = self._config_provider
        setter = getattr(provider, "set_executable_path", None)
        if callable(setter):
            setter(path)
