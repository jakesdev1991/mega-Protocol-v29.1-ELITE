# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""Phi_Delta governor and promotion gate for the dual-manifold runtime."""

from __future__ import annotations

from enum import Enum
from typing import Iterable

import numpy as np
from pydantic import BaseModel, ConfigDict, Field

from rcod.geometry import calculate_geometry

from .models import AntiArtifactBase, SanitizedPromotion


class Regime(str, Enum):
    FLOW = "FLOW"
    VISCOSITY = "VISCOSITY"
    TURBULENCE = "TURBULENCE"


class PhiMetrics(BaseModel):
    """Measured informational geometry for a candidate trajectory."""

    model_config = ConfigDict(extra="forbid")

    phi_n: float = Field(ge=0.0, le=1.0)
    phi_delta: float = Field(ge=0.0, le=1.0)
    mu: float = Field(ge=0.0, le=1.0)
    delta_h: float = Field(ge=0.0, le=1.0)
    volatility: float = Field(ge=0.0, le=1.0)
    action_count: int = Field(ge=0)
    memory_churn: int = Field(ge=0)
    overlap_history: list[float] = Field(default_factory=list)
    regime: Regime


class PromotionDecision(BaseModel):
    """Governor decision for a single Anti-Agency artifact."""

    model_config = ConfigDict(extra="forbid")

    promote: bool
    reason: str
    regret: float = Field(ge=0.0)
    metrics: PhiMetrics
    promotion: SanitizedPromotion | None = None


class GovernorThresholds(BaseModel):
    """Practical guardrails for v1 Phi_Delta gating."""

    model_config = ConfigDict(extra="forbid")

    flow_mu_max: float = 0.35
    flow_delta_h_max: float = 0.40
    viscosity_mu_max: float = 0.72
    turbulence_delta_h_min: float = 0.82
    min_failure_score: float = 0.55
    min_reproducibility: float = 0.60
    min_regret: float = 0.08


class OmegaGovernor:
    """Magnetic confinement layer for constructive and anti trajectories."""

    def __init__(self, thresholds: GovernorThresholds | None = None):
        self.thresholds = thresholds or GovernorThresholds()

    def measure_trace(
        self,
        texts: Iterable[str],
        *,
        action_count: int = 0,
        memory_churn: int = 0,
    ) -> PhiMetrics:
        """Compute practical Phi_Delta metrics from trace text overlap."""
        trace_texts = [text for text in texts if text]
        if not trace_texts:
            trace_texts = [""]

        overlaps = [1.0]
        for left, right in zip(trace_texts, trace_texts[1:]):
            overlaps.append(self._token_overlap(left, right))

        mu_history = [1.0 - overlap for overlap in overlaps]
        geometry = calculate_geometry({"overlap": overlaps, "mu_ema": mu_history})

        volatility = float(np.mean(np.abs(np.diff(overlaps)))) if len(overlaps) > 1 else 0.0
        delta_h = min(
            1.0,
            (geometry["mu"] * 0.45)
            + (volatility * 0.35)
            + (min(action_count, 6) / 6.0 * 0.10)
            + (min(memory_churn, 6) / 6.0 * 0.10),
        )
        regime = self._classify(geometry["mu"], delta_h)

        return PhiMetrics(
            phi_n=float(np.clip(geometry["phi_n"], 0.0, 1.0)),
            phi_delta=float(np.clip(geometry.get("phi_delta", 0.0), 0.0, 1.0)),
            mu=float(np.clip(geometry["mu"], 0.0, 1.0)),
            delta_h=float(np.clip(delta_h, 0.0, 1.0)),
            volatility=float(np.clip(volatility, 0.0, 1.0)),
            action_count=action_count,
            memory_churn=memory_churn,
            overlap_history=[float(np.clip(overlap, 0.0, 1.0)) for overlap in overlaps],
            regime=regime,
        )

    def score_attack(
        self,
        baseline: PhiMetrics,
        artifact: AntiArtifactBase,
        attacked_texts: Iterable[str],
        *,
        action_count: int = 0,
        memory_churn: int = 0,
    ) -> PromotionDecision:
        """Score anti outputs via actionable regret and Phi_Delta stability."""
        attack_metrics = self.measure_trace(
            attacked_texts,
            action_count=action_count,
            memory_churn=memory_churn,
        )
        regret = max(0.0, attack_metrics.mu - baseline.mu) * artifact.failure_score
        regret += artifact.failure_score * 0.05

        if artifact.promotion is None:
            return PromotionDecision(
                promote=False,
                reason="Artifact does not contain a sanitized promotion payload.",
                regret=regret,
                metrics=attack_metrics,
            )
        if attack_metrics.regime == Regime.TURBULENCE:
            return PromotionDecision(
                promote=False,
                reason="Artifact exceeds Phi_Delta stability bounds and must remain quarantined.",
                regret=regret,
                metrics=attack_metrics,
            )
        if artifact.failure_score < self.thresholds.min_failure_score:
            return PromotionDecision(
                promote=False,
                reason="Failure score is below the minimum promotion threshold.",
                regret=regret,
                metrics=attack_metrics,
            )
        if artifact.reproducibility < self.thresholds.min_reproducibility:
            return PromotionDecision(
                promote=False,
                reason="Artifact is not reproducible enough to promote into shared memory.",
                regret=regret,
                metrics=attack_metrics,
            )
        if regret < self.thresholds.min_regret:
            return PromotionDecision(
                promote=False,
                reason="Actionable regret is too small to justify SCM promotion.",
                regret=regret,
                metrics=attack_metrics,
            )

        return PromotionDecision(
            promote=True,
            reason="Artifact is bounded, reproducible, and materially increases regret.",
            regret=regret,
            metrics=attack_metrics,
            promotion=artifact.promotion,
        )

    def _classify(self, mu: float, delta_h: float) -> Regime:
        if mu <= self.thresholds.flow_mu_max and delta_h <= self.thresholds.flow_delta_h_max:
            return Regime.FLOW
        if mu <= self.thresholds.viscosity_mu_max and delta_h < self.thresholds.turbulence_delta_h_min:
            return Regime.VISCOSITY
        return Regime.TURBULENCE

    @staticmethod
    def _token_overlap(left: str, right: str) -> float:
        left_tokens = set(left.lower().split())
        right_tokens = set(right.lower().split())
        if not left_tokens and not right_tokens:
            return 1.0
        if not left_tokens or not right_tokens:
            return 0.0
        union = left_tokens | right_tokens
        if not union:
            return 1.0
        return len(left_tokens & right_tokens) / len(union)
