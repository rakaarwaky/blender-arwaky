"""MCP CLI Wrapper: Subprocess bridge to blender-arwaky CLI.

FR-MCP-001: Expose MCP Tools — run_cli_command provides CLI invocation as MCP tool
FR-MCP-002: Route Tool Calls — wrapper routes MCP tool calls to CLI subprocess
FR-MCP-003: Format MCP Responses — wrapper returns standardized JSON responses for MCP client
"""

import asyncio
import json
import os
import sys
from typing import Any


async def run_cli_command(
    command: str,
    args: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Run a CLI command and return the result.

    Args:
        command: CLI command name (init, run, screenshot, render, close, status)
        args: Command arguments
        timeout: Timeout in seconds

    Returns:
        Parsed JSON result from CLI
    """
    # Build CLI command
    cmd = [sys.executable, "-m", "cli.main", command]

    # Add arguments based on command type
    if args:
        if command == "init":
            cmd.extend(["--filepath", args.get("filepath", "")])
            if "mode" in args:
                cmd.extend(["--mode", args["mode"]])
            if "port" in args:
                cmd.extend(["--port", str(args["port"])])

        elif command == "run":
            cmd.extend(["--filepath", args.get("filepath", "")])
            cmd.extend(["--action", args.get("action", "")])
            if "params" in args:
                cmd.extend(["--params", json.dumps(args["params"])])

        elif command == "screenshot":
            cmd.extend(["--filepath", args.get("filepath", "")])
            cmd.extend(["--output", args.get("output", "")])
            if "max_size" in args:
                cmd.extend(["--max-size", str(args["max_size"])])
            if "view_angle" in args:
                cmd.extend(["--view-angle", args["view_angle"]])
            if "shading" in args:
                cmd.extend(["--shading", args["shading"]])
            if args.get("show_overlays") is False:
                cmd.append("--no-overlays")
            if "focus_object" in args:
                cmd.extend(["--focus-object", args["focus_object"]])

        elif command == "render":
            cmd.extend(["--filepath", args.get("filepath", "")])
            cmd.extend(["--output", args.get("output", "")])
            if "resolution_x" in args:
                cmd.extend(["--resolution-x", str(args["resolution_x"])])
            if "resolution_y" in args:
                cmd.extend(["--resolution-y", str(args["resolution_y"])])

        elif command == "close":
            cmd.extend(["--filepath", args.get("filepath", "")])

    cmd.append("--json")

    try:
        # Run CLI subprocess
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await asyncio.wait_for(
            proc.communicate(),
            timeout=timeout,
        )

        stdout_str = stdout.decode("utf-8").strip()
        stderr_str = stderr.decode("utf-8").strip()

        if proc.returncode != 0:
            error_msg = stderr_str or stdout_str or "CLI command failed"
            return {"success": False, "error": error_msg, "exit_code": proc.returncode}

        # Parse JSON output
        try:
            result = json.loads(stdout_str) if stdout_str else {"success": True}
        except json.JSONDecodeError:
            result = {"success": True, "message": stdout_str}

        return result

    except asyncio.TimeoutError:
        return {"success": False, "error": f"CLI command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": f"CLI execution error: {e}"}


async def init_entity(filepath: str, mode: str = "headless") -> dict[str, Any]:
    """Initialize a Blender entity."""
    return await run_cli_command("init", {"filepath": filepath, "mode": mode})


async def execute_action(filepath: str, action: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute an action on the active Blender entity."""
    return await run_cli_command("run", {"filepath": filepath, "action": action, "params": params or {}})


async def capture_screenshot(
    filepath: str,
    output: str,
    max_size: int = 800,
    view_angle: str = "PERSPECTIVE",
    shading: str = "MATERIAL",
    show_overlays: bool = True,
    focus_object: str | None = None,
) -> dict[str, Any]:
    """Capture a viewport screenshot."""
    result = await run_cli_command(
        "screenshot",
        {
            "filepath": filepath,
            "output": output,
            "max_size": max_size,
            "view_angle": view_angle,
            "shading": shading,
            "show_overlays": show_overlays,
            "focus_object": focus_object,
        },
    )

    # If successful, read the image file and encode to base64
    if result.get("success") and os.path.exists(output):
        import base64

        with open(output, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("ascii")
        os.remove(output)  # Clean up temp file
        result["image_data"] = image_data

    return result


async def render_frame(
    filepath: str,
    output: str,
    resolution_x: int = 1920,
    resolution_y: int = 1080,
) -> dict[str, Any]:
    """Execute a full frame render."""
    result = await run_cli_command(
        "render",
        {
            "filepath": filepath,
            "output": output,
            "resolution_x": resolution_x,
            "resolution_y": resolution_y,
        },
    )

    # If successful, read the image file and encode to base64
    if result.get("success") and os.path.exists(output):
        import base64

        with open(output, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("ascii")
        os.remove(output)  # Clean up temp file
        result["image_data"] = image_data

    return result


async def close_entity(filepath: str) -> dict[str, Any]:
    """Close the active Blender entity."""
    return await run_cli_command("close", {"filepath": filepath})


async def get_status() -> dict[str, Any]:
    """Get status of the active Blender entity."""
    return await run_cli_command("status")
