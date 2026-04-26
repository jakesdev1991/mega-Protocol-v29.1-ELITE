# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
from .registry import tool_link

@tool_link
def read_local_file(path: str):
    """Reads the content of a local file."""
    if not os.path.exists(path):
        return f"Error: File '{path}' not found."
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

@tool_link
def write_local_file(path: str, content: str):
    """Writes content to a local file. Overwrites if exists."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    return f"Success: Wrote to {path}"

@tool_link
def list_local_dir(path: str = "."):
    """Lists files and directories in a given path."""
    if not os.path.isdir(path):
        return f"Error: '{path}' is not a directory."
    return ", ".join(os.listdir(path))
