"""Code execution adapter with input validation and safety checks."""

import asyncio
import logging
import re

from contract import BlenderConnectionPort, CodeExecutionPort
from taxonomy import ActionName, ErrorMessage, Prompt
from taxonomy.blender_mcp_error import ValidationError

logger = logging.getLogger("BlenderMCPServer")

# Maximum code length (chars) to prevent abuse
MAX_CODE_LENGTH = 10_000

# Blocked patterns — dangerous system-level operations.
# These are pre-filters to catch common abuse; they are NOT a security boundary.
# The actual execution happens inside Blender's trusted process, so the real
# trust model is: "reject obviously malicious payloads before forwarding."
# Regex-based filtering is inherently bypassable (e.g., getattr(os, "system")),
# AST parsing or a proper sandbox would be stronger controls.
_BLOCKED: list[tuple[re.Pattern[str], str]] = [
    # OS-level operations
    (re.compile(r"\bos\.system\s*\(", re.IGNORECASE), "os.system()"),
    (re.compile(r"\bos\.popen\s*\(", re.IGNORECASE), "os.popen()"),
    (re.compile(r"\bos\.exec\w*\s*\(", re.IGNORECASE), "os.exec*()"),
    (re.compile(r"\bos\.spawn\w*\s*\(", re.IGNORECASE), "os.spawn*()"),
    (re.compile(r"\bos\.remove\s*\(", re.IGNORECASE), "os.remove()"),
    (re.compile(r"\bos\.unlink\s*\(", re.IGNORECASE), "os.unlink()"),
    (re.compile(r"\bos\.rmdir\s*\(", re.IGNORECASE), "os.rmdir()"),
    # Subprocess / shell
    (re.compile(r"\bsubprocess\b", re.IGNORECASE), "subprocess"),
    (re.compile(r"\bshutil\.rmtree\s*\(", re.IGNORECASE), "shutil.rmtree()"),
    (re.compile(r"\bshutil\.move\s*\(", re.IGNORECASE), "shutil.move()"),
    # Dynamic import / code execution
    (re.compile(r"__import__\s*\("), "__import__()"),
    (re.compile(r"\bimportlib\b"), "importlib"),
    (re.compile(r"\beval\s*\("), "eval()"),
    (re.compile(r"\bexec\s*\("), "exec()"),
    (re.compile(r"\bcompile\s*\("), "compile()"),
    # File system access
    (re.compile(r"\bopen\s*\("), "open()"),
    # Network
    (re.compile(r"\bsocket\s*\.\s*socket\s*\("), "socket.socket()"),
    (re.compile(r"\brequests\.(get|post|put|delete|patch)\s*\("), "requests HTTP"),
    (re.compile(r"\burllib\b"), "urllib"),
]


def validate_code(code: str) -> None:
    """Validate code for abuse prevention before execution.

    Raises ValidationError if the code contains known-bad patterns
    or exceeds length limits.

    NOTE: This is a pre-filter, not a security boundary. Regex-based
    filtering is inherently bypassable (e.g., getattr(os, "system")).
    The actual execution happens inside Blender's trusted process.
    """
    if not code or not code.strip():
        raise ValidationError(ErrorMessage("Code cannot be empty"))

    if len(code) > MAX_CODE_LENGTH:
        raise ValidationError(
            ErrorMessage(f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters (received {len(code)})")
        )

    for pattern, description in _BLOCKED:
        if pattern.search(code):
            logger.warning(
                "Blocked code execution attempt: pattern '%s' detected",
                description,
            )
            raise ValidationError(
                ErrorMessage(
                    f"Code contains blocked pattern: {description}. "
                    f"For security, system-level operations are not allowed "
                    f"through execute_blender_code. Use Blender's Python API (bpy) instead."
                )
            )


class CodeExecutionAdapter(CodeExecutionPort):
    """Wrapper class for code execution functions with input validation."""

    def __init__(self, connection_port: BlenderConnectionPort):
        self._connection_port = connection_port

    async def execute_blender_code(self, code: Prompt) -> Prompt:
        """Execute Python code in Blender via IPC.

        This method validates the code against a denylist of dangerous
        patterns (regex pre-filter), then forwards it to Blender through
        the socket adapter. It does NOT sandbox the code — the actual
        execution happens inside Blender's trusted process.

        Returns:
            Prompt with either a success message (containing the result)
            or an error message (validation failure or IPC exception).
        """
        code_str = str(code)

        # Validate input before sending to Blender
        try:
            validate_code(code_str)
        except ValidationError as e:
            logger.warning("Code validation failed: %s", e)
            return Prompt(f"Validation error: {e}")

        # Audit log — record all code execution attempts
        logger.info(
            "Executing Blender code (length=%d chars): %.100s%s",
            len(code_str),
            code_str,
            "..." if len(code_str) > 100 else "",
        )

        try:
            # Offload synchronous IPC call to thread pool to avoid blocking event loop
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._connection_port.send_command(ActionName("execute_code"), {"code": code_str}),
            )
            # result is a dict from send_command; extract 'result' safely
            return Prompt(f"Code executed successfully: {result.get('result', '')}")
        except ValidationError:
            # Re-raise validation errors (shouldn't reach here, but be safe)
            raise
        except Exception:
            logger.exception("Error executing code in Blender")
            return Prompt("Internal server error during code execution.")
