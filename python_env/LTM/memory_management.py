# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""PID-governed memory lifecycle control for the Omega LTM stack.

The SamsonMemoryController keeps the Qdrant working set near the Mark-I harmonic
attractor by measuring how much active memory is verified/stiff versus
transient/exploratory.  When the active manifold becomes noisy, it demotes or
removes weak Qdrant memories.  When a memory is stable but ages out of working
memory, it is staged for Milvus archival via ``milvus-bulk-insert``.
"""

from __future__ import annotations

import json
import math
import os
import sqlite3
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Sequence, Tuple

import numpy as np

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(PROJECT_ROOT)
sys.path.append(REPO_ROOT)

from configs.config import config
from LTM.process_memories import DB_PATH, cosine_similarity

MARK_1_ATTRACTOR = 0.35


class MemorySummarizer(Protocol):
    """Callable protocol for controlled reset summaries."""

    def __call__(self, memories: Sequence["MemoryRecord"]) -> str:
        """Return a compact summary of memories being reset."""


@dataclass
class MemoryControlConfig:
    """Configuration for PID control and lifecycle thresholds."""

    pid_kp: float = 0.7
    pid_ki: float = 0.05
    pid_kd: float = 0.2
    target_harmonic_ratio: float = MARK_1_ATTRACTOR
    promotion_stiffness_threshold: float = 0.82
    promotion_relevance_threshold: float = 0.68
    promotion_age_seconds: float = 7 * 24 * 60 * 60
    demotion_stiffness_threshold: float = 0.35
    demotion_relevance_threshold: float = 0.45
    deletion_stiffness_threshold: float = 0.18
    deletion_relevance_threshold: float = 0.2
    max_qdrant_working_set_size: int = 5000
    dissonance_critical_threshold: float = 0.75
    max_tick_deletions: int = 100
    max_tick_demotions: int = 250
    milvus_bulk_insert_command: Tuple[str, ...] = ("milvus-bulk-insert",)
    milvus_bulk_insert_timeout_seconds: int = 120
    dry_run: bool = False

    @classmethod
    def from_app_config(cls, app_config: Any = config) -> "MemoryControlConfig":
        """Build controller configuration from the repository config object."""

        command = getattr(app_config, "milvus_bulk_insert_command", ["milvus-bulk-insert"])
        if isinstance(command, str):
            command = tuple(command.split())
        else:
            command = tuple(command)

        return cls(
            pid_kp=float(getattr(app_config, "memory_pid_kp", cls.pid_kp)),
            pid_ki=float(getattr(app_config, "memory_pid_ki", cls.pid_ki)),
            pid_kd=float(getattr(app_config, "memory_pid_kd", cls.pid_kd)),
            target_harmonic_ratio=float(
                getattr(app_config, "memory_target_harmonic_ratio", MARK_1_ATTRACTOR)
            ),
            promotion_stiffness_threshold=float(
                getattr(
                    app_config,
                    "memory_promotion_stiffness_threshold",
                    cls.promotion_stiffness_threshold,
                )
            ),
            promotion_relevance_threshold=float(
                getattr(
                    app_config,
                    "memory_promotion_relevance_threshold",
                    cls.promotion_relevance_threshold,
                )
            ),
            promotion_age_seconds=float(
                getattr(app_config, "memory_promotion_age_seconds", cls.promotion_age_seconds)
            ),
            demotion_stiffness_threshold=float(
                getattr(app_config, "memory_demotion_stiffness_threshold", cls.demotion_stiffness_threshold)
            ),
            demotion_relevance_threshold=float(
                getattr(app_config, "memory_demotion_relevance_threshold", cls.demotion_relevance_threshold)
            ),
            deletion_stiffness_threshold=float(
                getattr(app_config, "memory_deletion_stiffness_threshold", cls.deletion_stiffness_threshold)
            ),
            deletion_relevance_threshold=float(
                getattr(app_config, "memory_deletion_relevance_threshold", cls.deletion_relevance_threshold)
            ),
            max_qdrant_working_set_size=int(
                getattr(app_config, "max_qdrant_working_set_size", cls.max_qdrant_working_set_size)
            ),
            dissonance_critical_threshold=float(
                getattr(
                    app_config,
                    "memory_dissonance_critical_threshold",
                    cls.dissonance_critical_threshold,
                )
            ),
            max_tick_deletions=int(getattr(app_config, "memory_max_tick_deletions", cls.max_tick_deletions)),
            max_tick_demotions=int(getattr(app_config, "memory_max_tick_demotions", cls.max_tick_demotions)),
            milvus_bulk_insert_command=command,
            milvus_bulk_insert_timeout_seconds=int(
                getattr(
                    app_config,
                    "milvus_bulk_insert_timeout_seconds",
                    cls.milvus_bulk_insert_timeout_seconds,
                )
            ),
            dry_run=bool(getattr(app_config, "memory_controller_dry_run", cls.dry_run)),
        )


@dataclass
class MemoryRecord:
    """A normalized memory from Qdrant or the legacy SQLite store."""

    id: Any
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    score: float = 0.0
    created_at: Optional[float] = None
    source: str = "qdrant"
    vector: Optional[List[float]] = None

    @property
    def stiffness(self) -> float:
        return _bounded_float(self.metadata.get("stiffness", self.metadata.get("stiffness_score", 0.0)))

    @property
    def relevance(self) -> float:
        candidates = (
            self.metadata.get("relevance"),
            self.metadata.get("relevance_score"),
            self.metadata.get("rerank_score"),
            self.score,
        )
        for value in candidates:
            if value is not None:
                return _bounded_float(value)
        return 0.0

    @property
    def verified(self) -> bool:
        return bool(self.metadata.get("verified") or self.metadata.get("is_verified"))

    @property
    def exploratory(self) -> bool:
        lifecycle = str(self.metadata.get("lifecycle", self.metadata.get("state", ""))).lower()
        return bool(
            self.metadata.get("exploratory")
            or self.metadata.get("transient")
            or lifecycle in {"transient", "exploratory", "working", "draft"}
        )

    @property
    def age_seconds(self) -> float:
        if self.created_at is None:
            return 0.0
        return max(0.0, time.time() - self.created_at)


@dataclass
class PIDState:
    """PID accumulator persisted across ticks."""

    integral: float = 0.0
    previous_error: float = 0.0
    last_tick: Optional[float] = None


@dataclass
class MemoryControlReport:
    """Structured result from a Samson control tick."""

    timestamp: str
    total_active: int
    verified_stiff_count: int
    transient_exploratory_count: int
    harmonic_ratio: float
    error: float
    proportional: float
    integral: float
    derivative: float
    control_signal: float
    dissonance: float
    demoted_ids: List[Any] = field(default_factory=list)
    deleted_ids: List[Any] = field(default_factory=list)
    promoted_ids: List[Any] = field(default_factory=list)
    reset_triggered: bool = False
    reset_summary: Optional[str] = None
    milvus_result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "total_active": self.total_active,
            "verified_stiff_count": self.verified_stiff_count,
            "transient_exploratory_count": self.transient_exploratory_count,
            "harmonic_ratio": self.harmonic_ratio,
            "error": self.error,
            "pid": {
                "proportional": self.proportional,
                "integral": self.integral,
                "derivative": self.derivative,
                "control_signal": self.control_signal,
            },
            "dissonance": self.dissonance,
            "actions": {
                "demoted_ids": self.demoted_ids,
                "deleted_ids": self.deleted_ids,
                "promoted_ids": self.promoted_ids,
                "reset_triggered": self.reset_triggered,
                "reset_summary": self.reset_summary,
                "milvus_result": self.milvus_result,
            },
        }


class SamsonMemoryController:
    """PID controller for Qdrant working-memory hygiene and Milvus promotion."""

    MARK_1_ATTRACTOR = MARK_1_ATTRACTOR

    def __init__(
        self,
        control_config: Optional[MemoryControlConfig] = None,
        qdrant_memory_system: Optional[Any] = None,
        summarizer: Optional[MemorySummarizer] = None,
    ):
        self.config = control_config or MemoryControlConfig.from_app_config()
        self.qdrant_memory_system = qdrant_memory_system
        self.summarizer = summarizer or self._default_summarizer
        self.pid_state = PIDState()
        self.knowledge_dir = os.path.join(PROJECT_ROOT, "agent_zero", "knowledge")

    def control_tick(self, active_records: Optional[Sequence[MemoryRecord]] = None) -> MemoryControlReport:
        """Run one proportional-integral-derivative lifecycle tick."""

        records = list(active_records) if active_records is not None else self.fetch_active_memories()
        ratio, verified_count, transient_count = self.compute_harmonic_ratio(records)
        now = time.time()
        dt = max(now - self.pid_state.last_tick, 1.0) if self.pid_state.last_tick else 1.0
        error = self.config.target_harmonic_ratio - ratio
        self.pid_state.integral += error * dt
        derivative_error = (error - self.pid_state.previous_error) / dt
        proportional = self.config.pid_kp * error
        integral = self.config.pid_ki * self.pid_state.integral
        derivative = self.config.pid_kd * derivative_error
        control_signal = proportional + integral + derivative
        self.pid_state.previous_error = error
        self.pid_state.last_tick = now

        dissonance = self.compute_dissonance(records, ratio, error)
        reset_triggered = dissonance >= self.config.dissonance_critical_threshold
        reset_summary = None
        demoted_ids: List[Any] = []
        deleted_ids: List[Any] = []

        if reset_triggered:
            reset_summary = self.controlled_reset_summary(records)
            demoted_ids.extend(self.demote_memories(self._reset_demote_candidates(records)))
        elif self._active_store_is_too_noisy(records, control_signal):
            delete_candidates, demote_candidates = self.select_noise_reduction_candidates(records, control_signal)
            deleted_ids.extend(self.delete_memories(delete_candidates))
            demoted_ids.extend(self.demote_memories(demote_candidates))

        promoted_ids, milvus_result = self.promote_aged_stiff_memories(records)

        return MemoryControlReport(
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_active=len(records),
            verified_stiff_count=verified_count,
            transient_exploratory_count=transient_count,
            harmonic_ratio=ratio,
            error=error,
            proportional=proportional,
            integral=integral,
            derivative=derivative,
            control_signal=control_signal,
            dissonance=dissonance,
            demoted_ids=demoted_ids,
            deleted_ids=deleted_ids,
            promoted_ids=promoted_ids,
            reset_triggered=reset_triggered,
            reset_summary=reset_summary,
            milvus_result=milvus_result,
        )

    def fetch_active_memories(self) -> List[MemoryRecord]:
        """Fetch active memories from Qdrant, falling back to legacy SQLite."""

        if self.qdrant_memory_system is not None:
            return self._fetch_qdrant_memories()
        return self._fetch_sqlite_memories()

    def compute_harmonic_ratio(self, records: Sequence[MemoryRecord]) -> Tuple[float, int, int]:
        """Return verified/stiff share versus transient/exploratory composition."""

        if not records:
            return self.config.target_harmonic_ratio, 0, 0

        stiff_threshold = self.config.promotion_stiffness_threshold
        relevance_threshold = self.config.promotion_relevance_threshold
        verified_stiff_count = sum(
            1
            for record in records
            if record.verified or (record.stiffness >= stiff_threshold and record.relevance >= relevance_threshold)
        )
        transient_exploratory_count = sum(
            1
            for record in records
            if record.exploratory
            or record.stiffness <= self.config.demotion_stiffness_threshold
            or record.relevance <= self.config.demotion_relevance_threshold
        )
        denominator = verified_stiff_count + transient_exploratory_count
        if denominator == 0:
            return 0.0, verified_stiff_count, transient_exploratory_count
        return verified_stiff_count / denominator, verified_stiff_count, transient_exploratory_count

    def compute_dissonance(self, records: Sequence[MemoryRecord], ratio: float, error: float) -> float:
        """Compute bounded dissonance pressure for reset/summarization gating."""

        if not records:
            return 0.0
        low_stiffness = sum(1 for record in records if record.stiffness <= self.config.deletion_stiffness_threshold)
        low_relevance = sum(1 for record in records if record.relevance <= self.config.deletion_relevance_threshold)
        working_set_pressure = max(0.0, len(records) - self.config.max_qdrant_working_set_size) / max(
            self.config.max_qdrant_working_set_size,
            1,
        )
        harmonic_pressure = min(abs(error) / max(self.config.target_harmonic_ratio, 0.01), 1.0)
        noise_pressure = (low_stiffness + low_relevance) / max(len(records) * 2, 1)
        ratio_floor_pressure = max(0.0, self.config.target_harmonic_ratio - ratio)
        return _bounded_float(0.45 * harmonic_pressure + 0.35 * noise_pressure + 0.2 * working_set_pressure + ratio_floor_pressure)

    def select_noise_reduction_candidates(
        self,
        records: Sequence[MemoryRecord],
        control_signal: float,
    ) -> Tuple[List[MemoryRecord], List[MemoryRecord]]:
        """Choose low-value Qdrant memories to delete or demote when noise is high."""

        noisy_records = sorted(records, key=lambda record: (record.stiffness + record.relevance, -record.age_seconds))
        requested = max(1, math.ceil(abs(control_signal) * max(len(records), 1)))
        overage = max(0, len(records) - self.config.max_qdrant_working_set_size)
        budget = max(requested, overage)

        delete_candidates = [
            record
            for record in noisy_records
            if record.source == "qdrant"
            and record.stiffness <= self.config.deletion_stiffness_threshold
            and record.relevance <= self.config.deletion_relevance_threshold
        ][: min(budget, self.config.max_tick_deletions)]
        delete_ids = {record.id for record in delete_candidates}

        demote_budget = max(0, budget - len(delete_candidates))
        demote_candidates = [
            record
            for record in noisy_records
            if record.source == "qdrant"
            and record.id not in delete_ids
            and record.stiffness <= self.config.demotion_stiffness_threshold
            and record.relevance <= self.config.demotion_relevance_threshold
        ][: min(demote_budget, self.config.max_tick_demotions)]
        return delete_candidates, demote_candidates

    def delete_memories(self, records: Sequence[MemoryRecord]) -> List[Any]:
        """Delete low-stiffness, low-relevance memories from Qdrant."""

        ids = [record.id for record in records if record.source == "qdrant"]
        if not ids or self.config.dry_run or self.qdrant_memory_system is None:
            return ids if self.config.dry_run else []
        client, collection_name = self._qdrant_client_and_collection()
        client.delete(collection_name=collection_name, points_selector=ids)
        return ids

    def demote_memories(self, records: Sequence[MemoryRecord]) -> List[Any]:
        """Mark Qdrant memories as demoted so retrieval can down-rank them."""

        ids = [record.id for record in records if record.source == "qdrant"]
        if not ids or self.config.dry_run or self.qdrant_memory_system is None:
            return ids if self.config.dry_run else []
        client, collection_name = self._qdrant_client_and_collection()
        for record in records:
            if record.source != "qdrant":
                continue
            metadata = dict(record.metadata)
            metadata.update({"lifecycle": "demoted", "demoted_at": datetime.now(timezone.utc).isoformat()})
            client.set_payload(
                collection_name=collection_name,
                payload={"metadata": metadata, "lifecycle": "demoted"},
                points=[record.id],
            )
        return ids

    def promote_aged_stiff_memories(self, records: Sequence[MemoryRecord]) -> Tuple[List[Any], Optional[Dict[str, Any]]]:
        """Promote stable aged-out Qdrant memories to Milvus via milvus-bulk-insert."""

        candidates = [
            record
            for record in records
            if record.source == "qdrant"
            and record.age_seconds >= self.config.promotion_age_seconds
            and record.stiffness >= self.config.promotion_stiffness_threshold
            and record.relevance >= self.config.promotion_relevance_threshold
        ]
        if not candidates:
            return [], None

        if self.config.dry_run:
            return [record.id for record in candidates], {"dry_run": True, "count": len(candidates)}

        payload_path = self._write_milvus_payload(candidates)
        command = [*self.config.milvus_bulk_insert_command, str(payload_path)]
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=self.config.milvus_bulk_insert_timeout_seconds,
        )
        result = {
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout[-2000:],
            "stderr": completed.stderr[-2000:],
            "payload_path": str(payload_path),
        }
        if completed.returncode == 0:
            self.demote_memories(candidates)
        return [record.id for record in candidates] if completed.returncode == 0 else [], result

    def controlled_reset_summary(self, records: Sequence[MemoryRecord]) -> str:
        """Summarize high-dissonance working memory before controlled reset."""

        reset_candidates = self._reset_demote_candidates(records)
        return self.summarizer(reset_candidates)

    def scan_log_redundancy(self) -> List[Dict[str, Any]]:
        """Scan for oversized active jsonl logs that should be compressed."""

        if not os.path.isdir(self.knowledge_dir):
            return []
        logs = [name for name in os.listdir(self.knowledge_dir) if name.endswith(".jsonl")]
        redundant_logs = []
        for log_name in logs:
            path = os.path.join(self.knowledge_dir, log_name)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            if size_mb > 10.0:
                redundant_logs.append({"file": log_name, "size_mb": round(size_mb, 2), "action": "compress"})
        return redundant_logs

    def run_epoch(self) -> Dict[str, Any]:
        """Compatibility entry point for scheduled memory-management epochs."""

        print("🧹 [SamsonMemoryController] Performing PID memory lifecycle sweep...")
        report = self.control_tick().to_dict()
        report["log_optimization"] = self.scan_log_redundancy()
        print("--- BEGIN MEMORY CONTROL REPORT ---")
        print(json.dumps(report, indent=2, default=str))
        print("--- END MEMORY CONTROL REPORT ---")
        return report

    def _active_store_is_too_noisy(self, records: Sequence[MemoryRecord], control_signal: float) -> bool:
        return bool(
            records
            and (
                control_signal > 0
                or len(records) > self.config.max_qdrant_working_set_size
            )
        )

    def _reset_demote_candidates(self, records: Sequence[MemoryRecord]) -> List[MemoryRecord]:
        return [
            record
            for record in sorted(records, key=lambda item: (item.stiffness + item.relevance, -item.age_seconds))
            if record.source == "qdrant"
            and (
                record.stiffness <= self.config.demotion_stiffness_threshold
                or record.relevance <= self.config.demotion_relevance_threshold
                or record.exploratory
            )
        ][: self.config.max_tick_demotions]

    def _fetch_qdrant_memories(self) -> List[MemoryRecord]:
        client, collection_name = self._qdrant_client_and_collection()
        points, _next_page = client.scroll(
            collection_name=collection_name,
            limit=self.config.max_qdrant_working_set_size * 2,
            with_payload=True,
            with_vectors=True,
        )
        return [self._record_from_qdrant_point(point) for point in points]

    def _fetch_sqlite_memories(self) -> List[MemoryRecord]:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, content, vector_data, metadata FROM local_memories")
                rows = cursor.fetchall()
        except sqlite3.Error:
            return []

        records: List[MemoryRecord] = []
        for row_id, content, vector_data, metadata_str in rows:
            metadata = _safe_json(metadata_str, {})
            if not isinstance(metadata, dict):
                metadata = {}
            vector = _safe_json(vector_data, None)
            records.append(
                MemoryRecord(
                    id=row_id,
                    content=content,
                    metadata=metadata,
                    source="sqlite",
                    vector=vector if isinstance(vector, list) else None,
                )
            )
        self._annotate_legacy_relevance(records)
        return records

    def _annotate_legacy_relevance(self, records: Sequence[MemoryRecord]) -> None:
        if len(records) < 2:
            return
        vectors = [np.array(record.vector) for record in records if record.vector]
        if not vectors:
            return
        centroid = np.mean(vectors, axis=0)
        for record in records:
            if record.vector:
                record.score = _bounded_float((cosine_similarity(np.array(record.vector), centroid) + 1.0) / 2.0)

    def _qdrant_client_and_collection(self) -> Tuple[Any, str]:
        client = getattr(self.qdrant_memory_system, "client", self.qdrant_memory_system)
        collection_name = getattr(self.qdrant_memory_system, "collection_name", "omega_memories")
        return client, collection_name

    def _record_from_qdrant_point(self, point: Any) -> MemoryRecord:
        payload = dict(getattr(point, "payload", {}) or {})
        metadata = payload.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}
        merged_metadata = {**payload, **metadata}
        content = str(payload.get("content", metadata.get("content", "")))
        created_at = _parse_created_at(payload.get("created_at") or metadata.get("created_at"))
        return MemoryRecord(
            id=getattr(point, "id", payload.get("id")),
            content=content,
            metadata=merged_metadata,
            score=float(getattr(point, "score", payload.get("score", 0.0)) or 0.0),
            created_at=created_at,
            source="qdrant",
            vector=getattr(point, "vector", None),
        )

    def _write_milvus_payload(self, candidates: Sequence[MemoryRecord]) -> Path:
        output_dir = Path(tempfile.mkdtemp(prefix="samson_milvus_"))
        payload_path = output_dir / "bulk_insert.jsonl"
        with payload_path.open("w", encoding="utf-8") as handle:
            for record in candidates:
                handle.write(
                    json.dumps(
                        {
                            "id": str(record.id),
                            "content": record.content,
                            "metadata": {
                                **record.metadata,
                                "source": "qdrant",
                                "promoted_at": datetime.now(timezone.utc).isoformat(),
                            },
                            "vector": record.vector,
                        },
                        default=str,
                    )
                    + "\n"
                )
        return payload_path

    def _default_summarizer(self, memories: Sequence[MemoryRecord]) -> str:
        if not memories:
            return "No reset candidates required summarization."
        snippets = [memory.content.strip().replace("\n", " ")[:240] for memory in memories[:20] if memory.content]
        summary = " | ".join(snippets)
        return f"Controlled reset summarized {len(memories)} noisy memories: {summary[:1800]}"


class MemoryManagement(SamsonMemoryController):
    """Backward-compatible name for scheduled janitor integrations."""

    def __init__(self, redundancy_threshold: float = 0.94, **kwargs: Any):
        super().__init__(**kwargs)
        self.threshold = redundancy_threshold


def _bounded_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(number) or math.isinf(number):
        return 0.0
    return max(0.0, min(1.0, number))


def _safe_json(raw: Any, default: Any) -> Any:
    if raw is None:
        return default
    if isinstance(raw, (dict, list)):
        return raw
    try:
        return json.loads(raw)
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def _parse_created_at(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).timestamp()
    except ValueError:
        return None


if __name__ == "__main__":
    mm = MemoryManagement()
    mm.run_epoch()
