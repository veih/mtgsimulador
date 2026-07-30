---
kind: frontend_style
name: No Frontend — CLI-Only Console Application
category: frontend_style
scope:
    - '**'
source_files:
    - simuladorMtg/main.py
---

This repository contains no frontend styling system whatsoever. The MTG Match Simulator is a pure Python command-line application with no HTML, CSS, JavaScript, or any web-based UI layer. All user interaction occurs through the terminal via `main.py`, which uses `print()` statements and `input()` for interactive prompts. Output formatting is done with plain text alignment, ASCII art headers (e.g., `"=" * 58`), and simple character-based progress bars using `#` and `.` characters. There are no `.css`, `.scss`, `.html`, `.js`, or any frontend asset files in the entire repository. The project is strictly a backend simulation engine exposed through a CLI interface.