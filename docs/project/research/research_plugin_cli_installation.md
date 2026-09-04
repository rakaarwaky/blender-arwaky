# Plugin CLI Installation Findings

Date: 2026-08-15

## Official Blender sources

- Extension creation and command-line validation: https://docs.blender.org/manual/en/latest/advanced/extensions/getting_started.html
- Extension command-line arguments: https://docs.blender.org/manual/en/latest/advanced/command_line/extension_arguments.html

## Relevant findings

1. Blender extensions are distributed as ZIP packages with a manifest and add-on files.
2. The official extension workflow provides command-line build and validation commands.
3. Blender's extension CLI includes install-file support in current Blender documentation, but the available Blender version must be checked before invoking it.
4. A provider manager must not assume that every Blender version supports the same extension CLI. It must perform capability/version detection and return an explicit unsupported result when the command is unavailable.
5. Downloaded packages must be verified before installation. At minimum the registry entry should provide a HTTPS source, expected SHA-256, plugin id, plugin version, and supported Blender range.
6. Installation must use a controlled cache and temporary directory, reject path traversal and malformed packages, and avoid executing downloaded Python directly from the Arwaky process.
7. Installation and removal are destructive or environment-changing operations and need explicit CLI confirmation. The operation should invoke a controlled Blender process or an existing Blender runtime boundary rather than import arbitrary downloaded code into the Arwaky Python process.
8. MPFB2 is distributed through the Blender Extensions platform and supports Blender 4.2+, but current command-line extension management documentation targets newer Blender versions. MPFB2 installation therefore needs a version-aware strategy rather than assuming `blender --command extension install-file` works on every supported Blender version.
