"""Utility: String sanitization, validation, and formatting.

Stateless standalone functions for text processing, encoding,
and safe string operations. Domain-agnostic — reusable across modules.
"""

from __future__ import annotations

import re
from typing import Final

# Common patterns
_UTF8_BOM: Final[bytes] = b"\xef\xbb\xbf"
_WHITESPACE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\s+", re.UNICODE)
_NEWLINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\r?\n")


def sanitize_whitespace(text: str) -> str:
    """Collapse all whitespace sequences into single spaces.

    Args:
        text: Input string with potentially excessive whitespace.

    Returns:
        String with normalized single-space whitespace.
    """
    return _WHITESPACE_PATTERN.sub(" ", text).strip()


def normalize_newlines(text: str) -> str:
    """Normalize line endings to Unix style (\\n).

    Converts \\r\\n and \\r to \\n.

    Args:
        text: Input string with mixed line endings.

    Returns:
        String with normalized \\n line endings.
    """
    return _NEWLINE_PATTERN.sub("\n", text)


def truncate_string(text: str, max_length: int, ellipsis: str = "...") -> str:
    """Truncate a string to a maximum length with optional ellipsis.

    Args:
        text: Input string to truncate.
        max_length: Maximum total length including ellipsis.
        ellipsis: Truncation indicator (default: '...').

    Returns:
        Truncated string, or original if under limit.
    """
    if len(text) <= max_length:
        return text

    available = max_length - len(ellipsis)
    if available < 0:
        return ellipsis[:max_length]

    return text[:available] + ellipsis


def safe_decode(data: bytes, encoding: str = "utf-8") -> str:
    """Safely decode bytes to string, replacing invalid sequences.

    Args:
        data: Bytes to decode.
        encoding: Target encoding (default: 'utf-8').

    Returns:
        Decoded string with replacement characters for invalid bytes.
    """
    return data.decode(encoding, errors="replace")


def safe_encode(text: str, encoding: str = "utf-8") -> bytes:
    """Safely encode string to bytes, replacing invalid sequences.

    Args:
        text: String to encode.
        encoding: Target encoding (default: 'utf-8').

    Returns:
        Encoded bytes with replacement characters for invalid chars.
    """
    return text.encode(encoding, errors="replace")


def starts_with_any(text: str, prefixes: list[str]) -> bool:
    """Check if text starts with any of the given prefixes.

    Args:
        text: String to check.
        prefixes: List of prefix strings to match.

    Returns:
        True if text starts with any prefix.
    """
    return any(text.startswith(p) for p in prefixes)


def ends_with_any(text: str, suffixes: list[str]) -> bool:
    """Check if text ends with any of the given suffixes.

    Args:
        text: String to check.
        suffixes: List of suffix strings to match.

    Returns:
        True if text ends with any suffix.
    """
    return any(text.endswith(s) for s in suffixes)


def contains_any(text: str, substrings: list[str]) -> bool:
    """Check if text contains any of the given substrings.

    Args:
        text: String to search within.
        substrings: List of substring patterns to match.

    Returns:
        True if any substring is found in text.
    """
    return any(s in text for s in substrings)


def safe_int(value: str, default: int = 0) -> int:
    """Safely convert a string to integer, returning default on failure.

    Args:
        value: String to convert.
        default: Fallback value if conversion fails (default: 0).

    Returns:
        Integer value, or default if conversion failed.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: str, default: float = 0.0) -> float:
    """Safely convert a string to float, returning default on failure.

    Args:
        value: String to convert.
        default: Fallback value if conversion fails (default: 0.0).

    Returns:
        Float value, or default if conversion failed.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def camel_to_snake(name: str) -> str:
    """Convert CamelCase or PascalCase to snake_case.

    Handles common patterns like 'HTMLParser' → 'html_parser',
    'MyClassName' → 'my_class_name'.

    Args:
        name: CamelCase or PascalCase string.

    Returns:
        snake_case string.
    """
    result = re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
    return result


def snake_to_camel(name: str, capitalize_first: bool = True) -> str:
    """Convert snake_case to CamelCase or camelCase.

    Args:
        name: snake_case string.
        capitalize_first: If True, produces CamelCase.
                         If False, produces camelCase (default: True).

    Returns:
        CamelCase or camelCase string.
    """
    parts = name.split("_")
    if capitalize_first:
        return "".join(p.capitalize() for p in parts)
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def escape_json_string(value: str) -> str:
    """Escape a string for safe inclusion in JSON.

    Handles common special characters that need escaping in JSON
    strings beyond what json.dumps already handles.

    Args:
        value: Raw string to escape.

    Returns:
        Escaped string safe for JSON embedding.
    """
    return (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
    )


def is_valid_python_identifier(name: str) -> bool:
    """Check if a string is a valid Python identifier.

    Args:
        name: String to validate.

    Returns:
        True if the string is a valid Python identifier.
    """
    return bool(re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name))
