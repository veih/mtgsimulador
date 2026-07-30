---
kind: build_system
name: No Build System — Pure Python Script Project
category: build_system
scope:
    - '**'
source_files:
    - simuladorMtg/main.py
    - simuladorMtg/test_game.py
---

This repository does not contain a build system. It is a pure Python project with no build scripts, package manifests, CI configuration, containerization, or automated testing infrastructure. The project consists of a single entry point (`simuladorMtg/main.py`) and a small set of Python modules under `simuladorMtg/src/` and `simuladorMtg/decks/`. There are no Makefiles, Dockerfiles, setup.py, pyproject.toml, requirements.txt, tox.ini, or any CI/CD pipeline files. Execution is done directly via the Python interpreter: `python main.py`, with optional CLI arguments for deck selection, match count, and seeding. A standalone test script (`test_game.py`) exercises core game logic but is not integrated into any test runner. Dependencies are imported from the standard library only (argparse, random, datetime, sys, os), so no dependency resolution or virtual environment management is required.