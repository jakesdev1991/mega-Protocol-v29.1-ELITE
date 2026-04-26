# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for QULN‑like subsystems.
Implements checks for:
    Φ-1: Causal Fidelity   (no superluminal decision propagation)
    Φ-2: Informational Mass Conservation (entropy increase ≤5%)
    Φ-3: Topological Integrity (route manifold simply‑connected → necessary for S³)
Author: Agent Smith (Omega Protocol Guardian)
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np
import networkx as nx

# ----------------------------------------------------------------------
# Exception definitions
# ----------------------------------------------------------------------
class OmegaViolation(RuntimeError):
    """Raised when an Omega Protocol invariant is violated."""
    pass

# ----------------------------------------------------------------------
# Data structures
# ----------------------------------------------------------------------
@dataclass
class DecisionEvent:
    """A logistics decision with timestamp and spatial origin."""
    t: float          # decision time (normalized units)
    x: Tuple[float, float, float]  # origin coordinates (x,y,z)
    info: str         # payload description (for debugging)

@dataclass
class LogisticsTick:
    """State snapshot for one simulation tick."""
    decisions: List[DecisionEvent]
    entropy: float    # current informational entropy (bits)
    route_graph: nx.Graph  # undirected graph of active routes (nodes = waypoints)

# ----------------------------------------------------------------------
# Validator core
# ----------------------------------------------------------------------
class OmegaValidator:
    def __init__(self,
                 c_local: float = 1.0,
                 entropy_budget: float = 0.05,
                 max_entropy_history: int = 100):
        """
        Parameters
        ----------
        c_local : float
            Local speed of causal influence (normalized to 1).
        entropy_budget : float
            Allowed fractional entropy increase per tick (Φ-2).
        max_entropy_history : int
            How many past entropy samples to keep for drift detection.
        """
        self.c_local = c_local
        self.entropy_budget = entropy_budget
        self.entropy_history: List[float] = []
        self.max_entropy_history = max_entropy_history
        self._last_entropy: float = 0.0

    # ------------------------------------------------------------------
    # Φ-1: Causal Fidelity
    # ------------------------------------------------------------------
    def check_causal_fidelity(self, tick: LogisticsTick) -> None:
        """Ensure no decision influences another outside its future light‑cone."""
        for i, d1 in enumerate(tick.decisions):
            for d2 in tick.decisions[i+1:]:
                dt = abs(d2.t - d1.t)
                dx = np.linalg.norm(np.array(d2.x) - np.array(d1.x))
                # If Δt < distance / c_local → superluminal influence
                if dt < dx / self.c_local - 1e-9:   # tiny epsilon for FP noise
                    raise OmegaViolation(
                        f"Φ-1 violation: decision {d1.info} at ({d1.t},{d1.x}) "
                        f"influences {d2.info} at ({d2.t},{d2.x}) "
                        f"(Δt={dt:.3f}, dx={dx:.3f}, c_local={self.c_local})"
                    )

    # ------------------------------------------------------------------
    # Φ-2: Informational Mass Conservation
    # ------------------------------------------------------------------
    def check_entropy_conservation(self, tick: LogisticsTick) -> None:
        """Entropy may not grow more than budget * previous entropy."""
        if self._last_entropy == 0.0:
            # First tick – just record
            self._last_entropy = tick.entropy
            self.entropy_history.append(tick.entropy)
            return

        delta = tick.entropy - self._last_entropy
        allowed = self.entropy_budget * self._last_entropy
        if delta > allowed + 1e-12:
            raise OmegaViolation(
                f"Φ-2 violation: entropy increase {delta:.6f} > budget {allowed:.6f} "
                f"(current H={tick.entropy:.6f}, prior H={self._last_entropy:.6f})"
            )
        # Update history
        self._last_entropy = tick.entropy
        self.entropy_history.append(tick.entropy)
        if len(self.entropy_history) > self.max_entropy_history:
            self.entropy_history.pop(0)

    # ------------------------------------------------------------------
    # Φ-3: Topological Integrity (simply‑connected → necessary for S³)
    # ------------------------------------------------------------------
    def check_topological_integrity(self, tick: LogisticsTick) -> None:
        """The route manifold must have trivial π₁ (no non‑contractible loops)."""
        G = tick.route_graph
        if not nx.is_connected(G):
            raise OmegaViolation(
                "Φ-3 violation: route graph is disconnected → non‑trivial π₀"
            )
        # Compute a spanning tree and count independent cycles
        # For an undirected graph, cyclomatic number = E - V + C
        cycles = G.number_of_edges() - G.number_of_vertices() + nx.number_connected_components(G)
        if cycles > 0:
            raise OmegaViolation(
                f"Φ-3 violation: route graph contains {cycles} independent cycle(s) "
                f"(non‑trivial π₁ → cannot be homotopy‑equivalent to S³)"
            )

    # ------------------------------------------------------------------
    # Full tick validation
    # ------------------------------------------------------------------
    def validate_tick(self, tick: LogisticsTick) -> None:
        """Run all three checks; raises OmegaViolation on first failure."""
        self.check_causal_fidelity(tick)
        self.check_entropy_conservation(tick)
        self.check_topological_integrity(tick)

# ----------------------------------------------------------------------
# Example usage (would be integrated into the subsystem's main loop)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    validator = OmegaValidator(c_local=1.0, entropy_budget=0.05)

    # Mock a single tick that *should* pass
    G_pass = nx.Graph()
    G_pass.add_edges_from([(0,1),(1,2),(2,3),(3,0)])  # a simple cycle → will FAIL Φ-3
    tick_ok = LogisticsTick(
        decisions=[
            DecisionEvent(t=0.0, x=(0,0,0), info="assign drone A"),
            DecisionEvent(t=0.5, x=(0.1,0,0), info="re‑route drone B")
        ],
        entropy=10.0,
        route_graph=G_pass
    )

    try:
        validator.validate_tick(tick_ok)
        print("Tick PASSED all Omega invariants.")
    except OmegaViolation as e:
        print(f"Omega Violation: {e}")

    # Mock a tick that violates Φ-1 (superluminal decision)
    tick_bad = LogisticsTick(
        decisions=[
            DecisionEvent(t=0.0, x=(0,0,0), info="early decision"),
            DecisionEvent(t=0.1, x=(1.0,0,0), info="far‑away decision")  # dx=1, dt=0.1 > c_local? actually dt < dx => violation
        ],
        entropy=10.0,
        route_graph=nx.Graph()
    )
    try:
        validator.validate_tick(tick_bad)
    except OmegaViolation as e:
        print(f"Expected Φ-1 catch: {e}")