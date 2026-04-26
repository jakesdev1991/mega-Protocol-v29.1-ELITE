# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for Bureaucratic Decision Manifold (v26.0)
-----------------------------------------------------------------
This script audits the mathematical soundness of the specification
and enforces the Omega Protocol invariants:
    - Psi_id (Goal Integrity)   >= PSI_ID_THRESHOLD
    - H_top (Topological Impedance) in [0, 1]
    - Phi_N (Net Phi-density)   >= 0
    - J_star (Jacobian approx.) >= J_STAR_MIN
    - No Procedural Black Hole without triggering Geodesic Smoothing
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple

# ----------------------------------------------------------------------
# Protocol Constants (as per the C++ spec, but with corrected invariants)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95          # Goal Integrity hard gate
COD_THRESHOLD    = 0.80          # Minimum alignment for stability
XI_BOUND_DEFAULT = 1.5
XI_BOUND_MAX     = 3.0
XI_BOUND_MIN     = 0.5
H_TOP_LIMIT      = 0.85
LAMBDA_COUPLING  = 1.0
J_STAR_MIN       = 0.7          # Example protocol-defined minimum Jacobian

# ----------------------------------------------------------------------
# Data Structures
# ----------------------------------------------------------------------
@dataclass
class DecisionNode:
    approval_cost: float      # ∈ [0,1]
    risk_variance: float      # ∈ [0,1]
    node_id: str = ""

@dataclass
class DecisionPath:
    nodes: List[DecisionNode] = field(default_factory=list)
    intent: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0]))
    outcome: np.ndarray = field(default_factory=lambda: np.array([1.0, 0.0]))
    xi_bound: float = XI_BOUND_DEFAULT

    # ------------------------------------------------------------------
    # Core Computations
    # ------------------------------------------------------------------
    def topological_impedance(self) -> float:
        """H_top = Σ(cost_i * var_i) / Σ(cost_i)  (dimensionless, clamped)."""
        num = sum(n.approval_cost * n.risk_variance for n in self.nodes)
        den = sum(n.approval_cost for n in self.nodes)
        if den == 0.0:
            return 0.0
        raw = num / den
        return float(np.clip(raw, 0.0, 1.0))

    def fidelity(self) -> float:
        """|<intent|outcome>| (dimensionless)."""
        dot = np.dot(self.intent, self.outcome)
        norm = np.linalg.norm(self.intent) * np.linalg.norm(self.outcome)
        return float(np.abs(dot) / norm) if norm > 0 else 0.0

    def cod(self) -> float:
        """COD = fidelity * exp(-Lambda * H_top)."""
        return self.fidelity() * np.exp(-LAMBDA_COUPLING * self.topological_impedance())

    def psi_id(self) -> float:
        """
        Goal Integrity: we approximate it as the *undamped* fidelity,
        i.e., alignment before entropic damping.
        """
        return self.fidelity()

    def jacobian_approx(self) -> float:
        """
        Crude Jacobian determinant for a discrete path:
        product of local transition scalars (cost_i) normalized.
        For a more rigorous treatment one would build Jacobians of each node's
        state‑transition map; here we use cost as a proxy for local stretching.
        """
        if not self.nodes:
            return 1.0
        prod = np.prod([n.approval_cost for n in self.nodes])
        # Normalize by path length to keep dimensionless and bounded
        return float(np.clip(prod ** (1.0 / len(self.nodes)), 0.0, 1.0))

    def procedural_black_hole(self) -> Tuple[bool, str]:
        """Return (True, reason) if BH condition holds."""
        H = self.topological_impedance()
        X = self.xi_bound
        if H > H_TOP_LIMIT and X > 0.9 * XI_BOUND_MAX:
            return True, f"H_top={H:.3f} > {H_TOP_LIMIT} and Xi_bound={X:.3f} > {0.9*XI_BOUND_MAX:.3f}"
        return False, ""

    # ------------------------------------------------------------------
    # Geodesic Smoothing Operator (curvature reduction)
    # ------------------------------------------------------------------
    def geodesic_smoothing(self) -> None:
        """
        Prune high‑curvature nodes while preserving Psi_id.
        This is a simplified deterministic version for validation.
        """
        # Compute current state
        H_before = self.topological_impedance()
        psi_before = self.psi_id()
        cod_before = self.cod()

        # Early exit if already stable
        if cod_before >= COD_THRESHOLD and not self.procedural_black_hole()[0]:
            return

        # Identify nodes sorted by curvature contribution (cost*var)
        curvature = [(i, n.approval_cost * n.risk_variance) for i, n in enumerate(self.nodes)]
        curvature.sort(key=lambda x: x[1], reverse=True)

        # Prune loop
        removed_any = False
        for idx, _ in curvature:
            # Simulate removal
            trial_nodes = self.nodes[:idx] + self.nodes[idx+1:]
            trial_path = DecisionPath(
                nodes=trial_nodes,
                intent=self.intent.copy(),
                outcome=self.outcome.copy(),
                xi_bound=self.xi_bound
            )
            # Hard gate on Goal Integrity (Psi_id)
            if trial_path.psi_id() < PSI_ID_THRESHOLD:
                # Cannot remove this node without breaking integrity
                break
            # Actually remove
            self.nodes.pop(idx)
            removed_any = True
            # Re‑evaluate stop conditions
            if self.topological_impedance() <= 0.9 * H_TOP_LIMIT and self.psi_id() >= PSI_ID_THRESHOLD:
                break

        if removed_any:
            # Update outcome to reflect pruning (simple model: shift toward intent)
            shift = 0.03 * len(self.nodes)  # small intentional pull
            self.outcome = np.clip(self.outcome + shift * (self.intent - self.outcome), 0.0, 1.0)
            # Modulate stiffness
            if self.topological_impedance() < 0.5 * H_TOP_LIMIT:
                self.xi_bound = min(XI_BOUND_MAX, self.xi_bound * 1.05)

        # Final assertions (will raise if violated)
        self._assert_invariants()

    # ------------------------------------------------------------------
    # Invariant Assertions (Omega Protocol)
    # ------------------------------------------------------------------
    def _assert_invariants(self) -> None:
        """Raise AssertionError if any Omega invariant is violated."""
        # 1. Goal Integrity
        assert self.psi_id() >= PSI_ID_THRESHOLD, \
            f"Goal Integrity violated: psi_id={self.psi_id():.3f} < {PSI_ID_THRESHOLD}"

        # 2. Topological Impedance bounds
        H = self.topological_impedance()
        assert 0.0 <= H <= 1.0, \
            f"H_top out of [0,1]: {H:.3f}"

        # 3. Phi_N (Net Phi-density) – define as fidelity - H_top - penalty for stiffness
        #    (simple linear combination; can be replaced with protocol‑specific formula)
        phi_n = self.fidelity() - H - 0.1 * max(0.0, self.xi_bound - XI_BOUND_DEFAULT)
        assert phi_n >= -1e-9, \
            f"Net Phi-density negative: phi_n={phi_n:.3f}"

        # 4. J_star (Jacobian approx.) – must stay above protocol minimum
        j_star = self.jacobian_approx()
        assert j_star >= J_STAR_MIN, \
            f"Jacobian below minimum: j_star={j_star:.3f} < {J_STAR_MIN}"

        # 5. Procedural Black Hole must be resolved by smoothing
        in_bh, reason = self.procedural_black_hole()
        assert not in_bh, \
            f"Procedural Black Hole detected after smoothing: {reason}"

    # ------------------------------------------------------------------
    # Monitoring (optional)
    # ------------------------------------------------------------------
    def monitor_phi_density(self, throughput: float = 1.0) -> float:
        """Compute Phi_Net = Throughput - Impedance_Cost - Risk_Leak."""
        impedance_cost = self.topological_impedance()
        risk_leak = sum(n.risk_variance for n in self.nodes) / max(1, len(self.nodes))
        phi_net = throughput - impedance_cost - risk_leak
        if phi_net < 0.0:
            print(f"[WARN] Negative Phi-Density: {phi_net:.3f}")
        return phi_net

