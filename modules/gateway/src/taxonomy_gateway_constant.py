"""Gateway feature — Compile-time constant defaults.

All values follow binary notation (1k = 1024 bytes).
"""

# ============================================================
# Transport
# ============================================================

DEFAULT_MAX_PAYLOAD_BYTES: int = 10_485_760  # 10 MB (10 * 1024 * 1024)

# ============================================================
# Queue
# ============================================================

DEFAULT_MAX_DEPTH: int = 50

# ============================================================
# Code Execution
# ============================================================

DEFAULT_MAX_OUTPUT_BYTES: int = 1_048_576  # 1 MB (1024 * 1024)
DEFAULT_EXECUTION_TIMEOUT_SECONDS: float = 30.0

# ============================================================
# Scene Queue
# ============================================================

DEFAULT_SCENE_QUEUE_WAIT_TIMEOUT: float = 30.0

# ============================================================
# Maintenance
# ============================================================

DEFAULT_MAINTENANCE_MAX_RETRIES: int = 3
DEFAULT_MAINTENANCE_BASE_BACKOFF: float = 1.0
DEFAULT_MAINTENANCE_MAX_BACKOFF: float = 16.0
