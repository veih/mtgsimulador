---
kind: logging_system
name: Logging System — Minimal In-Memory Game Log with print() Console Output
category: logging_system
scope:
    - '**'
source_files:
    - simuladorMtg/src/game_state.py
    - simuladorMtg/main.py
---

This repository does not implement a formal logging system. There is no use of Python's `logging` module, no logger configuration, no log levels (DEBUG/INFO/WARNING/ERROR), no structured log fields, and no external sinks (files, streams, handlers). Instead, the codebase uses two ad-hoc output mechanisms:

1. **In-memory game log**: `GameState` maintains a `game_log: list` field (line 185 in `src/game_state.py`) and appends timestamped entries via the `log(message)` method, which formats each entry as `[T{turn_number}] {message}`. This is purely an internal record of game events stored in memory; it is not routed to any sink or file.

2. **Console output via `print()`**: The CLI entry point (`main.py`) uses `print()` statements throughout for user-facing output — headers, stats tables, progress messages, error prompts, and analysis summaries. There is no abstraction layer around printing; all console output is scattered directly in functions like `print_header()`, `print_stats()`, `print_all_matchups_summary()`, and inline in `interactive_mode()` and `all_matchups_mode()`.

No centralized logging configuration exists. There are no log files written, no rotation, no filtering by severity, and no way to disable or redirect output programmatically beyond passing a `verbosity` parameter to `MatchSimulator` (which controls whether per-game output is printed, but still via `print()`). Error handling is done through `try/except KeyboardInterrupt` and simple `print(f"Erro: ...")` messages rather than exception logging.