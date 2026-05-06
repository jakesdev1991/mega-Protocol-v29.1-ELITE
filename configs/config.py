# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Central runtime configuration for Omega memory services.

The Long-Term Memory stack imports the module-level ``config`` object from this
package. Defaults are intentionally local-development friendly while each value
can be overridden with an environment variable for deployed MCP/Qdrant/Milvus
nodes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parent.parent


def _optional_env(name: str) -> Optional[str]:
    value = os.getenv(name)
    return value if value not in (None, "") else None


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    return float(value) if value not in (None, "") else default


@dataclass(frozen=True)
class MemoryControllerConfig:
    """Samson/memory-controller guardrails and PID tuning constants."""

    stiffness_min_s: float = field(default_factory=lambda: _float_env("OMEGA_STIFFNESS_MIN_S", 0.35))
    reverse_overlap_max_r: float = field(default_factory=lambda: _float_env("OMEGA_REVERSE_OVERLAP_MAX_R", 0.62))
    dissonance_delta_max: float = field(default_factory=lambda: _float_env("OMEGA_DISSONANCE_DELTA_MAX", 0.18))
    zscore_warn: float = field(default_factory=lambda: _float_env("OMEGA_ZSCORE_WARN", 2.0))
    zscore_block: float = field(default_factory=lambda: _float_env("OMEGA_ZSCORE_BLOCK", 3.0))
    pid_kp: float = field(default_factory=lambda: _float_env("OMEGA_MEMORY_PID_KP", 0.42))
    pid_ki: float = field(default_factory=lambda: _float_env("OMEGA_MEMORY_PID_KI", 0.08))
    pid_kd: float = field(default_factory=lambda: _float_env("OMEGA_MEMORY_PID_KD", 0.21))


@dataclass(frozen=True)
class OmegaConfig:
    """Unified configuration for the Omega Protocol memory architecture."""

    qdrant_path: Path = field(
        default_factory=lambda: Path(os.getenv("OMEGA_QDRANT_PATH", REPO_ROOT / "python_env" / "LTM" / "qdrant_storage"))
    )
    qdrant_url: Optional[str] = field(default_factory=lambda: _optional_env("OMEGA_QDRANT_URL"))
    qdrant_collection: str = field(default_factory=lambda: os.getenv("OMEGA_QDRANT_COLLECTION", "omega_memories"))
    milvus_uri: str = field(default_factory=lambda: os.getenv("OMEGA_MILVUS_URI", "http://localhost:19530"))
    milvus_token: Optional[str] = field(default_factory=lambda: _optional_env("OMEGA_MILVUS_TOKEN"))
    milvus_collection: str = field(default_factory=lambda: os.getenv("OMEGA_MILVUS_COLLECTION", "omega_archive"))
    ltm_embedding: str = field(
        default_factory=lambda: os.getenv("OMEGA_EMBEDDING_MODEL", "Alibaba-NLP/gte-large-en-v1.5")
    )
    reranker_model: str = field(
        default_factory=lambda: os.getenv("OMEGA_RERANKER_MODEL", "BAAI/bge-reranker-large")
    )
    mcp_transport: str = field(default_factory=lambda: os.getenv("OMEGA_MCP_TRANSPORT", "stdio"))
    memory_controller: MemoryControllerConfig = field(default_factory=MemoryControllerConfig)


config = OmegaConfig()
