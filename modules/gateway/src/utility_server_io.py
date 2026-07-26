"""Utility: File I/O and temporary path helpers.

Stateless standalone functions for safe file operations, temporary
path generation, and cleanup. Domain-agnostic — reusable across modules.
"""

from __future__ import annotations

import contextlib
import logging
import os
import tempfile
from pathlib import Path

logger = logging.getLogger("BlenderMCPServer")


def generate_temp_path(suffix: str = ".tmp", prefix: str = "blender_") -> str:
    """Generate a unique temporary file path.

    Uses the system temp directory and creates a UUID-based filename
    to avoid collisions. Does not create the file.

    Args:
        suffix: File extension suffix (default: '.tmp').
        prefix: Filename prefix (default: 'blender_').

    Returns:
        Full path string for a new temporary file.
    """
    return os.path.join(tempfile.gettempdir(), f"{prefix}_{suffix}")


def read_file_bytes(filepath: str) -> bytes:
    """Read a file's contents as bytes.

    Args:
        filepath: Absolute path to the file.

    Returns:
        File content as bytes.

    Raises:
        FileNotFoundError: If the file does not exist.
        PermissionError: If the file cannot be read.
    """
    return Path(filepath).read_bytes()


def write_file_bytes(filepath: str, data: bytes) -> None:
    """Write bytes to a file, creating parent directories if needed.

    Args:
        filepath: Absolute path to the target file.
        data: Bytes to write.
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    Path(filepath).write_bytes(data)


def write_file_text(filepath: str, text: str, encoding: str = "utf-8") -> None:
    """Write text to a file, creating parent directories if needed.

    Args:
        filepath: Absolute path to the target file.
        text: Text content to write.
        encoding: File encoding (default: 'utf-8').
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    Path(filepath).write_text(text, encoding=encoding)


def safe_remove(filepath: str) -> bool:
    """Safely remove a file, suppressing errors.

    Returns True if the file was removed, False if it did not exist
    or could not be removed.

    Args:
        filepath: Absolute path to the file to remove.

    Returns:
        True if removal succeeded or file already absent.
    """
    with contextlib.suppress(OSError, PermissionError):
        Path(filepath).unlink(missing_ok=True)
        return True
    return False


def truncate_bytes(data: bytes, max_bytes: int) -> tuple[bytes, bool]:
    """Truncate bytes to a maximum size.

    Args:
        data: Original byte string.
        max_bytes: Maximum allowed bytes.

    Returns:
        Tuple of (truncated bytes, was_truncated flag).
    """
    if len(data) <= max_bytes:
        return data, False
    return data[:max_bytes], True


def truncate_text(text: str, max_chars: int) -> tuple[str, bool]:
    """Truncate text to a maximum character count.

    Args:
        text: Original text string.
        max_chars: Maximum allowed characters.

    Returns:
        Tuple of (truncated text, was_truncated flag).
    """
    if len(text) <= max_chars:
        return text, False
    return text[:max_chars], True


def format_bytes(size_bytes: int) -> str:
    """Format byte count to human-readable string using binary notation.

    Uses binary notation (1k = 1024 bytes) per user preference.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Formatted string like '1.5k', '256B', '1.2M'.
    """
    if size_bytes < 1024:
        return f"{size_bytes}B"

    units = [("k", 1024), ("M", 1024**2), ("G", 1024**3), ("T", 1024**4)]

    for unit, threshold in reversed(units):
        if size_bytes >= threshold:
            value = size_bytes / threshold
            if value >= 10:
                return f"{int(value)}{unit}"
            return f"{value:.1f}{unit}"

    return f"{size_bytes}B"


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """Sanitize a string to be safe as a filename.

    Removes or replaces characters that are invalid in filenames
    across common filesystems. Does not truncate.

    Args:
        name: Original filename or path component.
        replacement: Character to replace invalid chars with
                     (default: '_').

    Returns:
        Sanitized filename string.
    """
    unsafe_chars = "<>:\"|?*/\\*[],"
    result = name
    for char in unsafe_chars:
        result = result.replace(char, replacement)
    return result.strip(" .")


def is_safe_path(path: str, allowed_base: str) -> bool:
    """Check if a path is within an allowed base directory.

    Prevents directory traversal attacks by resolving symlinks
    and checking the normalized path prefix.

    Args:
        path: Absolute or relative path to check.
        allowed_base: Base directory that must contain the path.

    Returns:
        True if the path is safely within allowed_base.
    """
    base = Path(allowed_base).resolve()
    target = Path(path).resolve()
    return str(target).startswith(str(base))
