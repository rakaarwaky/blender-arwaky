"""Domain error types for the config domain."""

from __future__ import annotations

from ..common.taxonomy_core_vo import Details, ErrorString
from ..common.taxonomy_domain_error import BlenderMCPError


class ConfigError(BlenderMCPError):
    """Base for all configuration-related errors."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        message = message or ErrorString("Configuration error")
        super().__init__(message)
        self.details = details or {}


class ConfigParseError(ConfigError):
    """Raised when YAML parsing fails (strict mode)."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration parse error"))


class ConfigLoadError(ConfigError):
    """Raised when configuration loading fails (missing file, permission denied, oversized source)."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration load error"))


class ConfigValidationError(ConfigError):
    """Raised when configuration fails schema validation (strict mode)."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration validation error"))


class ConfigPathError(ConfigError):
    """Raised when a configuration path is invalid or malformed."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration path error"))


class ConfigTypeError(ConfigError):
    """Raised when a configuration value does not match expected type (strict mode)."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration type error"))


class ConfigRootResolutionError(ConfigError):
    """Raised when project root cannot be resolved from any strategy."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration root resolution error"))