"""MCP constants — tool names, default server values, envelope schema."""

DEFAULT_SERVER_NAME = "blender-arwaky"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080

TOOL_EXECUTE_COMMAND = "execute_command"
TOOL_LIST_COMMANDS = "list_commands"
TOOL_HELP = "help"
TOOL_HEALTH_CHECK = "health_check"

# Envelope schema keys
MCP_KEY_TRACKING_ID = "tracking_id"
MCP_KEY_TOOL = "tool"
MCP_KEY_SUCCESS = "success"
MCP_KEY_DATA = "data"
MCP_KEY_ERROR_CATEGORY = "error_category"
MCP_KEY_MESSAGE = "message"
MCP_KEY_WARNINGS = "warnings"
MCP_KEY_METADATA = "metadata"
MCP_KEY_PROTOCOL_VERSION = "protocol_version"
MCP_KEY_CATALOG_VERSION = "catalog_version"
MCP_KEY_VALUE = "value"
MCP_KEY_TRUNCATED = "truncated"
MCP_KEY_NOTE = "note"

# Envelope defaults
MCP_PROTOCOL_VERSION = "1.0"
MCP_CATALOG_VERSION_UNKNOWN = "unknown"
MCP_EXECUTION_FAILED_MESSAGE = "Execution failed"

# Validation messages
MCP_ACTION_REQUIRED_ERROR = "action is required"

# Truncation messages
MCP_TRUNCATION_NOTE_TEMPLATE = "Response exceeded {max_size} bytes"
MCP_RESPONSE_TRUNCATED_MESSAGE = "Response truncated due to size limit"
