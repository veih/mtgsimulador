---
kind: configuration_system
name: No Centralized Configuration System
category: configuration_system
scope:
    - '**'
source_files:
    - simuladorMtg/main.py
    - simuladorMtg/decks/__init__.py
    - simuladorMtg/src/simulator.py
---

This repository does not implement a centralized configuration system. There are no configuration files (such as .env, .yaml, .toml, .json, or settings.py), no environment variable loading logic, and no dedicated configuration module. All runtime behavior is controlled through two mechanisms:

1. **Command-line arguments** — `main.py` uses Python's `argparse` to accept parameters like `--deck-a`, `--deck-b`, `--matches`, `--all-matchups`, `--list-decks`, and `--seed`. These override defaults at invocation time.
2. **Hardcoded in-memory defaults** — Deck definitions live in `decks/__init__.py` as Python constants (`ALL_DECKS`, individual deck lists). Simulation parameters such as starting life (20), initial hand size (7), AI aggressiveness ranges (0.35–0.65), and verbosity levels (0/1/2) are embedded directly in the code of `src/simulator.py` and `main.py`.

There is no mechanism to load configuration from external sources, no feature flags, and no separation between config and code. Any change to game rules, deck compositions, or simulation parameters requires modifying the Python source files directly.