"""Server domain — Compile-time constant defaults from FRD specification.

All values follow binary notation (1k = 1024 bytes).
"""

# ============================================================
# Connection Defaults
# ============================================================

DEFAULT_HOST: str = "localhost"
DEFAULT_PORT: int = 9876
CONNECTION_TIMEOUT_SECONDS: float = 30.0
HEARTBEAT_INTERVAL_SECONDS: int = 10
HEARTBEAT_FAILURE_THRESHOLD: int = 3
MAX_RECONNECT_ATTEMPTS: int = 3
RETRY_BASE_DELAY_SECONDS: float = 1.0
RETRY_MAX_DELAY_SECONDS: float = 4.0

# ============================================================
# Execution Defaults
# ============================================================

DEFAULT_EXECUTION_TIMEOUT_MS: float = 30_000.0  # 30 seconds
DEFAULT_COMMAND_TIMEOUT_MS: float = 5_000.0     # 5 seconds
MAX_CODE_PAYLOAD_BYTES: int = 1_048_576          # 1 MB (1k = 1024)

# ============================================================
# Queue Defaults
# ============================================================

QUEUE_MAX_DEPTH: int = 50
DEFAULT_QUEUE_WAIT_TIMEOUT_MS: float = 10_000.0  # 10 seconds target

# ============================================================
# Task Defaults
# ============================================================

DEFAULT_TASK_RETENTION_SECONDS: float = 600.0    # 10 minutes

# ============================================================
# Transport Types
# ============================================================

TRANSPORT_SOCKET: str = "socket"
TRANSPORT_STDIO: str = "stdio"
