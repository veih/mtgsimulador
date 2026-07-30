---
kind: dependency_management
name: No External Dependency Management — Pure Python Stdlib Project
category: dependency_management
scope:
    - '**'
source_files:
    - simuladorMtg/main.py
    - simuladorMtg/src/__init__.py
    - simuladorMtg/decks/__init__.py
---

This repository contains a Python-based Magic: The Gathering match simulator that relies exclusively on the Python standard library. There is no dependency management system in place because the project does not use any third-party packages.

**What system/approach is used:**
- No package manager (no pip, poetry, pipenv, conda, etc.)
- No dependency manifest files (no requirements.txt, pyproject.toml, setup.py, Pipfile, etc.)
- No vendoring or lockfiles
- All imports are from Python's standard library modules only: `sys`, `os`, `argparse`, `random`, `datetime`, `dataclasses`, `enum`, `typing`

**Key observations:**
- The codebase is self-contained with all logic implemented in local modules under `src/` and `decks/`
- Dependencies are managed purely through Python's import system within the project structure
- The main entry point (`main.py`) adds its own directory to `sys.path` to enable relative imports between project modules
- Internal module organization uses Python packages (`__init__.py` files) for clean separation between core engine (`src/`) and deck definitions (`decks/`)

**Architecture and conventions:**
- Pure Python stdlib approach eliminates external dependency risks
- Simple flat package structure with clear separation of concerns
- No version pinning or dependency resolution needed since there are no external dependencies
- The project can be run directly with `python main.py` without any installation or environment setup beyond a Python interpreter

**Conventions and constraints:**
- All functionality must be achievable using only Python standard library modules
- No third-party libraries are imported anywhere in the codebase
- This approach ensures maximum portability but limits available functionality to what the standard library provides