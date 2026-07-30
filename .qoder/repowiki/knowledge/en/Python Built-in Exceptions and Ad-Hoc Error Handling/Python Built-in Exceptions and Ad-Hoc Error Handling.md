---
kind: error_handling
name: Python Built-in Exceptions and Ad-Hoc Error Handling
category: error_handling
scope:
    - '**'
source_files:
    - simuladorMtg/main.py
    - simuladorMtg/decks/__init__.py
    - simuladorMtg/src/cards_db.py
---

This repository does not implement a dedicated error handling system. Instead, it relies on Python's built-in exception mechanism with ad-hoc try/except blocks at the user-input boundary.

**Approach used:**
- **Built-in exceptions only**: The codebase raises `ValueError` for invalid inputs (deck not found, card not found) and catches `ValueError`, `EOFError`, and `KeyboardInterrupt` in the CLI layer (`main.py`). No custom exception classes are defined anywhere in the project.
- **Localized error handling**: `try/except` blocks appear only around interactive input prompts in `main.py` (lines 186–226), where invalid user input is caught and a friendly message is printed before returning from the function. A `KeyboardInterrupt` is caught at the top level to gracefully exit.
- **No error propagation pattern**: Errors that are raised (e.g., `get_deck()` and `get_card()` raising `ValueError`) are not caught within the core simulation logic — they propagate upward unhandled. There is no middleware, logging framework, or centralized error handler.
- **No structured logging**: The game state maintains a `game_log` list (`game_state.py` line 231) that appends turn messages as strings, but this is a log of game events, not an error reporting mechanism.

**Key files with error-related code:**
- `simuladorMtg/main.py`: Only file containing `try/except` blocks; handles CLI input validation and graceful shutdown.
- `simuladorMtg/decks/__init__.py`: Raises `ValueError` when an unknown deck name is passed to `get_deck()`.
- `simuladorMtg/src/cards_db.py`: Raises `ValueError` when an unknown card ID is passed to `get_card()`.

**Conventions observed:**
- Validation errors use `ValueError` with descriptive Portuguese messages (e.g., "Deck não encontrado", "Carta não encontrada").
- User-facing errors are handled by printing a message and returning early rather than crashing.
- There is no distinction between recoverable and unrecoverable errors — all errors are treated uniformly as exceptions.