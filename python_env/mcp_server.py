# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Ensure both repo root and python_env are importable when this file is run directly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from configs.config import config
from mcp_memory_server import register_memory_tools

# Initialize FastMCP server
mcp = FastMCP("Omega_Workspace_Filesystem")

# Restrict access to the configured project directory for security. Override with
# OMEGA_WORKSPACE_BASE_DIR when running outside the original Windows checkout.
BASE_DIR = config.workspace_base_dir.resolve()


def get_safe_path(rel_path: str) -> Path:
    """Ensure the path remains inside the workspace boundary."""
    target = (BASE_DIR / str(rel_path)).resolve()
    try:
        target.relative_to(BASE_DIR)
    except ValueError as exc:
        raise ValueError(f"Access denied: Path '{rel_path}' is outside the workspace.") from exc
    return target


@mcp.tool()
def list_directory(path: str = ".") -> list[str]:
    """Lists the contents of a directory within the Omega workspace."""
    try:
        target = get_safe_path(path)
        if not target.is_dir():
            return [f"Error: '{path}' is not a valid directory."]
        return os.listdir(target)
    except Exception as e:
        return [f"Error: {str(e)}"]


@mcp.tool()
def read_file(path: str) -> str:
    """Reads the complete contents of a file within the Omega workspace."""
    try:
        target = get_safe_path(path)
        if not target.is_file():
            return f"Error: '{path}' is not a valid file."
        with target.open("r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


@mcp.tool()
def get_file_info(path: str) -> dict:
    """Gets standard file/directory metadata (size, type) within the workspace."""
    try:
        target = get_safe_path(path)
        if not target.exists():
            return {"error": "Path does not exist"}
        stat = target.stat()
        return {
            "name": target.name,
            "path": str(target),
            "size_bytes": stat.st_size,
            "is_dir": target.is_dir(),
            "is_file": target.is_file(),
        }
    except Exception as e:
        return {"error": str(e)}


register_memory_tools(mcp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Omega MCP Filesystem Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport protocol to use (default: stdio)")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE transport (default: 8000)")
    args = parser.parse_args()

    print(f"Starting Omega MCP Server on {args.transport} transport...", file=sys.stderr)
    if args.transport == "sse":
        print(f"SSE Server will be available at http://localhost:{args.port}/sse", file=sys.stderr)
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run(transport="stdio")
