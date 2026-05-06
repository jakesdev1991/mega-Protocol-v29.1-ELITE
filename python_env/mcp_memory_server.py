# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""FastMCP memory tools for Qdrant and Milvus long-term memory."""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import os
import sys
from functools import lru_cache
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Ensure both repo root and python_env are importable when this file is run as a script.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from LTM.milvus_memory import MilvusMemorySystem

mcp = FastMCP("Omega_Memory")


@lru_cache(maxsize=1)
def _qdrant() -> Any:
    if importlib.util.find_spec("qdrant_client") is None:
        raise RuntimeError("qdrant-client is not installed; install qdrant-client to use Qdrant memory tools.")
    module = importlib.import_module("LTM.qdrant_memory")
    return module.QdrantMemorySystem()


@lru_cache(maxsize=1)
def _milvus() -> MilvusMemorySystem:
    return MilvusMemorySystem()


def _metadata_matches(metadata: Dict[str, Any], filters: Optional[Dict[str, Any]]) -> bool:
    if not filters:
        return True
    return all(metadata.get(key) == value for key, value in filters.items())


def qdrant_store(content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Store a content string and optional metadata in Qdrant."""
    if not isinstance(content, str) or not content.strip():
        return {"ok": False, "error": "content must be a non-empty string"}
    if metadata is not None and not isinstance(metadata, dict):
        return {"ok": False, "error": "metadata must be a dictionary when provided"}
    ok = _qdrant().add_memory(content=content, metadata=metadata)
    return {"ok": bool(ok), "backend": "qdrant"}


def qdrant_find(query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Find Qdrant memories by semantic query with optional exact metadata filters."""
    if not isinstance(query, str) or not query.strip():
        return []
    safe_limit = max(1, min(int(limit), 100))
    search_limit = safe_limit * 4 if filters else safe_limit
    results = _qdrant().search(query=query, limit=search_limit, filters=filters)
    filtered = [result for result in results if _metadata_matches(result.get("metadata", {}), filters)]
    return filtered[:safe_limit]


def milvus_bulk_insert(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Bulk insert memory records into Milvus."""
    if not isinstance(records, list):
        return {"ok": False, "error": "records must be a list of dictionaries"}
    if not all(isinstance(record, dict) for record in records):
        return {"ok": False, "error": "each record must be a dictionary"}
    result = _milvus().bulk_insert(records)
    result["ok"] = True
    result["backend"] = "milvus"
    return result


def milvus_hybrid_search(query: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Run Milvus hybrid search when supported, otherwise dense-vector fallback."""
    if not isinstance(query, str) or not query.strip():
        return {"ok": False, "error": "query must be a non-empty string", "results": []}
    safe_limit = max(1, min(int(limit), 100))
    result = _milvus().hybrid_search(query=query, limit=safe_limit, filters=filters)
    result["ok"] = True
    result["backend"] = "milvus"
    return result


def memory_health() -> Dict[str, Any]:
    """Report dependency and backend health without forcing heavy model loads."""
    health: Dict[str, Any] = {
        "qdrant": {"available": importlib.util.find_spec("qdrant_client") is not None},
        "milvus": {"available": MilvusMemorySystem.available()},
        "sentence_transformers": {"available": importlib.util.find_spec("sentence_transformers") is not None},
    }

    try_qdrant = os.getenv("OMEGA_MEMORY_HEALTH_CONNECT", "0") == "1"
    if try_qdrant and health["qdrant"]["available"]:
        qdrant = _qdrant()
        health["qdrant"].update({"collection": qdrant.collection_name, "path": str(qdrant.client._client.location) if hasattr(qdrant.client, "_client") else None})

    if health["milvus"]["available"] and os.getenv("OMEGA_MEMORY_HEALTH_CONNECT", "0") == "1":
        health["milvus"].update(_milvus().health())

    return health


def _register_tool(target_mcp: FastMCP, name: str, func: Any) -> None:
    """Register a tool name across FastMCP versions that differ on keyword support."""
    try:
        target_mcp.tool(name=name)(func)
    except TypeError:
        target_mcp.tool(name)(func)


def register_memory_tools(target_mcp: FastMCP) -> None:
    """Register stable kebab-case memory tool names on an existing FastMCP app."""
    _register_tool(target_mcp, "qdrant-store", qdrant_store)
    _register_tool(target_mcp, "qdrant-find", qdrant_find)
    _register_tool(target_mcp, "milvus-bulk-insert", milvus_bulk_insert)
    _register_tool(target_mcp, "milvus-hybrid-search", milvus_hybrid_search)
    _register_tool(target_mcp, "memory-health", memory_health)


register_memory_tools(mcp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Omega MCP Memory Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport protocol to use (default: stdio)")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE transport (default: 8000)")
    args = parser.parse_args()

    print(f"Starting Omega Memory MCP Server on {args.transport} transport...", file=sys.stderr)
    if args.transport == "sse":
        print(f"SSE Server will be available at http://localhost:{args.port}/sse", file=sys.stderr)
        mcp.run(transport="sse", port=args.port)
    else:
        mcp.run(transport="stdio")
