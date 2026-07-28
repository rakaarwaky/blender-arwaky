# ARWAKY LOOP QUESTIONS

## Status OPEN

### question

**Cycle 46 (Linter AES201 Detection)** : False positive detection on `surface_cli_command.py` importing from `agent_` prefix files in `shared/src/common/`. The linter uses prefix-based detection rather than path-based layer detection.

### answer

**Cycle 46 (Linter AES201 Detection)** : its not fasle psotiive its true vioaltion surface shoud import from utitltiy taxonomy contract agregate only read RULES AES

### question

 **Cycle 87 (AES504 Shared Utility)** : Linter reports AES504 on `shared/src/gateway/utility/utility_config_loader.py` even after adding barrel exports. This is a pure utility function (`load_server_config`), not an agent orchestrator. Should I suppress AES504 for shared/ foundation files, or does the linter rule need configuration adjustment?

### answer

 **Cycle 87 (AES504 Shared Utility)** : Already fix linter to detect cross vioaltion 