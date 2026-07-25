"""Compatibility shim for legacy blender_mcp_error imports."""

from modules.shared.src.taxonomy_domain_error import (
    AssetNotFoundError,
    BlenderConnectionFailure,
    BlenderMCPError,
    ConnectionError,
    DomainError,
    ExecutionError,
    InvalidCommandError,
    ProviderError,
    SceneValidationError,
    ValidationError,
)

__all__ = [
    "BlenderMCPError",
    "DomainError",
    "SceneValidationError",
    "AssetNotFoundError",
    "ValidationError",
    "ConnectionError",
    "ProviderError",
    "ExecutionError",
    "BlenderConnectionFailure",
    "InvalidCommandError",
]
