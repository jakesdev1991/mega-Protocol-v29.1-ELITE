# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Adaptive retrieval leakage gate for long-term-memory search.

The gate keeps retrieval near the target harmonic state by maintaining rolling
systemic-error estimates and by rescoring candidates with both relevance and
stability signals.  It is intentionally dependency-light so Qdrant, Milvus, and
MCP health tooling can share one implementation.
"""

from __future__ import annotations

import math
import statistics
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Iterable, List, Mapping, MutableMapping, Optional


@dataclass
class ZScoreLeakageGate:
    """Z-score based retrieval gate centered on harmonic state ``0.35``.

    The gate tracks recent systemic signals:
    - dissonance from candidate/result metadata,
    - failed tool calls as a rate or count,
    - auditor conflicts as a rate or count,
    - retrieval variance from candidate similarity/reranker spreads.

    Positive Z-scores indicate the current state is above target and retrieval
    should constrict. Negative Z-scores indicate the system is under target and
    can open leakage to recover associative context.
    """

    target_harmonic_state: float = 0.35
    window_size: int = 64
    standard_error_floor: float = 0.05
    open_threshold_z: float = -1.0
    constricted_threshold_z: float = 1.0
    minimum_allow_score: float = 0.2
    _dissonance: Deque[float] = field(default_factory=deque, init=False, repr=False)
    _failed_tool_calls: Deque[float] = field(default_factory=deque, init=False, repr=False)
    _auditor_conflicts: Deque[float] = field(default_factory=deque, init=False, repr=False)
    _retrieval_variance: Deque[float] = field(default_factory=deque, init=False, repr=False)
    _last_z_score: float = field(default=0.0, init=False)
    _last_mode: str = field(default="normal", init=False)
    _last_result_count: int = field(default=0, init=False)

    def update_metrics(
        self,
        *,
        dissonance: Optional[float] = None,
        failed_tool_calls: Optional[float] = None,
        auditor_conflicts: Optional[float] = None,
        retrieval_variance: Optional[float] = None,
    ) -> None:
        """Add one observation for any supplied systemic-error channel."""

        self._append(self._dissonance, dissonance)
        self._append(self._failed_tool_calls, failed_tool_calls)
        self._append(self._auditor_conflicts, auditor_conflicts)
        self._append(self._retrieval_variance, retrieval_variance)

    def observe_results(self, results: Iterable[Mapping[str, Any]]) -> None:
        """Update rolling dissonance/retrieval-variance estimates from results."""

        materialized = list(results)
        self._last_result_count = len(materialized)
        scores = [self._numeric(result.get("vector_similarity", result.get("score")), 0.0) for result in materialized]
        dissonance = [self._metric(result, "dissonance_delta", 0.0) for result in materialized]
        if len(scores) > 1:
            self.update_metrics(retrieval_variance=statistics.pvariance(scores))
        elif scores:
            self.update_metrics(retrieval_variance=0.0)
        if dissonance:
            self.update_metrics(dissonance=sum(abs(value) for value in dissonance) / len(dissonance))

    def systemic_standard_error(self) -> float:
        """Return a rolling systemic standard-error estimate."""

        component_errors = [
            self._standard_error(self._dissonance),
            self._standard_error(self._failed_tool_calls),
            self._standard_error(self._auditor_conflicts),
            self._standard_error(self._retrieval_variance),
        ]
        active = [value for value in component_errors if value > 0.0]
        if not active:
            return self.standard_error_floor
        rms_error = math.sqrt(sum(value * value for value in active) / len(active))
        return max(self.standard_error_floor, rms_error)

    def z_score(self, current_state: Optional[float]) -> float:
        """Compute the current harmonic-state Z-score."""

        state = self.target_harmonic_state if current_state is None else self._numeric(current_state, self.target_harmonic_state)
        self._last_z_score = (state - self.target_harmonic_state) / self.systemic_standard_error()
        self._last_mode = self.mode(self._last_z_score)
        return self._last_z_score

    def mode(self, z_score: Optional[float] = None) -> str:
        """Return ``open-leakage``, ``normal``, or ``constricted``."""

        z = self._last_z_score if z_score is None else z_score
        if z <= self.open_threshold_z:
            return "open-leakage"
        if z >= self.constricted_threshold_z:
            return "constricted"
        return "normal"

    def score(self, result: Mapping[str, Any], current_state: Optional[float] = None) -> float:
        """Return a gated retrieval score in ``[0, 1]`` for one candidate."""

        z = self.z_score(current_state)
        vector_similarity = self._numeric(result.get("vector_similarity", result.get("score")), 0.0)
        reranker_score = self._numeric(result.get("reranker_score", result.get("rerank_score")), vector_similarity)
        stiffness_s = self._metric(result, "stiffness_s", 0.5)
        reverse_overlap_r = self._metric(result, "reverse_overlap_r", 0.0)
        dissonance_delta = self._metric(result, "dissonance_delta", 0.0)

        relevance = (0.55 * self._clamp01(vector_similarity)) + (0.25 * self._sigmoid(reranker_score))
        stability = (0.12 * self._clamp01(stiffness_s)) + (0.08 * (1.0 - self._clamp01(reverse_overlap_r)))
        systemic_pressure = min(abs(z) / 3.0, 1.0)
        dissonance_penalty = min(abs(dissonance_delta), 1.0) * (0.1 + 0.2 * systemic_pressure)

        # Open leakage admits more exploratory memories by softening the penalty;
        # constriction favors high-stiffness, low-overlap, low-dissonance results.
        mode = self.mode(z)
        if mode == "open-leakage":
            mode_adjustment = 0.08 * (1.0 - self._clamp01(reverse_overlap_r))
            dissonance_penalty *= 0.75
        elif mode == "constricted":
            mode_adjustment = -0.08 * systemic_pressure + 0.08 * self._clamp01(stiffness_s)
            dissonance_penalty *= 1.25
        else:
            mode_adjustment = 0.0

        return self._clamp01(relevance + stability + mode_adjustment - dissonance_penalty)

    def allow(self, result: Mapping[str, Any], current_state: Optional[float] = None) -> bool:
        """Return whether a candidate clears the current leakage threshold."""

        z = self.z_score(current_state)
        threshold = self.minimum_allow_score
        if self.mode(z) == "constricted":
            threshold += min(abs(z) / 10.0, 0.25)
        elif self.mode(z) == "open-leakage":
            threshold = max(0.05, threshold - 0.1)
        return self.score(result, current_state) >= threshold

    def rescore_results(
        self,
        results: Iterable[MutableMapping[str, Any]],
        current_state: Optional[float] = None,
        *,
        filter_disallowed: bool = False,
    ) -> List[MutableMapping[str, Any]]:
        """Attach leakage fields, optionally filter, and sort by gated score."""

        materialized = list(results)
        self.observe_results(materialized)
        z = self.z_score(current_state)
        mode = self.mode(z)
        rescored: List[MutableMapping[str, Any]] = []
        for result in materialized:
            leakage_score = self.score(result, current_state)
            allowed = self.allow(result, current_state)
            result["leakage_score"] = leakage_score
            result["current_z_score"] = z
            result["retrieval_mode"] = mode
            result["allowed_by_leakage_gate"] = allowed
            if allowed or not filter_disallowed:
                rescored.append(result)
        rescored.sort(key=lambda item: item.get("leakage_score", 0.0), reverse=True)
        return rescored

    def stats(self) -> Dict[str, Any]:
        """Expose MCP-friendly gate health statistics."""

        z = self._last_z_score
        return {
            "target_harmonic_state": self.target_harmonic_state,
            "systemic_standard_error": self.systemic_standard_error(),
            "current_z_score": z,
            "retrieval_mode": self.mode(z),
            "window_size": self.window_size,
            "observations": {
                "dissonance": len(self._dissonance),
                "failed_tool_calls": len(self._failed_tool_calls),
                "auditor_conflicts": len(self._auditor_conflicts),
                "retrieval_variance": len(self._retrieval_variance),
            },
            "rolling_means": {
                "dissonance": self._mean(self._dissonance),
                "failed_tool_calls": self._mean(self._failed_tool_calls),
                "auditor_conflicts": self._mean(self._auditor_conflicts),
                "retrieval_variance": self._mean(self._retrieval_variance),
            },
            "last_result_count": self._last_result_count,
        }

    def _append(self, queue: Deque[float], value: Optional[float]) -> None:
        if value is None:
            return
        queue.append(self._numeric(value, 0.0))
        while len(queue) > self.window_size:
            queue.popleft()

    def _standard_error(self, values: Deque[float]) -> float:
        if len(values) < 2:
            return 0.0
        return statistics.pstdev(values) / math.sqrt(len(values))

    def _mean(self, values: Deque[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    def _metric(self, result: Mapping[str, Any], key: str, default: float) -> float:
        metadata = result.get("metadata") if isinstance(result.get("metadata"), Mapping) else {}
        return self._numeric(result.get(key, metadata.get(key, default)), default)

    @staticmethod
    def _numeric(value: Any, default: float) -> float:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return default
        if math.isnan(number) or math.isinf(number):
            return default
        return number

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, value))

    @staticmethod
    def _sigmoid(value: float) -> float:
        return 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, value))))


GLOBAL_LEAKAGE_GATE = ZScoreLeakageGate()
