# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Memory substrates for the Agent Zero dual-manifold runtime."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import MemoryRecord, SanitizedPromotion


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KNOWLEDGE_DIR = PROJECT_ROOT / "agent_zero" / "knowledge"
DEFAULT_ROLE_MEMORY_DIR = DEFAULT_KNOWLEDGE_DIR / "role_local"
DEFAULT_ANTI_MEMORY_DIR = DEFAULT_KNOWLEDGE_DIR / "anti_private"
DEFAULT_DB_PATH = PROJECT_ROOT / "LTM" / "memories.db"


class SharedConsensusMemory:
    """SQLite-backed shared memory exposed to both manifolds for read access."""

    def __init__(self, db_path: str | Path | None = None, table_name: str = "omega_shared_consensus"):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        self.table_name = table_name
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_table()

    def _ensure_table(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def promote(
        self,
        promotion: SanitizedPromotion,
        source: str,
        *,
        writer: str = "governor",
        metadata: dict | None = None,
    ) -> MemoryRecord:
        """Persist a governor-approved, sanitized artifact into the shared manifold."""
        if writer != "governor":
            raise PermissionError("Shared consensus writes must be promoted by the governor.")

        merged_metadata = {
            "memory_type": "scm",
            "promotion_kind": promotion.kind,
            "promotion_tags": promotion.tags,
            **promotion.metadata,
            **(metadata or {}),
        }
        record = MemoryRecord(source=source, content=promotion.content, metadata=merged_metadata)
        self.append(record)
        return record

    def append(self, record: MemoryRecord) -> None:
        """Directly append a record to shared memory (legacy/unfiltered)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"INSERT INTO {self.table_name} (entry_id, source, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    record.entry_id,
                    record.source,
                    record.content,
                    json.dumps(record.metadata),
                    record.created_at.isoformat() if hasattr(record.created_at, "isoformat") else record.created_at,
                ),
            )
            conn.commit()

    def read(self, query: str | None = None, *, limit: int = 5, reader: str = "agent_zero") -> list[MemoryRecord]:
        """Read the most recent shared consensus entries, optionally filtered by text match."""
        _ = reader
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            sql = f"SELECT entry_id, source, content, metadata, created_at FROM {self.table_name}"
            params: tuple = ()
            if query:
                sql += " WHERE content LIKE ?"
                params = (f"%{query}%",)
            sql += " ORDER BY id DESC LIMIT ?"
            params = (*params, limit)
            cursor.execute(sql, params)
            rows = cursor.fetchall()

        records: list[MemoryRecord] = []
        for entry_id, source, content, metadata, created_at in rows:
            records.append(
                MemoryRecord(
                    entry_id=entry_id,
                    source=source,
                    content=content,
                    metadata=json.loads(metadata) if metadata else {},
                    created_at=created_at,
                )
            )
        return records


class RoleLocalMemory:
    """Per-role JSONL memory visible only to its owner and the Anti-Agency."""

    def __init__(self, owner_role: str, base_dir: str | Path | None = None):
        self.owner_role = owner_role
        self.base_dir = Path(base_dir or DEFAULT_ROLE_MEMORY_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.base_dir / f"{self.owner_role}.jsonl"

    def append(self, record: MemoryRecord, *, writer_role: str) -> None:
        if writer_role != self.owner_role:
            raise PermissionError(f"Only role '{self.owner_role}' can write to this local memory.")
        with self.file_path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")

    def read(self, *, reader_role: str, reader_manifold: str = "zero", limit: int = 10) -> list[MemoryRecord]:
        if reader_manifold != "anti" and reader_role != self.owner_role:
            raise PermissionError(f"Role '{reader_role}' cannot read local memory owned by '{self.owner_role}'.")
        if not self.file_path.exists():
            return []
        with self.file_path.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()[-limit:]
        return [MemoryRecord.model_validate_json(line) for line in lines]


class AntiPrivateMemory:
    """Sealed JSONL store for the Anti-Agency and its bandit strategy state."""

    def __init__(self, base_dir: str | Path | None = None):
        self.base_dir = Path(base_dir or DEFAULT_ANTI_MEMORY_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.base_dir / "anti_private.jsonl"
        self.strategy_path = self.base_dir / "strategy_weights.json"

    def append(self, record: MemoryRecord, *, writer_manifold: str = "anti") -> None:
        if writer_manifold not in {"anti", "governor"}:
            raise PermissionError("Only the Anti-Agency or governor can write to anti-private memory.")
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(record.model_dump_json() + "\n")

    def read(self, *, reader_manifold: str = "anti", limit: int = 50) -> list[MemoryRecord]:
        if reader_manifold != "anti":
            raise PermissionError("Anti-private memory is sealed from Agent Zero.")
        if not self.log_path.exists():
            return []
        with self.log_path.open("r", encoding="utf-8") as handle:
            lines = handle.readlines()[-limit:]
        return [MemoryRecord.model_validate_json(line) for line in lines]

    def load_strategy_weights(self, defaults: dict[str, float]) -> dict[str, float]:
        if not self.strategy_path.exists():
            return defaults.copy()
        with self.strategy_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        weights = defaults.copy()
        weights.update({key: float(value) for key, value in payload.items()})
        return weights

    def save_strategy_weights(self, weights: dict[str, float], *, writer_manifold: str = "anti") -> None:
        if writer_manifold not in {"anti", "governor"}:
            raise PermissionError("Only the Anti-Agency or governor can persist strategy weights.")
        with self.strategy_path.open("w", encoding="utf-8") as handle:
            json.dump(weights, handle, indent=2)
