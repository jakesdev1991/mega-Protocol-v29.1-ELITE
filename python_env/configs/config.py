from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _path_from_env(name: str, default: Path) -> Path:
    return Path(os.getenv(name, str(default))).expanduser().resolve()


@dataclass(frozen=True)
class Config:
    repo_root: Path = _repo_root()
    python_env_dir: Path = repo_root / "python_env"
    workspace_base_dir: Path = _path_from_env("OMEGA_WORKSPACE_BASE_DIR", repo_root)
    qdrant_path: Path = _path_from_env(
        "OMEGA_QDRANT_PATH", python_env_dir / "LTM" / "qdrant_storage"
    )
    ltm_embedding: str = os.getenv("OMEGA_LTM_EMBEDDING", "Qwen/Qwen3-Embedding-0.6B")
    reranker_model: str = os.getenv("OMEGA_RERANKER_MODEL", "Qwen/Qwen3-Reranker-0.6B")
    milvus_uri: str = os.getenv("OMEGA_MILVUS_URI", "./python_env/LTM/milvus_lite.db")
    milvus_token: str | None = os.getenv("OMEGA_MILVUS_TOKEN")
    milvus_db_name: str = os.getenv("OMEGA_MILVUS_DB_NAME", "default")
    milvus_collection: str = os.getenv("OMEGA_MILVUS_COLLECTION", "omega_memories")
    milvus_dense_dim: int = int(os.getenv("OMEGA_MILVUS_DENSE_DIM", "1024"))
    milvus_text_max_length: int = int(os.getenv("OMEGA_MILVUS_TEXT_MAX_LENGTH", "65535"))


config = Config()
