# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
Omega Protocol Invariant Validator for Gauge‑Invariant Liquidity Monitor (GILM‑Ω)

Checks:
    • Link unitarity: |U_ij| == 1
    • Plaquette angle real and curvature scalar R >= 0
    • Higgs magnitude v >= 0
    • Gauge invariant psi real
    • Phi_N, Phi_Delta remain non‑negative
    • Control constraints: R <= R_max, v >= v_c, entropy S_W <= S_W_max
"""

import numpy as np
from numpy.linalg import norm

# ------------------- USER‑CONFIGURABLE PARAMETERS -------------------
# Lattice size (example: 4x4 periodic grid)
L = 4
N = L * L                     # number of nodes
# Physical / model parameters (must be >0 unless noted)
e      = 1.0                  # gauge coupling
beta   = 1.0                  # gauge term weight
kappa  = 0.5                  # Higgs mass term
lam    = 0.1                  # Higgs self‑interaction
PhiN0  = 1.0                  # baseline Phi_N
PhiD0  = 1.0                  # baseline Phi_Delta
eta1   = 0.3                  # Phi_N sensitivity
eta2   = 0.2                  # Phi_Delta sensitivity
tau1   = 2.0                  # days lead for Phi_N
tau2   = 1.0                  # days lead for Phi_Delta
alpha  = 0.5                  # psi weighting
v_c    = 0.2                  # critical condensate
R0     = 1.0                  # reference curvature
R_max  = 5.0                  # max allowed curvature
S_W_max= 2.0                  # max Wilson‑loop entropy
# -------------------------------------------------------------------

def idx(i, j):
    """Map 2D coordinates to linear index with periodic BC."""
    return (i % L) * L + (j % L)

def reconstruct_links(J, B, A, tau):
    """
    Build link variables U_ij from transaction flow J_ij,
    order‑book depths B_i, A_i and latency tau_ij.
    Returns:
        U: dict {(i,j): complex link}
        phi: array of Higgs magnitudes per node
    """
    U = {}
    phi = np.sqrt(B * A)               # Higgs field magnitude
    # Simple linear mapping: A_ij proportional to net flow / latency
    for i in range(N):
        for j in range(N):
            if i == j: continue
            # net flow from i to j (could be asymmetric)
            flow = J[i, j] - J[j, i]
            lat  = tau[i, j] if tau[i, j] > 0 else 1.0
            A_ij = e * flow / lat       # discrete gauge connection (real)
            U[(i, j)] = np.exp(1j * A_ij)   # unitary link
    return U, phi

def plaquette_angle(U, i, j):
    """
    Compute oriented plaquette angle in the +x,+y direction
    starting at node (i,j). Returns scalar angle in (-pi,pi].
    """
    # coordinates
    x, y = divmod(i, L)
    # neighbours
    right = idx(x, (y+1)%L)
    up    = idx((x+1)%L, y)
    diag  = idx((x+1)%L, (y+1)%L)

    U1 = U.get((i, right), 1.0)          # i -> i+dx
    U2 = U.get((right, up),   1.0)       # i+dx -> i+dx+dy
    U3 = U.get((up,   diag),  np.conj(U.get((diag, right), 1.0)))  # i+dx+dy -> i+dy (reverse)
    U4 = U.get((diag, i),     np.conj(U.get((i, up), 1.0)))       # i+dy -> i (reverse)

    prod = U1 * U2 * U3 * U4
    angle = np.angle(prod)               # in (-pi,pi]
    return angle

def curvature_scalar(U):
    """Average of squared plaquette angles over all elementary plaquettes."""
    angles = []
    for i in range(N):
        angles.append(plaquette_angle(U, i, (i+1)%N))  # simple 1D proxy; replace with 2D if needed
    R = np.mean(np.array(angles)**2)
    return R

def wilson_loop_entropy(U):
    """
    Compute Shannon entropy of Wilson loop traces for all elementary squares.
    Returns entropy in bits.
    """
    traces = []
    for i in range(N):
        angle = plaquette_angle(U, i, (i+1)%N)
        W = np.exp(1j * angle)          # Wilson loop = e^{iF}
        traces.append(np.abs(W))        # |W| = 1 for perfect unitarity; deviation indicates disorder
    # Normalize to a probability distribution
    p = np.array(traces)
    p = p / p.sum() if p.sum() > 0 else np.ones_like(p)/len(p)
    # Shannon entropy
    S = -np.sum(p * np.log2(p + 1e-12))
    return S

def compute_psi(R, v):
    """Gauge‑invariant early‑warning signal."""
    return np.log(R / R0) - alpha * np.max([v_c - v, 0])**2

def compute_phi(psi, t):
    """Map psi to Omega invariants with lead times."""
    PhiN = PhiN0 - eta1 * np.tanh(psi - tau1)   # note: psi already evaluated at t‑tau1 inside caller
    PhiD = PhiD0 + eta2 * (psi - tau2)
    return PhiN, PhiD

def validate_step(t, J, B, A, tau):
    """Run all invariant checks for a single time‑step."""
    U, phi = reconstruct_links(J, B, A, tau)
    # 1. Link unitarity
    for (i, j), val in U.items():
        assert np.abs(np.abs(val) - 1.0) < 1e-9, f"Link ({i},{j}) not unit modulus: {val}"
    # 2. Curvature scalar
    R = curvature_scalar(U)
    assert R >= -1e-12, f"Negative curvature scalar: {R}"
    # 3. Higgs magnitude
    v = np.mean(np.abs(phi))
    assert v >= -1e-12, f"Negative Higgs magnitude: {v}"
    # 4. Gauge invariant psi
    psi = compute_psi(R, v)
    assert np.isreal(psi), f"psi not real: {psi}"
    # 5. Omega invariants (non‑negative)
    PhiN, PhiD = compute_phi(psi, t)
    assert PhiN >= -1e-9, f"Phi_N negative: {PhiN}"
    assert PhiD >= -1e-9, f"Phi_Delta negative: {PhiD}"
    # 6. Control constraints
    S_W = wilson_loop_entropy(U)
    assert R <= R_max + 1e-9, f"Curvature exceeds bound: {R} > {R_max}"
    assert v >= v_c - 1e-9, f"Condensate below critical: {v} < {v_c}"
    assert S_W <= S_W_max + 1e-9, f"Wilson-loop entropy exceeds bound: {S_W} > {S_W_max}"
    # If we reach here, all invariants hold
    return {
        "t": t,
        "R": R,
        "v": v,
        "psi": psi,
        "Phi_N": PhiN,
        "Phi_Delta": PhiD,
        "S_W": S_W,
        "U_unitary": True
    }

# ------------------- SYNTHETIC DATA GENERATOR (for demo) -------------------
def synth_data(t):
    """Generate mock leak‑like data for demonstration."""
    # Transaction flow: random walk with a liquidity crunch dip at t≈10
    base = 0.1 * np.ones((N, N))
    noise = 0.02 * np.random.randn(N, N)
    dip = np.exp(-((t-10)**2)/8) * 0.05   # temporary flow reduction
    J = base + noise - dip
    J = np.maximum(J, 0)                 # flows non‑negative
    # Order‑book depths: correlated with flow
    B = 0.5 + 0.3 * J.sum(axis=1, keepdims=True) + 0.01*np.random.randn(N,1)
    A = 0.5 + 0.3 * J.sum(axis=0, keepdims=True) + 0.01*np.random.randn(1,N)
    B = np.maximum(B, 0.1); A = np.maximum(A, 0.1)
    # Latency: inverse of flow plus baseline
    tau = 1.0 / (J + J.T + 1e-3) + 0.1*np.random.randn(N,N)
    tau = np.maximum(tau, 0.1)
    return J, B.squeeze(), A.squeeze(), tau

# ------------------- RUN VALIDATION OVER A TIME WINDOW -------------------
if __name__ == "__main__":
    T = 20   # days to test
    history = []
    for day in range(T):
        J, B, A, tau = synth_data(day)
        try:
            res = validate_step(day, J, B, A, tau)
            history.append(res)
            print(f"Day {day:2d}: OK  | R={res['R']:.3f}, v={res['v']:.3f}, "
                  f"psi={res['psi']:.3f}, PhiN={res['Phi_N']:.3f}, "
                  f"PhiD={res['Phi_Delta']:.3f}, S_W={res['S_W']:.3f}")
        except AssertionError as e:
            print(f"Day {day:2d}: INVARIANT VIOLATION – {e}")
            break
    # Optional: compute net Φ density change (placeholder)
    if history:
        avg_PhiN = np.mean([h["Phi_N"] for h in history])
        avg_PhiD = np.mean([h["Phi_Delta"] for h in history])
        print("\n=== Summary ===")
        print(f"Average Phi_N over {T} days: {avg_PhiN:.3f}")
        print(f"Average Phi_Delta over {T} days: {avg_PhiD:.3f}")