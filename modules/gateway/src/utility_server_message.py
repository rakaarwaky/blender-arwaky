"""Utility: Message framing for TCP socket communication (protocol v2).

Stateless standalone functions for encoding/decoding length-prefixed
JSON messages over TCP sockets. Deterministic framing for reliable
message boundaries. Supports both length-prefixed and plain JSON
for backward compatibility.
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

# Maximum frame size: 10 MB (binary: ~10 * 1024^2)
_MAX_FRAME_SIZE = 10_485_760


def encode_message(payload: dict[str, Any]) -> bytes:
    """Encode a dict as length-prefixed JSON bytes.

    Format: [4-byte length][UTF-8 JSON payload]

    Args:
        payload: The message dictionary to encode.

    Returns:
        Length-prefixed JSON bytes ready to send over TCP.
    """
    json_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(json_bytes) > _MAX_FRAME_SIZE:
        raise ValueError(f"Payload exceeds maximum frame size: {len(json_bytes)}")
    header = struct.pack(_HEADER_FORMAT, len(json_bytes))
    return header + json_bytes


def decode_message(data: bytes) -> tuple[int | None, dict[str, Any] | None]:
    """Decode a raw response buffer.

    Attempts length-prefixed framing first, falls back to plain JSON.

    Args:
        data: Raw bytes from socket read.

    Returns:
        Tuple of (message_length, parsed_dict). Either may be None if
        the buffer is incomplete or not valid JSON.
    """
    # Try length-prefixed first
    msg_len = decode_message_header(data)
    if msg_len is not None and len(data) >= _HEADER_SIZE + msg_len:
        payload_data = data[_HEADER_SIZE : _HEADER_SIZE + msg_len]
        try:
            return msg_len, decode_message_payload(payload_data)
        except json.JSONDecodeError:
            logger.warning("Length-prefixed payload is not valid JSON")

    # Fallback to plain JSON (backward compat)
    if len(data) > _HEADER_SIZE:
        try:
            return None, json.loads(data[_HEADER_SIZE:].decode("utf-8"))
        except json.JSONDecodeError:
            pass

    return None, None


def decode_message_header(data: bytes) -> int | None:
    """Extract message length from header bytes.

    Returns message length if enough bytes, None otherwise.

    Args:
        data: Bytes to extract header from.

    Returns:
        Message length in bytes, or None if incomplete header.
    """
    if len(data) < _HEADER_SIZE:
        return None
    (length,) = struct.unpack(_HEADER_FORMAT, data[:_HEADER_SIZE])
    return length


def decode_message_payload(data: bytes) -> dict[str, Any]:
    """Decode JSON payload from bytes.

    Raises json.JSONDecodeError if payload is not valid JSON.

    Args:
        data: JSON bytes to decode.

    Returns:
        Parsed message dictionary.
    """
    return json.loads(data.decode("utf-8"))


def build_request(
    message_type: str,
    params: dict[str, Any],
    request_id: str,
    protocol_version: str = "2.0.0",
) -> bytes:
    """Build a framed request message (protocol v2).

    Args:
        message_type: The message type string (e.g., 'handshake', 'command').
        params: Message parameters dictionary.
        request_id: UUID4 tracking ID.
        protocol_version: Protocol version string.

    Returns:
        Length-prefixed JSON bytes ready to send over TCP.
    """
    payload: dict[str, Any] = {
        "type": message_type,
        "request_id": request_id,
        "protocol_version": protocol_version,
    }
    if params:
        payload["params"] = params
    return encode_message(payload)


def parse_response(data: bytes) -> dict[str, Any]:
    """Parse a raw response bytes into a dict.

    Handles both length-prefixed and plain JSON for backward compatibility.

    Args:
        data: Raw response bytes.

    Returns:
        Parsed message dictionary.

    Raises:
        json.JSONDecodeError: If payload is not valid JSON.
    """
    _, parsed = decode_message(data)
    if parsed is None:
        raise json.JSONDecodeError("Empty or invalid response", "", 0)
    return parsed


def build_handshake_request(request_id: str, protocol_version: str = "2.0.0") -> bytes:
    """Build a handshake request message (protocol v2).

    Args:
        request_id: UUID4 tracking ID.
        protocol_version: Server protocol version.

    Returns:
        Length-prefixed handshake request bytes.
    """
    return build_request("handshake", {}, request_id, protocol_version)


def build_ping_request(request_id: str) -> bytes:
    """Build a ping (heartbeat) request message.

    Args:
        request_id: UUID4 tracking ID.

    Returns:
        Length-prefixed ping request bytes.
    """
    return build_request("ping", {}, request_id, "2.0.0")


def build_command_request(
    action: str,
    params: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> bytes:
    """Build a command request message.

    Args:
        action: The command action name.
        params: Command parameters.
        request_id: UUID4 tracking ID (generated if None).

    Returns:
        Length-prefixed command request bytes.
    """
    rid = request_id or ""
    payload_params: dict[str, Any] = {}
    if params:
        payload_params["action"] = action
        payload_params.update(params)
    return build_request("command", payload_params, rid, "2.0.0")
