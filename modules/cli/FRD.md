 FRD — Command-Line Interface Feature

## System Overview

The command-line interface (CLI) is the foundational execution engine for the system. It provides direct, manual control over the 3D application's lifecycle (locating, launching, monitoring, and shutting down) as well as the direct execution of 3D scene operations.

The AI integration layer operates strictly as a 1:1 transparent extension of this command-line interface. This means any 3D action or lifecycle command an AI client can perform is executed exactly as if the user typed it directly in the terminal. The CLI ensures that the application is correctly configured, running, and ready to accept commands, while safely handling crashes, unresponsive states, and persistent configuration across different sessions.

## Functional Requirements

### FR-CLI-001: Locate and Register Application

- **Use Case:** A user needs to tell the system where the 3D application is installed on their computer so that subsequent commands know which application to control.
- **User Action:** Run the initialization command, optionally providing a custom file path to the application.
- **System Response:** Verify the application exists at the specified (or auto-detected) path, validate it is the correct software, and remember this location for future commands.
- **Business Rules:**
  - If no path is provided, the system must automatically search standard installation directories and system paths to find the application.
  - The system must validate that the located file is actually a valid executable for the target 3D software.
  - The configured path must be remembered persistently so the user does not have to specify it every time they open a new terminal session.
  - If multiple versions are found during auto-detection, the system must select the most recent compatible version or prompt the user to specify.
- **Edge Cases:** Application is not installed, the provided path is incorrect or points to a non-executable file, multiple incompatible versions are found, system permissions prevent reading the directory.
- **Error Handling:** Return a clear `ApplicationNotFoundError` if the software cannot be located or the provided path is invalid.

### FR-CLI-002: Launch Application

- **Use Case:** A user needs to start the 3D application with the required integration components automatically enabled and ready to accept commands.
- **User Action:** Run the launch command, optionally providing extra startup arguments.
- **System Response:** Start the application, ensure the integration components are active, and wait until the application is fully initialized and ready.
- **Business Rules:**
  - The system must automatically inject the necessary arguments to enable the integration components upon startup.
  - The system must wait for the application to signal that it is fully ready and listening for commands before returning control to the user.
  - If an instance is already running and managed by the system, the command must warn the user and refuse to launch a duplicate instance.
  - The system must detect if the required communication channel is blocked by another application and report the conflict.
- **Edge Cases:** Application is already running, the required communication channel is in use, the integration components fail to load, application crashes immediately upon startup.
- **Error Handling:** Return `ApplicationAlreadyRunningError` if an instance exists; return `LaunchFailureError` if the application crashes or components fail to load; return `ChannelConflictError` if the communication channel is blocked.

### FR-CLI-003: Shut Down Application

- **Use Case:** A user needs to stop the running 3D application cleanly without losing unsaved data or corrupting the environment.
- **User Action:** Run the shutdown command.
- **System Response:** Send a graceful exit signal to the application, wait for it to close, and update the system's memory to reflect that it is no longer running.
- **Business Rules:**
  - The system must always attempt a graceful shutdown first, allowing the application to close normally.
  - If the application is unresponsive and does not close within a reasonable timeframe, the system must forcefully terminate it as a fallback.
  - Once the application is closed, the system must clear its internal record of the running state.
  - The command must succeed silently if the application is already closed.
- **Edge Cases:** Application is already closed, application is frozen/unresponsive and ignores the graceful shutdown signal, system permissions prevent terminating the process.
- **Error Handling:** Return `ShutdownFailureError` only if the application cannot be stopped even after force-termination attempts.

### FR-CLI-004: Check Application Status

- **Use Case:** A user needs to verify if the 3D application is currently running, healthy, and ready to accept commands.
- **User Action:** Run the status command.
- **System Response:** Display the current operational state of the application, including whether it is running, its system process identifier, the active communication channel, and how long it has been running.
- **Business Rules:**
  - The system must verify that the application is *actually* running (not just relying on a stale record from a previous session).
  - The system must verify that the communication channel to the application is active and responsive.
  - If the application crashed in the background, the system must detect this and report it as "Stopped" or "Unhealthy" rather than "Running".
