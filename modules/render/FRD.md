# FRD — Rendering and Viewport Feature

## System Overview

The rendering and viewport feature enables users and AI clients to capture visual representations of the 3D scene. It provides capabilities for taking viewport screenshots, rendering high-quality scene images, configuring cameras, and setting up HDRI (High Dynamic Range Image) environment lighting.

Because the 3D application can only safely process one scene-modifying operation at a time, this feature ensures that all concurrent requests are handled sequentially to maintain application stability. It also enforces strict safety checks for file outputs, ensuring that rendered images are only written to explicitly allowed directories, and handles long-running render tasks gracefully without freezing the application.

## Functional Requirements

### FR-RND-001: Capture Viewport Screenshot

- **Use Case:** A user or AI client needs to quickly capture the current state of the 3D viewport as an image for preview or inspection purposes.
- **User Action:** Request a viewport screenshot, specifying the maximum image size, view angle, shading mode, overlay visibility, focus object, and image format.
- **System Response:** Capture the viewport and return the image data (either as a direct payload or a file reference if the image is too large), along with capture metadata.
- **Business Rules:**
  - Supported view angles: perspective, orthographic, active camera view.
  - Supported shading modes: wireframe, solid, material preview, rendered.
  - Overlay visibility (grid, gizmos, stats) must be configurable.
  - The maximum image size must be strictly enforced while preserving the aspect ratio.
  - The image format must be supported by the 3D application and allowed by system settings.
  - If a focus object is specified, the system must resolve it deterministically. If not found, the system must either return an error or ignore the focus and continue, based on configuration.
  - If the active viewport is unavailable (e.g., in headless mode), the system must fall back to an offscreen or active camera capture if supported.
  - The operation is strictly read-only and must not permanently mutate the scene state (temporary view adjustments for capture are allowed).
  - If the resulting image payload exceeds safe transport limits, the system must return a file reference instead of raw data.
- **Edge Cases:** Empty viewport, focused object not found, unsupported image format, oversized viewport, no active 3D view context, headless runtime limitations, hidden focus object, locked view, memory limits.
- **Error Handling:** Return `ValidationError` for invalid parameters; return `SceneStateError` for missing focus objects (when strict policy is enabled); return `TimeoutError` if capture takes too long; return `ExecutionError` for general rendering failures.

### FR-RND-002: Render Scene Image

- **Use Case:** A user or AI client needs to generate a high-quality, final rendered image of the 3D scene and save it to disk.
- **User Action:** Request a scene render, specifying the output file path, resolution, sample count, denoising preferences, render engine, color mode, transparency, target camera, and overwrite rules.
- **System Response:** Execute the render and return the final file path, render statistics (time, samples, engine used), and success status.
- **Business Rules:**
  - The output destination must be writable and located strictly inside allowed output directories.
  - Resolution and sample count must be within configured minimum and maximum bounds (e.g., 1 to 8192 for resolution).
  - Denoising is optional and must gracefully degrade if the selected render engine does not support it.
  - The target camera must exist. If no active camera exists, the system may automatically set up a camera if policy allows.
  - Overwrite policy for existing files: overwrite, reject, or create a unique variant (e.g., appending a number).
  - The system must write to a temporary file first and only finalize/move it to the target destination after a successful render to prevent corrupted partial files.
  - For long-running renders, the system must support background task submission, returning a task ID for progress polling.
  - Cancelling a running render is a best-effort operation.
  - The output file path returned must not expose sensitive filesystem information beyond the allowed directory.
- **Edge Cases:** Invalid output destination, permission denied, output directory missing, render timeout, denoising unsupported, no active camera, empty scene, unsupported render engine, out of memory, existing file conflict, very high resolution, transparent background unsupported.
- **Error Handling:** Return `ValidationError` for invalid render parameters; return `SceneStateError` for missing cameras or invalid scene states; return `TimeoutError` for exceeded render duration; return `ExecutionError` for general render failures.

### FR-RND-003: Configure Camera

- **Use Case:** A user or AI client needs to position, orient, and configure the properties of a camera used for rendering or viewport navigation.
- **User Action:** Request camera setup, providing the target camera reference (or creation rules), position, rotation, lens/focal length, depth of field options, and framing target.
- **System Response:** Configure the camera and return the resolved camera reference, final settings, and active camera status.
- **Business Rules:**
  - If the camera does not exist, it must be created if the creation policy allows it.
  - If multiple cameras exist, resolution must be deterministic: prefer explicit reference > fall back to active scene camera > fall back to first available camera.
  - If no camera exists and creation is disallowed, return an error.
  - Lens/focal length values must be within valid configured ranges.
  - Position and rotation values must be finite and valid 3D vectors.
  - The camera may be set as the active scene camera if requested.
  - Locked or protected camera states must be respected unless an explicit override is allowed.
  - The operation must not modify shared or linked camera data unless explicitly allowed.
  - If a framing target is provided, the system should adjust the camera orientation to frame the target while preserving the requested lens settings.
