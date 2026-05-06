# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Central runtime configuration for Python LTM components."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


BASE_DIR = Path(__file__).resolve().parents[1]


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_command(name: str, default: str) -> List[str]:
    raw = os.getenv(name, default)
    return [part for part in raw.split() if part]


@dataclass(frozen=True)
class OmegaConfig:
    """Repository-wide defaults used by memory storage and lifecycle control."""

    ltm_dir: Path = field(default_factory=lambda: BASE_DIR / "LTM")
    qdrant_path: Path = field(default_factory=lambda: BASE_DIR / "LTM" / "qdrant_storage")
    ltm_embedding: str = field(
        default_factory=lambda: os.getenv("OMEGA_LTM_EMBEDDING", "Qwen/Qwen3-Embedding-0.6B")
    )
    reranker_model: str = field(
        default_factory=lambda: os.getenv("OMEGA_RERANKER_MODEL", "Qwen/Qwen3-Reranker-0.6B")
    )
    ollama_embed_url: str = field(
        default_factory=lambda: os.getenv("OMEGA_OLLAMA_EMBED_URL", "http://localhost:11434/api/embeddings")
    )
    ollama_generate_url: str = field(
        default_factory=lambda: os.getenv("OMEGA_OLLAMA_GENERATE_URL", "http://localhost:11434/api/generate")
    )

    memory_target_harmonic_ratio: float = 0.35
    memory_pid_kp: float = field(default_factory=lambda: _env_float("OMEGA_MEMORY_PID_KP", 0.7))
    memory_pid_ki: float = field(default_factory=lambda: _env_float("OMEGA_MEMORY_PID_KI", 0.05))
    memory_pid_kd: float = field(default_factory=lambda: _env_float("OMEGA_MEMORY_PID_KD", 0.2))
    memory_promotion_stiffness_threshold: float = field(
        default_factory=lambda: _env_float("OMEGA_MEMORY_PROMOTION_STIFFNESS_THRESHOLD", 0.82)
    )
    memory_promotion_relevance_threshold: float = field(
        default_factory=lambda: _env_float("OMEGA_MEMORY_PROMOTION_RELEVANCE_THRESHOLD", 0.68)
    )
    memory_promotion_age_seconds: int = field(
        default_factory=lambda: _env_int("OMEGA_MEMORY_PROMOTION_AGE_SECONDS", 7 * 24 * 60 * 60)
    )
    memory_demotion_stiffness_threshold: float = field(
        default_factory=lambda: _env_float("OMEGA_MEMORY_DEMOTION_STIFFNESS_THRESHOLD", 0.35)
    )
    memory_demotion_relevance_threshold: float = field(
        default_factory=lambda: _env_float("OMEGA_MEMORY_DEMOTION_RELEVANCE_THRESHOLD", 0.45)
    )
    memory_deletion_stiffness_threshold: float = field(
        default_factory=lambda: _env_float("OMEGA_MEMORY_DELETION_STIFFNESS_THRESHOLD", 0.18)
    )
    memory_deletion_relevance_threshold: float = field(
        default_factory=lambda: _env_float("OMEGA_MEMORY_DELETION_RELEVANCE_THRESHOLD", 0.2)
    )
    max_qdrant_working_set_size: int = field(
        default_factory=lambda: _env_int("OMEGA_MAX_QDRANT_WORKING_SET_SIZE", 5000)
    )
    memory_dissonance_critical_threshold: float = field(
        default_factory=lambda: _env_float("OMEGA_MEMORY_DISSONANCE_CRITICAL_THRESHOLD", 0.75)
    )
    memory_max_tick_deletions: int = field(
        default_factory=lambda: _env_int("OMEGA_MEMORY_MAX_TICK_DELETIONS", 100)
    )
    memory_max_tick_demotions: int = field(
        default_factory=lambda: _env_int("OMEGA_MEMORY_MAX_TICK_DEMOTIONS", 250)
    )
    milvus_bulk_insert_command: List[str] = field(
        default_factory=lambda: _env_command("OMEGA_MILVUS_BULK_INSERT_COMMAND", "milvus-bulk-insert")
    )
    milvus_bulk_insert_timeout_seconds: int = field(
        default_factory=lambda: _env_int("OMEGA_MILVUS_BULK_INSERT_TIMEOUT_SECONDS", 120)
    )
    memory_controller_dry_run: bool = field(
        default_factory=lambda: _env_bool("OMEGA_MEMORY_CONTROLLER_DRY_RUN", False)
    )


config = OmegaConfig()
