"""Type-hint unwrapping utilities for action dispatch.

Pure functions with no class or module dependency — safe for utility layer reuse.
"""

import inspect
import typing
from typing import Any


def unwrap_annotation(annotation: Any) -> Any | None:
    """Unwrap Optional/Annotated/Union type hints to get the underlying type.

    Handles:
    - Plain types (e.g. GetScreenshotRequestVO) → returns the type
    - Optional[X] / Union[X, None] → returns X
    - Annotated[X, metadata] → returns X

    Returns None if the annotation cannot be unwrapped.
    """
    if annotation is inspect.Parameter.empty:
        return None

    origin = typing.get_origin(annotation)
    if origin is None:
        return annotation if isinstance(annotation, type) else None

    if origin is typing.Union:
        args = [a for a in typing.get_args(annotation) if a is not type(None)]
        return args[0] if len(args) == 1 and isinstance(args[0], type) else None

    if origin is typing.Annotated:
        args = typing.get_args(annotation)
        return args[0] if args and isinstance(args[0], type) else None

    return None