# ----------------------------------------------------------------------
# Test Harness
# ----------------------------------------------------------------------
def run_validation_suite(num_trials: int = 1000) -> None:
    """Generate random decision paths and enforce Omega invariants."""
    np.random.seed(42)
    for trial in range(num_trials):
        # Random path length 2‑8
        length = np.random.randint(2, 9)
        nodes = []
        for i in range(length):
            cost = np.random.rand()          # [0,1]
            var  = np.random.rand()          # [0,1]
            nodes.append(DecisionNode(cost, var, f"N{i}"))
        # Random intent/outcome vectors (2‑D for simplicity)
        intent = np.random.rand(2)
        outcome = np.random.rand(2)
        # Normalize to unit length for fidelity stability
        intent = intent / np.linalg.norm(intent)
        outcome = outcome / np.linalg.norm(outcome)
        xi = np.random.uniform(XI_BOUND_MIN, XI_BOUND_MAX)

        path = DecisionPath(nodes=nodes,
                            intent=intent.copy(),
                            outcome=outcome.copy(),
                            xi_bound=xi)

        # Run the smoothing operator (which internally asserts invariants)
        try:
            path.geodesic_smoothing()
        except AssertionError as e:
            print(f"\n[Trial {trial}] INVARIANT VIOLATION:")
            print(f"  Path: {[ (n.approval_cost, n.risk_variance) for n in path.nodes ]}")
            print(f"  Intent: {path.intent}, Outcome: {path.outcome}")
            print(f"  Xi_bound: {path.xi_bound:.3f}")
            print(f"  Error: {e}")
            raise  # Fail fast – Omega Protocol demands zero tolerance

        # Optional: monitor Phi density
        phi = path.monitor_phi_density()
        if phi < 0.0:
            print(f"[Trial {trial}] Phi_Net negative but not fatal: {phi:.3f}")

    print(f"\n✅ All {num_trials} trials passed Omega Protocol validation.")

if __name__ == "__main__":
    run_validation_suite()