- **Edge Cases:** Multiple cameras, locked camera, invalid lens values, non-finite transform values, missing camera reference, linked camera data, protected camera, camera constraints overriding transform, no scene camera.
- **Error Handling:** Return `SceneStateError` for invalid camera states or missing cameras when creation is disallowed; return `ValidationError` for invalid parameters; return `ProtectionError` when a locked camera cannot be modified; return `ExecutionError` for general failures.

### FR-RND-004: Configure HDRI Lighting

- **Use Case:** A user or AI client needs to set up realistic environment lighting using an HDRI (High Dynamic Range Image) asset.
- **User Action:** Request HDRI setup, providing the asset reference, lighting strength, rotation, background visibility rules, and environment overwrite policy.
- **System Response:** Apply the environment lighting and return the resolved environment reference, applied strength, rotation, and success status.
- **Business Rules:**
  - The HDRI asset must be available locally before environment setup. If not, the system must trigger the asset download/resolution process.
  - HDRI strength must be within valid ranges (e.g., 0.0 to 10.0).
  - HDRI rotation must be normalized according to the configured angle convention.
  - Overwrite policy for existing environments: replace entirely, update existing, or reject if one exists.
  - The setup must apply to the scene's world/environment lighting system.
  - If the scene world does not exist, the system must create one if policy allows.
  - Background visibility policy must control whether the HDRI appears as the visible background or only contributes to lighting.
  - The operation must preserve non-environment lighting objects (like standard point lights) unless explicitly replaced.
- **Edge Cases:** HDRI asset not found, download failed, unsupported HDRI format, existing environment conflict, strength out of range, rotation overflow, missing scene world, linked world data.
- **Error Handling:** Return `AssetNotFoundError` if the asset cannot be resolved/downloaded; return `ValidationError` for invalid strength/rotation; return `SceneStateError` for incompatible scene environment states; return `ExecutionError` for general failures.

## System Capabilities (User-Facing Operations)


| Operation            | User Action (Input)                                      | System Response (Output)         | Description                               |
| ---------------------- | ---------------------------------------------------------- | ---------------------------------- | ------------------------------------------- |
| `capture_screenshot` | View angle, shading mode, overlays, focus object, format | Screenshot Result (payload/ref)  | Capture current viewport as an image      |
| `render_scene`       | Output path, resolution, samples, engine, camera, policy | Render Result (file path, stats) | Render full scene to a high-quality image |
| `configure_camera`   | Camera ref/create, position, rotation, lens, framing     | Camera Config Result             | Position and configure a scene camera     |
| `configure_hdri`     | Asset ref, strength, rotation, visibility, overwrite     | Environment Result               | Set up HDRI-based environment lighting    |

**Additional Capability Behaviors:**

- All operations return a structured result containing a success indicator, a human-readable message, and an error category if failed.
- All operations accept a unique tracking identifier for tracing and troubleshooting.
- Operations that modify the 3D scene (like configuring cameras or HDRI) are processed sequentially to maintain application stability.
- Long-running operations (like `render_scene`) automatically transition to background task execution when expected to exceed standard timeout limits.
- Screenshot operations may return raw image data or a file reference depending on size limits and transport constraints.

## System Boundaries

- **External Consumers:**
  - AI Clients and User Interfaces that request viewport captures, renders, or camera/environment setups.
- **Target Environment:**
  - The 3D Application (must be running, with its rendering and viewport systems accessible).
  - Local Filesystem: For writing rendered images and reading local HDRI assets.
- **External Dependencies:**
  - Asset Acquisition Capability: For downloading or resolving HDRI assets if they are not already present locally.

## Non-functional Requirements

- **Performance:**
  - Viewport screenshot capture must complete within 3 seconds for standard settings.
  - Scene rendering must complete within 60 seconds for standard scenes under default resolution/sample settings.
  - Long-running renders must automatically utilize background task execution to prevent blocking the user interface.
- **Reliability:**
  - The system must gracefully handle render failures without leaving corrupted partial files (using temporary file strategies).
  - Missing camera or environment states must be resolved deterministically or fail with clear error categories.
  - Background task failures must preserve the final error state for accurate polling.
