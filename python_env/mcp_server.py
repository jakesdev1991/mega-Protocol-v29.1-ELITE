# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import argparse
from mcp.server.fastmcp import FastMCP
import os
import sys

# Ensure project root is in path for shared configuration defaults
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from configs.config import config

# Initialize FastMCP server
mcp = FastMCP("Omega_Workspace_Filesystem")

# Restrict access to the project directory for security
BASE_DIR = os.path.abspath(r"C:\Users\Jakesdev1991\Downloads\training")

def get_safe_path(rel_path: str) -> str:
    """Ensure the path remains inside the workspace boundary."""
    target = os.path.abspath(os.path.join(BASE_DIR, str(rel_path)))
    if not target.startswith(BASE_DIR):
        raise ValueError(f"Access denied: Path '{rel_path}' is outside the workspace.")
    return target

@mcp.tool()
def list_directory(path: str = ".") -> list[str]:
    """Lists the contents of a directory within the Omega workspace."""
    try:
        target = get_safe_path(path)
        if not os.path.isdir(target):
            return [f"Error: '{path}' is not a valid directory."]
        return os.listdir(target)
    except Exception as e:
        return [f"Error: {str(e)}"]

@mcp.tool()
def read_file(path: str) -> str:
    """Reads the complete contents of a file within the Omega workspace."""
    try:
        target = get_safe_path(path)
        if not os.path.isfile(target):
            return f"Error: '{path}' is not a valid file."
        with open(target, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
def get_file_info(path: str) -> dict:
    """Gets standard file/directory metadata (size, type) within the workspace."""
    try:
        target = get_safe_path(path)
        if not os.path.exists(target):
            return {"error": "Path does not exist"}
        stat = os.stat(target)
        return {
            "name": os.path.basename(target),
            "path": target,
            "size_bytes": stat.st_size,
            "is_dir": os.path.isdir(target),
            "is_file": os.path.isfile(target)
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Omega MCP Filesystem Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default=config.mcp_transport, help="Transport protocol to use (default: OMEGA_MCP_TRANSPORT or stdio)")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE transport (default: 8000)")
    args = parser.parse_args()

    print(f"Starting Omega MCP Server on {args.transport} transport...", file=sys.stderr)
    if args.transport == "sse":
        print(f"SSE Server will be available at http://localhost:{args.port}/sse", file=sys.stderr)
        mcp.run(transport='sse', port=args.port)
    else:
        mcp.run(transport='stdio')
