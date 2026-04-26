# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant Validator for SPLISS Core Mathematics
-------------------------------------------------------------
This script isolates the mathematical core of the SPLISS proposal,
corrects the identified issues, and provides a strict invariant
checker that can be used to enforce the Omega Protocol rules.

Run:
    python3 omega_validator.py
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ----------------------------------------------------------------------
# Constants (Rubric-derived)
# ----------------------------------------------------------------------
EPSILON = 1e-9          # prevents singularity in ln()
XI_N = 0.85             # Newtonian stiffness (Rubric §3)
XI_DELTA = 0.35         # Differential stiffness (Rubric §3)
ASYMMETRY_BOUND_FACTOR = 0.5  # Φ_Δ < 0.5 * Φ_N (Rubric §6)
ENERGY_HEADROOM = 0.20  # 20% headroom required (Invariant 4)
IDENTITY_DRIFT_MAX = 0.01   # 1% drift tolerance (Invariant 3)
TEMPORAL_DRIFT_MAX = 1e-9   # 1 ns tolerance (Invariant 6)
INFORMATION_LOSS_TOL = 0.0  # zero‑loss tolerance (Invariant 5)
CAUSAL_VIOLATION_TOL = 0    # zero tolerance for backward links (Invariant 2)

# ----------------------------------------------------------------------
# Data Structures
# ----------------------------------------------------------------------
@dataclass
class CausalNode:
    node_id: str
    timestamp: float
    causal_links: List[str] = field(default_factory=list)
    topological_charge: complex = complex(1.0, 0.0)
    entropy_state: float = 0.0   # will store coupling ψ at creation

@dataclass
class LatticeState:
    nodes: Dict[str, CausalNode]
    phi_n: float
    phi_delta: float
    metric_determinant: float
    causal_order_valid: bool
    identity_drift: float
    energy_usage: float
    information_loss: float
    temporal_drift: float

