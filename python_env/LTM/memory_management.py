# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Repository-wide memory hygiene controller.

``SamsonMemoryController`` keeps the original janitor behavior while separating
SQLite inspection, archival summarization, and log compression planning into
small testable methods.  ``MemoryManagement`` remains as a compatibility alias
for existing launch scripts.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

DEFAULT_DB_PATH = PROJECT_ROOT / "LTM" / "memories.db"


def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculate cosine similarity while guarding zero vectors."""
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return float(np.dot(v1, v2) / (norm_v1 * norm_v2))


@dataclass(frozen=True)
class MemoryRow:
    """SQLite memory row normalized for controller analysis."""

    id: int
    content: str
    vector: np.ndarray


class SamsonMemoryController:
    """RCOD-based global manifold janitor for memories and JSONL logs."""

    def __init__(
        self,
        redundancy_threshold: float = 0.94,
        *,
        db_path: str | os.PathLike[str] = DEFAULT_DB_PATH,
        knowledge_dir: str | os.PathLike[str] | None = None,
        old_memory_window: int = 50,
        summarization_batch_size: int = 20,
        log_size_limit_mb: float = 10.0,
        finance_agent: Any | None = None,
    ):
        self.threshold = redundancy_threshold
        self.db_path = Path(db_path)
        self.knowledge_dir = Path(knowledge_dir) if knowledge_dir else PROJECT_ROOT / "agent_zero" / "knowledge"
        self.old_memory_window = old_memory_window
        self.summarization_batch_size = summarization_batch_size
        self.log_size_limit_mb = log_size_limit_mb
        if finance_agent is None:
            from finance.finance_agent import FinanceAgent

            finance_agent = FinanceAgent("Omega-Janitor")
        self.agent = finance_agent

    def scan_log_redundancy(self) -> list[dict[str, Any]]:
        """Scan top-level JSONL logs and mark oversized files for compression."""
        if not self.knowledge_dir.exists():
            return []

        redundant_logs: list[dict[str, Any]] = []
        for path in sorted(self.knowledge_dir.glob("*.jsonl")):
            size_mb = path.stat().st_size / (1024 * 1024)
            if size_mb > self.log_size_limit_mb:
                redundant_logs.append(
                    {"file": path.name, "size_mb": round(size_mb, 2), "action": "compress"}
                )
        return redundant_logs

    def load_memory_rows(self) -> list[MemoryRow]:
        """Load valid memory rows from SQLite, skipping malformed vectors."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, content, vector_data FROM local_memories")
                rows = cursor.fetchall()
        except sqlite3.Error as exc:
            print(f"Error accessing DB: {exc}")
            return []

        parsed_rows: list[MemoryRow] = []
        for row_id, content, vector_data in rows:
            try:
                parsed_rows.append(MemoryRow(int(row_id), str(content), np.array(json.loads(vector_data))))
            except (TypeError, ValueError, json.JSONDecodeError) as exc:
                print(f"Skipping malformed memory row {row_id}: {exc}")
        return parsed_rows

    def find_redundant_memories(self, rows: Iterable[MemoryRow]) -> list[dict[str, Any]]:
        """Find duplicate-like memories by pairwise cosine similarity."""
        memories = list(rows)
        redundancies: list[dict[str, Any]] = []
        redundant_ids: set[int] = set()

        for index, left in enumerate(memories):
            if left.id in redundant_ids:
                continue
            for right in memories[index + 1 :]:
                if right.id in redundant_ids:
                    continue
                score = cosine_similarity(left.vector, right.vector)
                if score > self.threshold:
                    redundant_ids.add(right.id)
                    redundancies.append(
                        {"id": right.id, "content": right.content[:50] + "...", "score": round(score, 4)}
                    )
        return redundancies

    def select_old_memories(self, rows: Iterable[MemoryRow]) -> list[str]:
        """Select older rows by insertion order, preserving the previous window semantics."""
        memories = list(rows)
        cutoff = max(0, len(memories) - self.old_memory_window)
        return [row.content for row in memories[:cutoff]]

    def summarize_old_memories(self, old_memories: list[str]) -> str:
        """Compress old memories into a high-density archival constant when useful."""
        if len(old_memories) <= 10:
            return ""

        print(f"🧠 [Janitor] Summarizing {len(old_memories)} old memories into a single epoch constant...")
        prompt = (
            "Summarize the following old memories into a single, high-density informational constant "
            "for the Omega Protocol. Retain all technical derivations and approved insights but remove "
            "conversational noise:\n\n"
            + "\n".join(old_memories[: self.summarization_batch_size])
        )
        return self.agent.reason(prompt)

    def build_report(self) -> dict[str, Any]:
        """Build the complete memory and log optimization report."""
        rows = self.load_memory_rows()
        redundancies = self.find_redundant_memories(rows) if len(rows) > 2 else []
        old_memories = self.select_old_memories(rows)
        summary = self.summarize_old_memories(old_memories)
        log_plan = self.scan_log_redundancy()

        return {
            "scope": "DIRECTORY-WIDE",
            "db_optimization": {
                "total_entries": len(rows),
                "redundant_ids": [item["id"] for item in redundancies],
                "redundant_candidates": redundancies,
                "old_memories_compressed": len(old_memories[: self.summarization_batch_size]),
                "new_archival_constant": summary[:200] + "..." if summary else "None",
            },
            "log_optimization": log_plan,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def run_epoch(self) -> dict[str, Any]:
        """Run one controller sweep and print the proposed learning report."""
        print("🧹 [Samson Memory Controller] Performing global manifold sweep...")
        report = self.build_report()
        print("--- BEGIN PROPOSED LEARNING ---")
        print(json.dumps(report, indent=2))
        print("--- END PROPOSED LEARNING ---")
        return report


class MemoryManagement(SamsonMemoryController):
    """Backward-compatible name for legacy scripts."""


if __name__ == "__main__":
    SamsonMemoryController().run_epoch()
