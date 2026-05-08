# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Z-score leakage controls for retrieval and search adapters.

The gate scores candidate records against a baseline distribution and rejects
statistical outliers that look too close to protected prompt, memory, or query
material.  It is intentionally dependency-light so it can run inside Agent Zero
search tools without starting model backends.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from statistics import fmean, pstdev
from typing import Iterable, Sequence

_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")


def _tokenize(text: str) -> set[str]:
    """Normalize text into a coarse lexical set for deterministic scoring."""
    return {token.lower() for token in _TOKEN_PATTERN.findall(text or "") if token}


def lexical_overlap(left: str, right: str) -> float:
    """Return a Jaccard overlap score in ``[0, 1]`` for two text fragments."""
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


@dataclass(frozen=True)
class LeakageDecision:
    """Structured decision returned by :class:`ZScoreLeakageGate`."""

    allowed: bool
    score: float
    z_score: float
    reason: str


@dataclass
class ZScoreLeakageGate:
    """Reject retrieval/search candidates that are anomalous leakage outliers.

    Parameters
    ----------
    z_threshold:
        Maximum positive z-score allowed before a candidate is quarantined.
    absolute_threshold:
        Hard overlap ceiling used even when the baseline distribution has too
        little variance for a meaningful z-score.
    min_baseline:
        Number of baseline values required before z-score blocking is active.
    baseline_scores:
        Optional historical overlap scores seeded by a caller.
    """

    z_threshold: float = 2.5
    absolute_threshold: float = 0.82
    min_baseline: int = 4
    baseline_scores: list[float] = field(default_factory=list)

    def fit(self, protected_text: str, candidates: Iterable[str]) -> "ZScoreLeakageGate":
        """Seed the baseline from candidate overlap with protected text."""
        self.baseline_scores = [lexical_overlap(protected_text, candidate) for candidate in candidates]
        return self

    def update(self, score: float) -> None:
        """Append a bounded score to the rolling baseline."""
        if math.isfinite(score):
            self.baseline_scores.append(max(0.0, min(1.0, float(score))))

    def z_score(self, score: float) -> float:
        """Compute the population z-score for ``score`` against the baseline."""
        if len(self.baseline_scores) < self.min_baseline:
            return 0.0
        deviation = pstdev(self.baseline_scores)
        if deviation <= 1e-12:
            return 0.0
        return (float(score) - fmean(self.baseline_scores)) / deviation

    def evaluate_score(self, score: float) -> LeakageDecision:
        """Evaluate a precomputed leakage score."""
        bounded_score = max(0.0, min(1.0, float(score)))
        z_value = self.z_score(bounded_score)
        if bounded_score >= self.absolute_threshold:
            return LeakageDecision(False, bounded_score, z_value, "absolute-threshold")
        if len(self.baseline_scores) >= self.min_baseline and z_value >= self.z_threshold:
            return LeakageDecision(False, bounded_score, z_value, "z-score-threshold")
        return LeakageDecision(True, bounded_score, z_value, "allowed")

    def evaluate_text(self, protected_text: str, candidate_text: str) -> LeakageDecision:
        """Score text overlap with protected material and return a decision."""
        return self.evaluate_score(lexical_overlap(protected_text, candidate_text))

    def filter_texts(self, protected_text: str, candidates: Sequence[str]) -> list[tuple[str, LeakageDecision]]:
        """Return candidates paired with decisions after fitting a local baseline."""
        local_scores = [lexical_overlap(protected_text, candidate) for candidate in candidates]
        original_baseline = list(self.baseline_scores)
        if len(local_scores) >= self.min_baseline:
            self.baseline_scores = local_scores
        try:
            return [(candidate, self.evaluate_score(score)) for candidate, score in zip(candidates, local_scores)]
        finally:
            self.baseline_scores = original_baseline
