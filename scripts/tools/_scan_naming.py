import os

LAYERS_STRICT = {
    'root': ['entry', 'container'],
    'taxonomy': ['vo', 'entity', 'error', 'event', 'constant'],
    'contract': ['protocol', 'aggregate'],
    'agent': ['orchestrator'],
    'surface': ['command', 'controller', 'page', 'view', 'component', 'router', 'layout', 'hook', 'store', 'action', 'screen'],
}

LAYERS_FLEXIBLE = {
    'capabilities': {'forbidden': ['vo', 'entity', 'error', 'event', 'constant', 'constants', 'protocol', 'aggregate', 'utility']},
    'utility': {'forbidden': ['vo', 'entity', 'error', 'event', 'constant', 'protocol', 'aggregate']},
}

EXCEPTIONS = {'__init__.py', '__main__.py', 'main.py', 'py.typed', 'pyproject.toml', 'lib.py'}
AES101_EXCEPTIONS = EXCEPTIONS | {'main.rs', 'lib.rs', 'mod.rs', 'index.ts', 'index.js'}

v101 = []
v102 = []

modules_dir = '/home/raka/mcp-arwaky/blender-arwaky/modules'
for root, _dirs, files in os.walk(modules_dir):
    parts_root = root.split(os.sep)
    if 'tests' in parts_root or '__pycache__' in parts_root or '.venv' in parts_root:
        continue
    for f in files:
        if not (f.endswith('.py') or f.endswith('.rs')):
            continue
        if f in AES101_EXCEPTIONS:
            continue
        name = f.replace('.py', '').replace('.rs', '')
        parts = name.split('_')

        # AES101: min 3 words (prefix + concept + suffix)
        if len(parts) < 3:
            v101.append((root, f, f'only {len(parts)} words'))

        # Detect layer by prefix
        prefixes = ['capabilities', 'agent', 'surface', 'taxonomy', 'contract', 'root', 'utility']
        found_prefix = None
        for p in prefixes:
            if name.startswith(p + '_'):
                found_prefix = p
                break

        if not found_prefix:
            # No layer prefix — possible AES101 but not AES102
            continue

        suffix = parts[-1]

        if found_prefix in LAYERS_STRICT:
            allowed = LAYERS_STRICT[found_prefix]
            if suffix not in allowed:
                v102.append((root, f, f'{found_prefix} strict: "{suffix}" not in {allowed}'))
        elif found_prefix in LAYERS_FLEXIBLE:
            forbidden = LAYERS_FLEXIBLE[found_prefix]['forbidden']
            if suffix in forbidden:
                v102.append((root, f, f'{found_prefix} flexible: "{suffix}" is forbidden'))

print('=== AES101 (< 3 words) ===')
for r, f, msg in sorted(v101):
    rel = os.path.relpath(os.path.join(r, f), modules_dir)
    print(f'  {rel}: {msg}')

print('\n=== AES102 (suffix violation) ===')
for r, f, msg in sorted(v102):
    rel = os.path.relpath(os.path.join(r, f), modules_dir)
    print(f'  {rel}: {msg}')

print(f'\nTotal: {len(v101)} AES101 + {len(v102)} AES102')