- **Edge Cases:** Application crashed in the background without notifying the system, the system's memory contains stale data from a previous session, the communication channel is open but the application is frozen.
- **Error Handling:** Return a clear "Not Running" or "Unhealthy" status message instead of throwing a fatal error.

### FR-CLI-005: Execute 3D Scene Actions

- **Use Case:** A user needs to perform a specific 3D operation (e.g., create an object, render a scene, clean up the scene) directly from the terminal.
- **User Action:** Run the execute command, providing the action name and structured parameters.
- **System Response:** Validate the parameters, execute the action in the 3D application, and print the structured result or error to the terminal.
- **Business Rules:**
  - The system must support the full catalog of available 3D actions.
  - The system must validate the provided parameters against the action's defined rules before execution.
  - All actions must be processed sequentially to maintain the stability of the 3D application.
  - The system must handle execution timeouts gracefully, printing a clear timeout error rather than hanging indefinitely.
  - This exact execution path is what the AI integration layer uses when it receives an AI request (1:1 parity).
- **Edge Cases:** Unknown action name, invalid or missing parameters, 3D application disconnected during execution, execution exceeds timeout limit.
- **Error Handling:** Print a structured error response with a descriptive message and specific error category (e.g., `ValidationError`, `TimeoutError`, `ExecutionError`).

### FR-CLI-006: Discover and Inspect Capabilities

- **Use Case:** A user needs to see what 3D actions are available, how to format the requests, and what the current system configuration is.
- **User Action:** Run the list or config commands.
- **System Response:** Print the complete catalog of available actions (with schemas and descriptions) or print the currently active system settings.
- **Business Rules:**
  - The list command must return a comprehensive, up-to-date list of all supported 3D actions, formatted for easy reading in the terminal.
  - The config command must return the active system settings, boundaries, and allowed directories.
  - Sensitive values (like authentication tokens) must be masked in the config output.
- **Edge Cases:** Action catalog fails to load, configuration file is missing or corrupted.
- **Error Handling:** Print a clear error message explaining why the catalog or configuration is unavailable.

### FR-CLI-007: Remember Configuration and State

- **Use Case:** The system needs to persistently remember the user's configured application path and the current running state across different terminal sessions and command invocations.
- **User Action:** (Implicit) The user runs commands in separate terminal sessions over time.
- **System Response:** Safely store and retrieve the application path and running state so the user doesn't have to reconfigure or relaunch unnecessarily.
- **Business Rules:**
  - The configured path and running state must be saved securely to the local file system.
  - If multiple terminal commands are run simultaneously, the state must remain consistent and not become corrupted.
  - If the saved state file is corrupted, missing, or unreadable, the system must fall back to safe defaults (e.g., assuming the app is not running) without crashing.
  - The system must never expose sensitive system paths or internal states in plain text if not required for user visibility.
- **Edge Cases:** Local storage is full, the state file is corrupted by an external process, simultaneous command executions attempt to update the state at the exact same millisecond.
- **Error Handling:** Log warnings for storage issues but allow commands to proceed with in-memory defaults. Never crash the CLI due to state persistence failures.

## System Capabilities (User-Facing Operations)


| Command   | User Action (Input)              | System Response (Output)       | Description                                  |
| ----------- | ---------------------------------- | -------------------------------- | ---------------------------------------------- |
| `init`    | Optional custom file path        | Success / Error Message        | Locate and remember the 3D app path          |
| `run`     | Optional extra startup arguments | Success / Error Message        | Launch 3D app with integration enabled       |
| `close`   | —                               | Success / Error Message        | Gracefully terminate the 3D app process      |
| `status`  | —                               | Status Report (State, Channel) | Check if 3D app is running and healthy       |
| `execute` | Action Name, Parameters          | Execution Result / Error       | Run a 3D scene action (1:1 AI parity)        |
| `list`    | —                               | Command Catalog                | Print available 3D actions and schemas       |
| `config`  | —                               | Active Configuration           | Print current system settings and boundaries |

