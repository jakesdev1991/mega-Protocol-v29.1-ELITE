# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Economic Topology Shield (ETS-Ω) invariant validator.
Verifies that the Ω‑invariants (Φ_N, Φ_Δ, J*) are well‑defined
and that the hard constraints (ETI, Φ_N, S_econ) hold.
"""

import numpy as np
import math
from typing import Tuple

# ------------------------------
# Helper functions (economic topology metrics)
# ------------------------------
def compute_entropy(flow_matrix: np.ndarray) -> float:
    """
    S_econ = - Σ_ij p_ij log(p_ij),  p_ij = flow(i->j) / total_flow
    flow_matrix: square matrix of non‑negative token flows.
    """
    total = flow_matrix.sum()
    if total == 0:
        return 0.0
    p = flow_matrix / total
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def compute_betweenness_stub(n_nodes: int) -> float:
    """
    Placeholder: real betweenness requires graph analysis.
    Returns a synthetic value in (0,1] for demo.
    """
    # Simulate a random normalized betweenness max ∈ [0.1, 1.0]
    return np.random.uniform(0.1, 1.0)

def compute_modularity_stub() -> float:
    """
    Placeholder: real modularity ∈ [0,1].
    """
    return np.random.uniform(0.2, 0.9)

def compute_eti(betweenness_max: float, modularity: float, S_econ: float) -> float:
    """
    ETI = (1 / max_betweenness) * modularity * exp(-S_econ)
    """
    if betweenness_max <= 0:
        return 0.0
    return (1.0 / betweenness_max) * modularity * math.exp(-S_econ)

def compute_phi_n_econ(eti: float, phi_n0: float = 1.0,
                       eta1: float = 0.3, eta2: float = 0.2,
                       modularity: float = 0.5, tau: int = 1) -> float:
    """
    Φ_N^(econ)(t) = Φ_N^(0) - η1·(1‑ETI(t‑τ)) + η2·modularity(t‑τ)
    (tau ignored in this static demo)
    """
    return phi_n0 - eta1 * (1.0 - eti) + eta2 * modularity

def compute_phi_delta_econ(eti: float, phi_delta0: float = 0.5,
                           eta3: float = 0.4, eta4: float = 0.3,
                           betweenness_skew: float = 0.0) -> float:
    """
    Φ_Δ^(econ)(t) = Φ_Δ^(0) + η3·betweenness_skew - η4·ETI(t‑τ)
    """
    return phi_delta0 + eta3 * betweenness_skew - eta4 * eti

def compute_psi_econ(phi_n_econ: float, phi_n0: float = 1.0) -> float:
    """
    ψ_econ = ln( Φ_N^(econ) / Φ_N^(0) )
    """
    if phi_n_econ <= 0:
        raise ValueError("Φ_N^(econ) must be positive for log.")
    return math.log(phi_n_econ / phi_n0)

def compute_J_mu(phi_delta_econ: float) -> np.ndarray:
    """
    J^μ = √2 Φ_Δ δ^μ_0  → only time component non‑zero.
    Returns 4‑vector [J^0, J^1, J^2, J^3].
    """
    J = np.zeros(4)
    J[0] = math.sqrt(2.0) * phi_delta_econ
    return J

def compute_A_mu(S_econ: float, dx: float = 1.0) -> np.ndarray:
    """
    A_μ = ∂_μ S_econ.
    In this toy model we approximate gradient by finite difference
    assuming S_econ varies only in time direction.
    """
    A = np.zeros(4)
    A[0] = S_econ / dx  # dS/dt ≈ S/Δt (Δt=dx)
    return A

# ------------------------------
# Validation routine
# ------------------------------
def validate_random_state(num_samples: int = 1000) -> Tuple[int, int]:
    """
    Draws random economic topology data, computes invariants,
    and checks hard constraints.
    Returns (num_valid, num_invalid).
    """
    valid = 0
    invalid = 0
    phi_n0 = 1.0
    phi_delta0 = 0.5

    for _ in range(num_samples):
        # Synthetic flow matrix (5×5)
        n = 5
        flow = np.random.rand(n, n) * 10.0   # arbitrary scale
        # Force some sparsity to mimic realistic topology
        flow[np.random.rand(n, n) > 0.7] = 0.0

        S_econ = compute_entropy(flow)

        betweenness_max = compute_betweenness_stub(n)
        modularity = compute_modularity_stub()
        eti = compute_eti(betweenness_max, modularity, S_econ)

        phi_n = compute_phi_n_econ(eti, phi_n0=phi_n0)
        phi_delta = compute_phi_delta_econ(eti, phi_delta0=phi_delta0)
        psi = compute_psi_econ(phi_n, phi_n0=phi_n0)

        J = compute_J_mu(phi_delta)
        A = compute_A_mu(S_econ)

        # Hard constraints from the MPC‑Ω formulation
        c1 = eti >= 0.6
        c2 = phi_n >= 0.5
        c3 = S_econ >= math.log(2.0)

        if c1 and c2 and c3:
            valid += 1
        else:
            invalid += 1
            # Optional: print first few violations for debugging
            if invalid <= 5:
                print(f"Violation #{invalid}: ETI={eti:.3f} (>=0.6? {c1}), "
                      f"Φ_N={phi_n:.3f} (>=0.5? {c2}), "
                      f"S_econ={S_econ:.3f} (>=ln2? {c3})")

    return valid, invalid

if __name__ == "__main__":
    v, iv = validate_random_state(num_samples=2000)
    print(f"\nValidation over 2000 random states:")
    print(f"  Valid (constraints satisfied): {v}")
    print(f"  Invalid (constraints broken):  {iv}")
    if iv == 0:
        print("✅ All sampled states respect the Ω‑invariants and hard constraints.")
    else:
        print("⚠️  Some states violate constraints – check the economic topology derivation.")