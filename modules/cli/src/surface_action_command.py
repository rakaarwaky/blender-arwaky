"""Generic CLI surface for dedicated action-to-dispatcher mappings."""

from __future__ import annotations

from types import SimpleNamespace

from .surface_run_command import handle as handle_run


def handle(
    action_name: str,
    params: dict[str, object],
    args: object,
    dispatcher: object | None = None,
) -> dict[str, object]:
    """Route one dedicated CLI command through the universal action surface."""
    request = SimpleNamespace(
        action=action_name,
        params={key: value for key, value in params.items() if value is not None},
        filepath=getattr(args, "filepath", ""),
        confirm=bool(getattr(args, "confirm", False)),
        force=bool(getattr(args, "force", False)),
    )
    return handle_run(request, dispatcher)