# ----------------------------------------------------------------------
# Core Mathematics (corrected)
# ----------------------------------------------------------------------
class RCODELatticeCore:
    """
    Minimal core that computes Φ_N, Φ_Δ, ψ, and related quantities.
    All state‑dependent values are recomputed on demand to avoid stale data.
    """

    def __init__(self):
        self.nodes: Dict[str, CausalNode] = {}
        self.graph: Dict[str, List[str]] = {}

    # ----- Node Management ------------------------------------------------
    def add_node(self, node_id: str, timestamp: float, links: Optional[List[str]] = None) -> CausalNode:
        node = CausalNode(
            node_id=node_id,
            timestamp=timestamp,
            causal_links=links or [],
            topological_charge=complex(1.0, 0.0),
            entropy_state=0.0   # will be set to ψ after insertion
        )
        self.nodes[node_id] = node
        self.graph[node_id] = links or []
        # set entropy_state to current ψ (coupling function)
        node.entropy_state = self._compute_psi()
        return node

    # ----- Φ‑Density Components -------------------------------------------
    def _compute_phi_n(self) -> float:
        """
        Newtonian Fidelity: stability of causal lattice topology.
        Uses a meaningful metric: fraction of nodes that have at least one causal link
        (prevents isolated nodes from degrading fidelity) and average link symmetry.
        """
        if not self.nodes:
            return 1.0

        # Node connectivity: proportion of nodes with >=1 link
        connected = sum(1 for links in self.graph.values() if len(links) > 0)
        conn_ratio = connected / len(self.nodes)

        # Link symmetry: for each link A->B, check if B->A exists (undirected‑like)
        total_links = sum(len(v) for v in self.graph.values())
        symmetric_links = 0
        for src, dsts in self.graph.items():
            for dst in dsts:
                if src in self.graph.get(dst, []):
                    symmetric_links += 1
        # each symmetric pair counted twice, so normalize
        sym_ratio = (symmetric_links / 2) / max(1, total_links / 2)

        # Combine with stiffness (Rubric §3)
        phi_n = XI_N * conn_ratio + (1 - XI_N) * sym_ratio
        return max(phi_n, 0.01)   # keep away from zero for ln()

    def _compute_phi_delta(self) -> float:
        """
        Differential Entropy: Shannon entropy of link distribution,
        normalized and stiffened.
        """
        if len(self.nodes) < 2:
            return 0.0

        link_counts = [len(v) for v in self.graph.values()]
        total = sum(link_counts) + EPSILON
        probs = [c / total for c in link_counts if c > 0]
        entropy = -sum(p * np.log2(p) for p in probs)

        max_entropy = np.log2(len(self.nodes) + 1)
        norm_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        return XI_DELTA * norm_entropy

    def _compute_psi(self) -> float:
        """Coupling function ψ = ln(Φ_N + ε) (Rubric §2)"""
        phi_n = self._compute_phi_n()
        return np.log(phi_n + EPSILON)

    def compute_phi_density(self) -> float:
        """Φ_total = Φ_N + Φ_Δ with asymmetry bound enforcement."""
        phi_n = self._compute_phi_n()
        phi_delta = self._compute_phi_delta()
        bound = ASYMMETRY_BOUND_FACTOR * phi_n
        if phi_delta >= bound:
            phi_delta = (bound - EPSILON)  # stay strictly below bound
        return phi_n + phi_delta

    # ----- Auxiliary Metrics ------------------------------------------------
    def _metric_determinant(self) -> float:
        """
        Spectral metric determinant (TOE Step 4).
        Simplified model: proportional to algebraic connectivity.
        Here we use node count as a proxy; in a real implementation
        this would be the determinant of the Laplacian of the causal graph.
        """
        if not self.nodes:
            return 1.0
        # Avoid zero determinant: use log‑scale to keep positive
        return max(np.log1p(len(self.nodes)), EPSILON)

    def _check_causal_order(self) -> bool:
        """Invariant 2: No backward causal links."""
        for src, dsts in self.graph.items():
            src_time = self.nodes[src].timestamp
            for dst in dsts:
                dst_time = self.nodes[dst].timestamp
                if dst_time < src_time - CAUSAL_VIOLATION_TOL:
                    return False
        return True

    def _identity_drift(self) -> float:
        """Invariant 3: Variance of topological charge magnitude."""
        if len(self.nodes) < 2:
            return 0.0
        magnitudes = [abs(n.topological_charge) for n in self.nodes.values()]
        return float(np.var(magnitudes))

    def _energy_usage(self) -> float:
        """Invariant 4: Normalized resource consumption."""
        # Simplified: linear with node count, capped at 1.0
        return min(len(self.nodes) / 1000.0, 1.0)

    def _information_loss(self) -> float:
        """Invariant 5: Should be zero in an informational‑first system."""
        return 0.0   # placeholder; real implementation would track erasures

    def _temporal_drift(self) -> float:
        """Invariant 6: Spread of timestamps."""
        if len(self.nodes) < 2:
            return 0.0
        times = [n.timestamp for n in self.nodes.values()]
        return float(max(times) - min(times))

    def get_lattice_state(self) -> LatticeState:
        """Export a snapshot for invariant validation."""
        return LatticeState(
            nodes=self.nodes,
            phi_n=self._compute_phi_n(),
            phi_delta=self._compute_phi_delta(),
            metric_determinant=self._metric_determinant(),
            causal_order_valid=self._check_causal_order(),
            identity_drift=self._identity_drift(),
            energy_usage=self._energy_usage(),
            information_loss=self._information_loss(),
            temporal_drift=self._temporal_drift(),
        )

    # ----- Invariant Checker ------------------------------------------------
    def validate_invariants(self, state: LatticeState) -> bool:
        """
        Returns True iff all six Omega Protocol invariants hold.
        Also prints which invariant(s) fail for debugging.
        """
        failures = []

        # 1. Metric Non-Degeneracy: det(M) > exp(-ψ)
        psi = self._compute_psi()
        threshold = np.exp(-psi)
        if state.metric_determinant <= threshold:
            failures.append(
                f"Metric Degeneracy: det={state.metric_determinant:.3e} <= exp(-ψ)={threshold:.3e}"
            )

        # 2. Causal Order Preservation
        if not state.causal_order_valid:
            failures.append("Causal Order Violation: backward link detected")

        # 3. Identity Continuity
        if state.identity_drift > IDENTITY_DRIFT_MAX:
            failures.append(
                f"Identity Drift Exceeded: {state.identity_drift:.3e} > {IDENTITY_DRIFT_MAX}"
            )

        # 4. Energy Envelope
        if state.energy_usage > (1.0 - ENERGY_HEADROOM):
            failures.append(
                f"Energy Envelope Breached: {state.energy_usage:.3e} > {1.0 - ENERGY_HEADROOM:.3e}"
            )

        # 5. Information Conservation
        if state.information_loss > INFORMATION_LOSS_TOL:
            failures.append(
                f"Information Loss: {state.information_loss:.3e} > {INFORMATION_LOSS_TOL}"
            )

        # 6. Temporal Coherence
        if state.temporal_drift > TEMPORAL_DRIFT_MAX:
            failures.append(
                f"Temporal Drift Exceeded: {state.temporal_drift:.3e} > {TEMPORAL_DRIFT_MAX}"
            )

        if failures:
            print("Invariant FAILURES:")
            for f in failures:
                print(" -", f)
            return False
        else:
            print("All Omega Protocol invariants SATISFIED.")
            return True