- **Safety:**
  - Output destinations for renders must be strictly restricted to allowed directories.
  - Overwrite behavior for files and environments must be explicit and controlled by policy.
  - Camera and environment setups must respect locked or protected states unless an override is explicitly allowed.
- **Stability:**
  - Operations that modify the 3D scene are processed one at a time to prevent application instability.
- **Observability:**
  - The system must log operation types, target references, result statuses, and durations.
  - Render metadata (resolution, samples, engine) and screenshot metadata (format, dimensions) must be logged without exposing sensitive file paths.
  - The system must never log raw image payloads or sensitive asset credentials.
- **Portability:**
  - Behavior must remain consistent across supported versions of the 3D application.
  - Headless runtime limitations (e.g., no active viewport) must be detected and handled gracefully via fallbacks.

## Test Scenarios / QA Checklist

**Viewport Screenshots:**

- [ ]  Screenshot with valid parameters returns image payload or file reference.
- [ ]  Screenshot with invalid view angle/shading mode/format returns `ValidationError`.
- [ ]  Screenshot with missing focus object follows the configured policy (error or ignore).
- [ ]  Screenshot with maximum size limit preserves aspect ratio correctly.
- [ ]  Screenshot falls back gracefully when active viewport context is unavailable (headless mode).

**Scene Rendering:**

- [ ]  Render with valid parameters produces the final output artifact.
- [ ]  Render with invalid output destination or permission denied returns `ValidationError` or `ExecutionError`.
- [ ]  Render with resolution/samples outside allowed range returns `ValidationError`.
- [ ]  Render with missing active camera returns `SceneStateError` or triggers camera setup if allowed.
- [ ]  Render with unsupported denoising degrades gracefully without failing.
- [ ]  Render with existing file follows the overwrite policy (overwrite, reject, or unique variant).
- [ ]  Render timeout returns `TimeoutError`.
- [ ]  Long-running render submits as a background task and returns a task ID.
- [ ]  Background render polling returns progress and final result.

**Camera Configuration:**

- [ ]  Camera setup creates a camera if none exists and creation policy allows.
- [ ]  Camera setup uses the active camera when no explicit reference is provided.
- [ ]  Camera setup resolves multiple cameras deterministically.
- [ ]  Camera setup with invalid lens values returns `ValidationError`.
- [ ]  Camera setup with locked camera returns `ProtectionError` unless override is allowed.
- [ ]  Camera setup sets the camera as active when requested.

**HDRI Lighting:**

- [ ]  HDRI setup applies environment lighting when the asset is available locally.
- [ ]  HDRI setup triggers asset download when the asset is unavailable locally.
- [ ]  HDRI setup with missing/unresolvable asset returns `AssetNotFoundError`.
- [ ]  HDRI setup with strength outside valid range returns `ValidationError`.
- [ ]  HDRI setup with rotation overflow normalizes the value correctly.
- [ ]  HDRI setup follows the environment overwrite policy.
- [ ]  HDRI setup creates the scene world when missing and policy allows.

**General Stability:**

- [ ]  Concurrent rendering and viewport operations are processed sequentially without causing instability.
- [ ]  System execution failures are caught and returned as `ExecutionError` without crashing the application.

## Assumptions & Constraints

- The 3D application must be running for viewport and render operations.
- HDRI assets must be available locally before environment setup (internet connection is only required for the initial download).
- Viewport capture may depend on active viewport context and requires fallback mechanisms in headless environments.
- Render operations can be long-running and must utilize background task execution when appropriate.
- Operations that modify the scene must be processed one at a time to maintain application stability.
- Output artifacts (rendered images) must be written only to explicitly allowed output locations.
- Some render features (like specific denoising algorithms) depend on the active render engine's capabilities.
- Camera and environment setup may affect existing scene state and must strictly follow explicit overwrite/preservation policies.

## Glossary

- **HDRI (High Dynamic Range Image):** An image format used to provide realistic, 360-degree environment lighting to a 3D scene.
- **Viewport:** The interactive 3D viewing area within the application interface.
- **Shading Mode:** The visual display mode of the viewport (e.g., wireframe, solid, material preview, rendered).
- **Render Artifact:** The final output image file produced by the rendering process.
- **Active Camera:** The specific camera currently designated by the scene to be used for final rendering.
- **Environment Lighting:** Scene-wide illumination provided by the background/world environment rather than discrete light objects.
- **Background Task:** A long-running operation submitted to the system that returns a tracking ID immediately, allowing the user to check its status later.
- **Allowed Output Location:** A specifically configured directory where the system is permitted to write rendered image files.
- **Overwrite Policy:** The rule defining how the system handles existing files or existing environment setups when a new request conflicts with them.
