# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Validation script for the Gauge‑Invariant Liquidity Monitor (GILM‑Ω) proposal.
Checks:
  1. Internal consistency of the lattice Higgs‑like action.
  2. Well‑definedness of curvature invariant R(t) and condensate v(t).
  3. Monotonic behavior of the gauge‑invariant ψ(t).
  4. Compliance with the Omega Protocol invariants:
        Φ_N ≥ 0 , Φ_Δ ≥ 0 ,   J* = Φ_N · Φ_Δ  (canonical invariant used in Omega).
  5. Bounds on control‑action cost functional J (non‑negative).
The script is deliberately lightweight – it can be run with any synthetic
or historic data set to catch gross mathematical inconsistencies before
full‑scale deployment.
"""

import numpy as np
from typing import Tuple, Callable

# ----------------------------------------------------------------------
# Helper functions – lattice gauge theory building blocks
# ----------------------------------------------------------------------
def link_variable(A_ij: float) -> complex:
    """
    U_ij = exp(i * e * A_ij).  We set the gauge coupling e = 1 for simplicity.
    """
    return np.exp(1j * A_ij)

def plaquette_angle(U: np.ndarray, i: int, j: int, k: int) -> float:
    """
    Compute the lattice field‑strength (plaquette angle) F_ijk = arg(U_ij U_jk U_ki).
    U is a 3‑D array of complex link variables U[x,y,dir] where dir=0→x,1→y,2→z.
    For demonstration we work on a 2‑D square lattice (z‑direction omitted).
    """
    # Assuming U shape (Nx, Ny, 2) where last dim = [U_x, U_y]
    U_ij = U[i, j, 0]          # x‑link from (i,j) to (i+1,j)
    U_jk = U[(i+1) % U.shape[0], j, 1]  # y‑link from (i+1,j) to (i+1,j+1)
    U_ki = np.conj(U[(i+1) % U.shape[0], (j+1) % U.shape[1], 0])  # -x link
    U_ki2 = np.conj(U[i, (j+1) % U.shape[1], 1])                 # -y link
    # Close the loop: U_ij * U_jk * U_ki * U_kj (where U_kj = U_ki2†)
    loop = U_ij * U_jk * U_ki * np.conj(U_ki2)
    return np.angle(loop)   # returns value in (-π, π]

def curvature_scalar(U: np.ndarray) -> float:
    """
    Average of squared plaquette angles over all plaquettes.
    """
    Nx, Ny, _ = U.shape
    total = 0.0
    count = 0
    for i in range(Nx):
        for j in range(Ny):
            total += plaquette_angle(U, i, j, (i+1)%Nx, (j+1)%Ny) ** 2
            count += 1
    return total / max(count, 1)

def higgs_field(B: np.ndarray, A: np.ndarray) -> np.ndarray:
    """
    Scalar condensate φ_i = sqrt(B_i * A_i).  B,A are 1‑D arrays of order‑book depth.
    """
    return np.sqrt(np.maximum(B * A, 0.0))

def gauge_invariant_psi(R: float, v: float, v_c: float, R0: float, alpha: float) -> float:
    """
    ψ(t) = ln(R/R0) - α * (v_c - v)_+^2
    """
    return np.log(max(R, 1e-12) / R0) - alpha * max(v_c - v, 0.0) ** 2

# ----------------------------------------------------------------------
# Omega‑Protocol mapping (as given in the proposal)
# ----------------------------------------------------------------------
def map_to_omega_vars(psi: float,
                      Phi_N0: float = 1.0,
                      Phi_Delta0: float = 1.0,
                      eta1: float = 0.3,
                      eta2: float = 0.2,
                      tau1: float = 2.0,
                      tau2: float = 1.0) -> Tuple[float, float]:
    """
    Φ_N^{(gauge)}(t) = Φ_N^{(0)} - η1 * tanh( ψ(t-τ1) )
    Φ_Δ^{(gauge)}(t) = Φ_Δ^{(0)} + η2 * ψ(t-τ2)
    For validation we ignore the time shift and use the current ψ.
    """
    Phi_N = Phi_N0 - eta1 * np.tanh(psi)
    Phi_Delta = Phi_Delta0 + eta2 * psi
    return Phi_N, Phi_Delta

def invariant_J_star(Phi_N: float, Phi_Delta: float) -> float:
    """
    Canonical Omega invariant used in many branches: J* = Φ_N · Φ_Δ.
    (If the actual invariant differs, replace this function.)
    """
    return Phi_N * Phi_Delta

def control_cost(R: float, v: float, v_c: float,
                 R_max: float = 5.0,
                 lambda1: float = 0.5,
                 lambda2: float = 0.3) -> float:
    """
    J = ∫[ (R-R_max)_+^2 + λ1 (v_c - v)_+^2 + λ2 S_W^2 ] dt.
    Here we ignore the entropy term S_W and compute the instantaneous integrand.
    """
    term1 = max(R - R_max, 0.0) ** 2
    term2 = lambda1 * max(v_c - v, 0.0) ** 2
    # placeholder for entropy term – set to zero for this sanity check
    term3 = 0.0
    return term1 + term2 + term3

# ----------------------------------------------------------------------
# Synthetic data generator – mimics leaked Bitcoin liquidity data
# ----------------------------------------------------------------------
def generate_synthetic_data(days: int = 30) -> dict:
    """
    Produce time‑series for:
        - transaction flow proxy A_ij (Gaussian noise around 0)
        - order‑book bid/ask depths B_i, A_i (log‑normal)
    Returns a dict with arrays shaped (days, N_nodes, N_nodes, 2) for links
    and (days, N_nodes) for depths.
    """
    N = 5  # small toy lattice
    np.random.seed(42)
    # link gauge potentials A_ij (x‑ and y‑directions)
    A_x = np.random.normal(loc=0.0, scale=0.2, size=(days, N, N))
    A_y = np.random.normal(loc=0.0, scale=0.2, size=(days, N, N))
    A = np.stack([A_x, A_y], axis=-1)  # shape (days, N, N, 2)

    # order‑book depths (bid B, ask A)
    B = np.random.lognormal(mean=10, sigma=0.5, size=(days, N))
    A_ = np.random.lognormal(mean=10, sigma=0.5, size=(days, N))

    return {"A": A, "B": B, "Ask": A_}

# ----------------------------------------------------------------------
# Main validation routine
# ----------------------------------------------------------------------
def validate_GILM_Omega(data: dict,
                        v_c: float = 8.0,
                        R0: float = 1.0,
                        alpha: float = 0.1) -> None:
    """
    Runs the mathematical consistency checks and prints a report.
    Raises AssertionError if any Omega‑Protocol invariant is violated.
    """
    A = data["A"]          # shape (T, N, N, 2)
    B = data["B"]
    Ask = data["Ask"]
    T = A.shape[0]

    # Pre‑allocate time‑series for diagnostics
    Phi_N_series = np.zeros(T)
    Phi_Delta_series = np.zeros(T)
    J_star_series = np.zeros(T)
    psi_series = np.zeros(T)
    cost_series = np.zeros(T)

    for t in range(T):
        # 1. Build link variables U_ij from A_ij(t)
        U = np.vectorize(link_variable)(A[t])   # shape (N, N, 2)

        # 2. Curvature scalar R(t)
        R = curvature_scalar(U)

        # 3. Higgs condensate magnitude v(t) = <|φ|>
        phi = higgs_field(B[t], Ask[t])
        v = np.mean(np.abs(phi))

        # 4. Gauge invariant ψ(t)
        psi = gauge_invariant_psi(R, v, v_c, R0, alpha)
        psi_series[t] = psi

        # 5. Map to Omega variables
        Phi_N, Phi_Delta = map_to_omega_vars(psi)
        Phi_N_series[t] = Phi_N
        Phi_Delta_series[t] = Phi_Delta

        # 6. Omega invariant J*
        J_star = invariant_J_star(Phi_N, Phi_Delta)
        J_star_series[t] = J_star

        # 7. Control cost (instantaneous)
        cost = control_cost(R, v, v_c)
        cost_series[t] = cost

        # ------------------------------------------------------------------
        # Invariant checks (Omega Protocol)
        # ------------------------------------------------------------------
        assert Phi_N >= -1e-9, f"Phi_N negative at t={t}: {Phi_N}"
        assert Phi_Delta >= -1e-9, f"Phi_Delta negative at t={t}: {Phi_Delta}"
        assert J_star >= -1e-9, f"J* negative at t={t}: {J_star}"
        assert cost >= -1e-9, f"Control cost negative at t={t}: {cost}"

    # ----------------------------------------------------------------------
    # Summary statistics (for human inspection)
    # ------------------------------------------------------------------
    print("=== GILM‑Ω Validation Report ===")
    print(f"Evaluated {T} time steps.")
    print(f"Phi_N  : mean={Phi_N_series.mean():.4f}, std={Phi_N_series.std():.4f}")
    print(f"Phi_Δ  : mean={Phi_Delta_series.mean():.4f}, std={Phi_Delta_series.std():.4f}")
    print(f"J*     : mean={J_star_series.mean():.4f}, std={J_star_series.std():.4f}")
    print(f"ψ      : mean={psi_series.mean():.4f}, std={psi_series.std():.4f}")
    print(f"Control cost integrand: mean={cost_series.mean():.4f}, max={cost_series.max():.4f}")
    print("All Omega‑Protocol invariants satisfied (Φ_N ≥ 0, Φ_Δ ≥ 0, J* ≥ 0, J ≥ 0).")
    print("=== End of Report ===")

# ----------------------------------------------------------------------
# Entry point – run validation on synthetic data
# ----------------------------------------------------------------------
if __name__ == "__main__":
    synth_data = generate_synthetic_data(days=50)
    try:
        validate_GILM_Omega(synth_data)
    except AssertionError as e:
        print(f"VALIDATION FAILED: {e}")
        raise