# ----------------------------------------------------------------------
# Test Suite (exercise edge cases)
# ----------------------------------------------------------------------
def run_tests():
    core = RCODELatticeCore()
    print("=== Test 1: Empty Lattice ===")
    state = core.get_lattice_state()
    assert core.validate_invariants(state) == True

    print("\n=== Test 2: Single Node ===")
    core.add_node("n1", timestamp=0.0)
    state = core.get_lattice_state()
    assert core.validate_invariants(state) == True
    print(f"Φ_N={state.phi_n:.3f}, Φ_Δ={state.phi_delta:.3f}, Φ_total={core.compute_phi_density():.3f}")

    print("\n=== Test 3: Two Nodes, Forward Link ===")
    core.add_node("n2", timestamp=1.0, links=["n1"])
    state = core.get_lattice_state()
    assert core.validate_invariants(state) == True
    print(f"Φ_N={state.phi_n:.3f}, Φ_Δ={state.phi_delta:.3f}, Φ_total={core.compute_phi_density():.3f}")

    print("\n=== Test 4: Introduce Asymmetric Φ_Δ (should clamp) ===")
    # Force high entropy by adding many links to a new node
    for i in range(3, 10):
        core.add_node(f"n{i}", timestamp=float(i), links=[f"n{j}" for j in range(1, i)])
    state = core.get_lattice_state()
    phi_n = state.phi_n
    phi_delta = state.phi_delta
    total = core.compute_phi_density()
    print(f"Φ_N={phi_n:.3f}, Φ_Δ={phi_delta:.3f}, Φ_total={total:.3f}")
    assert phi_delta < 0.5 * phi_n + 1e-12  # allow tiny epsilon slack
    assert core.validate_invariants(state) == True

    print("\n=== Test 5: Simulate Metric Degeneracy (force low determinant) ===")
    # We'll monkey-patch the metric to break the invariant
    original_metric = core._metric_determinant
    core._metric_determinant = lambda: 1e-12  # artificially small
    state = core.get_lattice_state()
    assert core.validate_invariants(state) == False
    core._metric_determinant = original_metric  # restore

    print("\n=== Test 6: Simulate Causal Order Violation ===")
    core.add_node("bad", timestamp=-5.0, links=["n1"])  # backward in time
    state = core.get_lattice_state()
    assert core.validate_invariants(state) == False

    print("\n=== All tests completed ===")

if __name__ == "__main__":
    run_tests()