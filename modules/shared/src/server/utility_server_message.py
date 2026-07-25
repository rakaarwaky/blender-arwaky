"""Utility: Message framing for TCP socket communication.

Stateless standalone functions for encoding/decoding length-prefixed
JSON messages over TCP sockets. Deterministic framing for reliable
message boundaries.
"""

from __future__ import annotations

import json
import logging
import struct
from typing import Any

logger = logging.getLogger("BlenderMCPServer")

# Header format: 4-byte big-endian unsigned integer for message length
_HEADER_FORMAT = "!I"
_HEADER_SIZE = struct.calcsize(_HEADER_FORMAT)


def encode_message(payload: dict[str, Any]) -> bytes:
    """Encode a dict as length-prefixed JSON bytes.

    Format: [4-byte length][UTF-8 JSON payload]
    """
    json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    header = struct.pack(_HEADER_FORMAT, len(json_bytes))
    return header + json_bytes


def decode_message_header(data: bytes) -> int | None:
    """Extract message length from header bytes.

    Returns message length if enough bytes, None otherwise.
    """
    if len(data) < _HEADER_SIZE:
        return None
    (length,) = struct.unpack(_HEADER_FORMAT, data[:_HEADER_SIZE])
    return length


def decode_message_payload(data: bytes) -> dict[str, Any]:
    """Decode JSON payload from bytes.

    Raises json.JSONDecodeError if payload is not valid JSON.
    """
    return json.loads(data.decode("utf-8"))


def build_request(
    command_type: str,
    params: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> bytes:
    """Build a framed request message.

    Returns length-prefixed JSON bytes ready to send over TCP.
    """
    payload: dict[str, Any] = {"type": command_type}
    if params:
        payload["params"] = params
    if request_id:
        payload["request_id"] = request_id
    return encode_message(payload)


def parse_response(data: bytes) -> dict[str, Any]:
    """Parse a raw response bytes into a dict.

    Handles both length-prefixed and plain JSON for backward compatibility.
    """
    # Try length-prefixed first
    msg_len = decode_message_header(data)
    if msg_len is not None and len(data) >= _HEADER_SIZE + msg_len:
        payload_data = data[_HEADER_SIZE : _HEADER_SIZE + msg_len]
        return decode_message_payload(payload_data)

    # Fallback to plain JSON (backward compat)
    return json.loads(data.decode("utf-8"))
