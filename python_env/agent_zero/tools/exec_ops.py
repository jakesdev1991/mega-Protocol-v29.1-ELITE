# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import subprocess
from .registry import tool_link

@tool_link
def run_shell(command: str):
    """Executes a shell command and returns output (sandboxed via subprocess)."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing shell command: {str(e)}"

@tool_link
def run_python_snippet(code: str):
    """Executes a small Python code snippet and returns its local variables or output."""
    # Note: This is a basic implementation for internal use.
    # In a production environment, this would need more stringent sandboxing.
    local_vars = {}
    try:
        exec(code, {}, local_vars)
        # Filter out built-ins for cleaner return
        return {k: v for k, v in local_vars.items() if not k.startswith("__")}
    except Exception as e:
        return f"Error executing Python snippet: {str(e)}"
