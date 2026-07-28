"""Scene taxonomy constants.

Stable domain constants for scene inspection and cleanup.
"""

from typing import Final

# ─── Defaults ────────────────────────────────────────────────
DEFAULT_PRESERVATION_LIST: Final[tuple[str, ...]] = ("camera", "light")
DEFAULT_DRY_RUN_MODE: Final[bool] = False
DEFAULT_INCLUDE_HIDDEN_OBJECTS: Final[bool] = False
DEFAULT_CHILD_HANDLING_POLICY: Final[str] = "detach"
DEFAULT_DEPENDENT_HANDLING_POLICY: Final[str] = "reject"

# ─── Policy / limits ─────────────────────────────────────────
CLEANUP_CONFIRMATION_REQUIRED: Final[bool] = True
CLEANUP_TIMEOUT_SECONDS: Final[float] = 30.0
INSPECTION_TIMEOUT_SECONDS: Final[float] = 15.0
MAX_INSPECTION_DETAIL_LIMIT: Final[int] = 500

# ─── Protection policy defaults ──────────────────────────────
PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA: Final[bool] = True
PROTECTED_OBJECT_POLICY_SOLE_CAMERA: Final[bool] = True
PROTECTED_OBJECT_POLICY_LIGHTS: Final[bool] = True
PROTECTED_OBJECT_POLICY_PROTECTED: Final[bool] = True

# ─── Cleanup modes ───────────────────────────────────────────
CLEANUP_MODE_ALL: Final[str] = "all"
CLEANUP_MODE_OBJECTS: Final[str] = "objects"
CLEANUP_MODE_MESHES: Final[str] = "meshes"

VALID_CLEANUP_MODES: Final[frozenset[str]] = frozenset(
    (
        CLEANUP_MODE_ALL,
        CLEANUP_MODE_OBJECTS,
        CLEANUP_MODE_MESHES,
    )
)

# ─── Child handling policies ─────────────────────────────────
CHILD_POLICY_DELETE: Final[str] = "delete"
CHILD_POLICY_DETACH: Final[str] = "detach"
CHILD_POLICY_REJECT: Final[str] = "reject"

VALID_CHILD_HANDLING_POLICIES: Final[frozenset[str]] = frozenset(
    (
        CHILD_POLICY_DELETE,
        CHILD_POLICY_DETACH,
        CHILD_POLICY_REJECT,
    )
)

# ─── Dependent handling policies ─────────────────────────────
DEPENDENT_POLICY_IGNORE: Final[str] = "ignore"
DEPENDENT_POLICY_REJECT: Final[str] = "reject"
DEPENDENT_POLICY_REMOVE_SAFE: Final[str] = "remove_safe"

VALID_DEPENDENT_HANDLING_POLICIES: Final[frozenset[str]] = frozenset(
    (
        DEPENDENT_POLICY_IGNORE,
        DEPENDENT_POLICY_REJECT,
        DEPENDENT_POLICY_REMOVE_SAFE,
    )
)

# ─── Inspection detail levels ────────────────────────────────
DETAIL_LEVEL_MINIMAL: Final[str] = "minimal"
DETAIL_LEVEL_STANDARD: Final[str] = "standard"
DETAIL_LEVEL_DETAILED: Final[str] = "detailed"
DETAIL_LEVEL_SUMMARY: Final[str] = "summary"

VALID_DETAIL_LEVELS: Final[frozenset[str]] = frozenset(
    (
        DETAIL_LEVEL_MINIMAL,
        DETAIL_LEVEL_STANDARD,
        DETAIL_LEVEL_DETAILED,
        DETAIL_LEVEL_SUMMARY,
    )
)

# ─── Preservation tokens ─────────────────────────────────────
PRESERVATION_CAMERA: Final[str] = "camera"
PRESERVATION_LIGHT: Final[str] = "light"

# ─── Blender object types ────────────────────────────────────
OBJECT_TYPE_CAMERA: Final[str] = "CAMERA"
OBJECT_TYPE_LIGHT: Final[str] = "LIGHT"
OBJECT_TYPE_MESH: Final[str] = "MESH"