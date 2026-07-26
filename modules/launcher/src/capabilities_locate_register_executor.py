"""Locate & register capability — discover and validate Blender executable.

FR-LAU-001: Locate and Register Application
- Searches for Blender executable in deterministic order
- Validates executable exists, is authentic Blender runtime
- Checks version compatibility against supported range
- Registers path via config or state store
- Normalizes path, handles symlinks safely
"""

import logging
import os
import shutil
import subprocess

from modules.shared.src.launcher.contract_locate_register_protocol import (
    LocateRegisterProtocol,
)
from modules.shared.src.launcher.taxonomy_launcher_constant import (
    LAUNCHER_MODE_INTERFACE,
)
from modules.shared.src.launcher.taxonomy_launcher_error import (
    LauncherConfigError,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ExecutableReferenceVO,
    LauncherConfigVO,
    RegistrationResultVO,
    RegistrationSource,
    VersionCompatibility,
)

logger = logging.getLogger("BlenderMCPServer")


class LocateRegisterExecutor(LocateRegisterProtocol):
    """Concrete implementation for locating and registering Blender executable.

    FR-LAU-001: Discovers via deterministic order, validates authenticity,
    checks version compatibility, registers through config or state store.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self) -> None:
        self._registered_path: str | None = None

    # ─── Block 2: Protocol Method Implementation ─────────────

    def locate_and_register(
        self,
        config: LauncherConfigVO,
        override: str | None = None,
    ) -> RegistrationResultVO:
        """Discover, validate, and register a Blender executable per discovery order.

        FR-LAU-001: Deterministic search order — override > configured > env > platform > system.
        Returns registration result with validated reference and source classification.
        """
        # 1. Explicit override (highest priority)
        if override:
            candidate = self._resolve_path(override)
            if candidate and self._validate_candidate(candidate):
                version_summary, compatibility = self._check_version(candidate)
                ref = ExecutableReferenceVO(path=candidate, version_summary=version_summary, compatibility=compatibility)
                self._register_path(candidate)
                logger.info("Registered Blender via override: %s (v%s)", candidate, version_summary)
                return RegistrationResultVO(executable=ref, source=RegistrationSource.OVERRIDE, registered=True)

        # 2. Configured path
        if config.executable_path:
            candidate = self._resolve_path(config.executable_path)
            if candidate and self._validate_candidate(candidate):
                version_summary, compatibility = self._check_version(candidate)
                ref = ExecutableReferenceVO(path=candidate, version_summary=version_summary, compatibility=compatibility)
                self._register_path(candidate)
                logger.info("Registered Blender via configured path: %s (v%s)", candidate, version_summary)
                return RegistrationResultVO(executable=ref, source=RegistrationSource.CONFIGURED, registered=True)

        # 3. Environment signal
        env_path = os.environ.get("BLENDER_PATH") or os.environ.get("BLENDER_EXECUTABLE")
        if env_path:
            candidate = self._resolve_path(env_path)
            if candidate and self._validate_candidate(candidate):
                version_summary, compatibility = self._check_version(candidate)
                ref = ExecutableReferenceVO(path=candidate, version_summary=version_summary, compatibility=compatibility)
                self._register_path(candidate)
                logger.info("Registered Blender via environment: %s (v%s)", candidate, version_summary)
                return RegistrationResultVO(executable=ref, source=RegistrationSource.ENVIRONMENT, registered=True)

        # 4. Platform-standard locations
        for location in config.search_locations or ():
            candidate = self._resolve_path(location)
            if candidate and self._validate_candidate(candidate):
                version_summary, compatibility = self._check_version(candidate)
                ref = ExecutableReferenceVO(path=candidate, version_summary=version_summary, compatibility=compatibility)
                self._register_path(candidate)
                logger.info("Registered Blender via platform location: %s (v%s)", candidate, version_summary)
                return RegistrationResultVO(executable=ref, source=RegistrationSource.PLATFORM, registered=True)

        # 5. System path
        system_blender = shutil.which("blender")
        if system_blender and self._validate_candidate(system_blender):
            version_summary, compatibility = self._check_version(system_blender)
            ref = ExecutableReferenceVO(path=system_blender, version_summary=version_summary, compatibility=compatibility)
            self._register_path(system_blender)
            logger.info("Registered Blender via system path: %s (v%s)", system_blender, version_summary)
            return RegistrationResultVO(executable=ref, source=RegistrationSource.SYSTEM_PATH, registered=True)

        # No valid candidate found
        logger.error("No valid Blender executable found")
        raise LauncherConfigError("Cannot locate a usable Blender executable")

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _resolve_path(self, path: str) -> str | None:
        """Resolve and normalize a potential executable path."""
        try:
            resolved = os.path.realpath(path)
            if not os.path.isfile(resolved):
                return None
            if not os.access(resolved, os.X_OK):
                return None
            return resolved
        except (OSError, ValueError):
            return None

    def _validate_candidate(self, path: str) -> bool:
        """Validate that path is a genuine Blender runtime."""
        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                timeout=10,
            )
            if result.returncode != 0:
                return False
            output = result.stdout.decode(errors="replace").lower()
            return "blender" in output
        except (subprocess.TimeoutExpired, OSError, ValueError):
            return False

    def _check_version(self, path: str) -> tuple[str, VersionCompatibility]:
        """Check Blender version against supported range."""
        SUPPORTED_MAJOR_MIN = 3

        try:
            result = subprocess.run(
                [path, "--version"],
                capture_output=True,
                timeout=10,
            )
            output = result.stdout.decode(errors="replace")
            parts = output.split()
            for i, part in enumerate(parts):
                if part == "Blender":
                    version_str = parts[i + 1] if i + 1 < len(parts) else "unknown"
                    major = self._parse_major(version_str)
                    compatibility = (
                        VersionCompatibility.SUPPORTED
                        if major >= SUPPORTED_MAJOR_MIN
                        else VersionCompatibility.UNSUPPORTED
                    )
                    return version_str, compatibility

        except (subprocess.TimeoutExpired, OSError, IndexError):
            pass

        return "unknown", VersionCompatibility.UNKNOWN

    def _parse_major(self, version_str: str) -> int:
        """Extract major version number from version string."""
        try:
            parts = version_str.split(".")
            return int(parts[0]) if parts else 0
        except (ValueError, IndexError):
            return 0

    def _register_path(self, path: str) -> None:
        """Store the validated executable path internally."""
        self._registered_path = path

    def get_registered_path(self) -> str | None:
        """Return the currently registered Blender executable path."""
        return self._registered_path

    def __repr__(self) -> str:
        return f"LocateRegisterExecutor(path={self._registered_path})"
