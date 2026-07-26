"""Scene domain constants.

Compile-time literal values for scene management.
No classes, no functions — only ALL_CAPS declarations.
"""

from __future__ import annotations

# ─── Scene Management Defaults (FR-SCN-001, FR-SCN-002) ──────────────

# Default preservation list — categories preserved during cleanup when request does not specify explicit preservation.
DEFAULT_PRESERVATION_LIST: tuple[str, ...] = (
    "camera",
    "light",
    "active_camera",
    "sole_camera",
    "protected",
)

# Default dry-run mode — whether cleanup defaults to preview-only mode.
DEFAULT_DRY_RUN_MODE: bool = False

# Include hidden objects in inspection — whether hidden objects are included by default.
DEFAULT_INCLUDE_HIDDEN_OBJECTS: bool = False

# Maximum inspection detail limit — limit for object detail returned during inspection.
MAX_INSPECTION_DETAIL_LIMIT: int = 1000

# Default cleanup timeout in seconds.
CLEANUP_TIMEOUT_SECONDS: float = 30.0

# Default inspection timeout in seconds.
INSPECTION_TIMEOUT_SECONDS: float = 15.0

# Cleanup confirmation required — whether destructive cleanup requires explicit confirmation when undo is unavailable.
CLEANUP_CONFIRMATION_REQUIRED: bool = True

# Default child handling policy — behavior for children of deleted objects.
DEFAULT_CHILD_HANDLING_POLICY: str = "detach"  # "delete", "detach", "reject"

# Default dependent handling policy — behavior for dependents such as constraints or references.
DEFAULT_DEPENDENT_HANDLING_POLICY: str = "reject"  # "ignore", "reject", "remove_safe"

# Protected object policy defaults.
PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA: bool = True
PROTECTED_OBJECT_POLICY_SOLE_CAMERA: bool = True
PROTECTED_OBJECT_POLICY_LIGHTS: bool = True
PROTECTED_OBJECT_POLICY_PROTECTED: bool = True