**Additional Capability Behaviors:**

- All commands must provide clear, human-readable feedback in the terminal.
- All commands must complete and return control to the user within 5 seconds under normal conditions (excluding long-running 3D actions like rendering).
- Commands must not execute arbitrary code; they are strictly limited to predefined lifecycle and 3D actions.
- The `execute`, `list`, and `config` commands form the exact foundation that the AI integration layer wraps 1:1.

## System Boundaries

- **External Consumers:**
  - Users interacting via the terminal/command-line interface.
  - The AI Integration Layer (which invokes these exact same capabilities programmatically).
- **Target Environment:**
  - Local Operating System (for process management and file system access).
  - 3D Application (the target process being managed and controlled).

## Non-functional Requirements

- **Performance:**
  - Lifecycle commands (`init`, `run`, `close`, `status`, `list`, `config`) must respond and return control to the user within 5 seconds.
  - 3D execution commands (`execute`) must respect the specific timeout limits of the underlying 3D operations.
- **Reliability:**
  - The CLI must gracefully handle situations where the 3D application crashes in the background, updating its state accordingly without hanging.
  - Sequential execution of 3D commands must be strictly enforced to prevent 3D application instability.
- **Security:**
  - The CLI must not allow arbitrary code execution.
  - The CLI must only interact with the specific 3D executable that was validated during the `init` phase.
  - Sensitive configuration values must be masked in terminal output.
- **Usability:**
  - Error messages must be actionable, clearly explaining what went wrong and how the user can fix it.

## Test Scenarios / QA Checklist

**Initialization & Configuration:**

- [ ]  `init` with a valid custom path successfully registers the 3D app.
- [ ]  `init` without a path successfully auto-detects the 3D app.
- [ ]  `init` with a missing or invalid path returns `ApplicationNotFoundError`.
- [ ]  Configuration persists across separate terminal sessions.
- [ ]  `config` prints active settings and masks sensitive tokens.

**Launching & Status:**

- [ ]  `run` starts the 3D app successfully and waits until it is ready.
- [ ]  `run` with the app already running returns `ApplicationAlreadyRunningError`.
- [ ]  `run` with a blocked communication channel returns `ChannelConflictError`.
- [ ]  `status` correctly reports a running process with accurate details.
- [ ]  `status` correctly reports "Not Running" if the app was closed manually.
- [ ]  `status` correctly reports "Unhealthy" if the app crashed in the background.

**3D Execution & Discovery (1:1 AI Parity):**

- [ ]  `execute` with a valid action and parameters returns a successful result.
- [ ]  `execute` with an unknown action returns a descriptive error.
- [ ]  `execute` with invalid parameters returns a validation error.
- [ ]  `execute` processes commands strictly sequentially, blocking the next command until the current one finishes.
- [ ]  `list` prints the full, correctly formatted command catalog.

**Shutdown & Reliability:**

- [ ]  `close` gracefully terminates a running 3D app instance.
- [ ]  `close` successfully force-terminates a frozen 3D app instance.
- [ ]  `close` succeeds silently if the app is already closed.
- [ ]  CLI commands do not crash or hang if the internal state file is corrupted.

## Assumptions & Constraints

- The 3D application (e.g., Blender 3.0+) must be installed on the user's machine.
- The default communication channel must be available on the local machine.
- The CLI operates as the core execution engine; the AI integration layer relies entirely on the CLI's capabilities and does not introduce independent 3D processing logic.
- All 3D operations must be processed sequentially to maintain application stability.

## Glossary

- **Command-Line Interface (CLI):** A text-based interface used to interact with the software by typing commands.
- **Integration Components:** The internal add-ons or scripts within the 3D application that allow it to receive and execute external commands.
- **Graceful Shutdown:** The process of asking an application to close normally, allowing it to save state and release resources, as opposed to a force-kill.
- **Stale State:** A situation where the system's memory indicates an application is running, but the application has actually crashed or been closed externally.
- **1:1 Parity:** The guarantee that an action executed via the AI integration layer has the exact same behavior, priority, and constraints as if it were executed directly via the CLI.
