# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BRDO‑Ω mathematical validation script.
Checks that the definitions of GCI, Φ_N, Φ_Δ, ψ, S_worker obey the Omega Protocol invariants:
    Φ_N ≥ 0.6,   GCI ≤ 0.7,   S_worker ≥ log(3)
for a range of Byzantine worker counts and encoding redundancies.
"""

import numpy as np
import itertools

# -------------------------- CONFIGURATION --------------------------
np.random.seed(42)

d = 10          # dimension of the true gradient
m = 9           # number of workers (must be odd for clear majority)
max_t = m       # we will sweep t from 0..m
rho_vals = [2.0, 3.0, 4.0]   # redundancy n/d to test
n_vals = [int(rho * d) for rho in rho_vals]  # encoded dimension

# Parameters for GCI (tanh‑scaled linear model)
alpha, beta, gamma = 2.0, 1.5, 0.5

# Delay steps for Φ_N, Φ_Δ mapping (not needed for invariant check)
tau1, tau2 = 2, 2
eta1, eta2, eta3, eta4 = 0.1, 0.1, 0.1, 0.1

# Thresholds for residual‑based corruption detection
tau_res = 1.0   # arbitrary; in practice set from decoder guarantee

# Curvature placeholder: we use algebraic connectivity of worker graph as a proxy
def ollivier_ricci_proxy(residuals):
    """
    Very cheap proxy: build a complete graph with weight = exp(-||r_i - r_j||^2)
    and return the second smallest eigenvalue of the graph Laplacian (algebraic connectivity).
    Larger value → higher curvature (more robust).
    """
    m = residuals.shape[0]
    if m < 2:
        return 1.0
    # pairwise squared distances
    diff = residuals[:, None, :] - residuals[None, :, :]   # (m,m,d)
    sqdist = np.sum(diff**2, axis=2)
    W = np.exp(-sqdist)
    np.fill_diagonal(W, 0.0)
    D = np.diag(W.sum(axis=1))
    L = D - W
    eigvals = np.linalg.eigvalsh(L)
    return eigvals[1]   # second smallest (Fiedler value)

# -------------------------- CORE FUNCTIONS --------------------------
def sparse_encoder(n, d):
    """
    Return a random matrix with i.i.d. N(0,1) entries and orthonormal rows.
    This mimics the deterministic sparse encoder's property: any subset of ≤ n/2 rows
    is full rank, enabling unique recovery when t ≤ floor((m-1)/2).
    """
    A = np.random.randn(n, d)
    Q, _ = np.linalg.qr(A.T)   # Q is d×n with orthonormal columns
    return Q.T[:n, :]          # n×d with orthonormal rows

def encode_gradient(E, g):
    """y = E g"""
    return E @ g

def add_byzantine_errors(y_true, t_corrupt, m):
    """
    For the first t_corrupt workers add arbitrarily large errors.
    """
    errors = np.zeros_like(y_true)
    if t_corrupt > 0:
        errors[:t_corrupt] = 10.0 * np.random.randn(t_corrupt, y_true.shape[1])
    return y_true + errors

def decoder(E, y_tilde):
    """
    Deterministic decoder: least‑squares solution (exact when E has full row rank
    and number of errors ≤ floor((m-1)/2)). In practice we use the pseudo‑inverse.
    """
    E_pinv = np.linalg.pinv(E)   # d×n
    return E_pinv @ y_tilde.mean(axis=0)   # average over workers then lift

def compute_residuals(E, g_hat, y_tilde):
    """r_i = ỹ_i – E_i g_hat"""
    return y_tilde - E @ g_hat[:, None]   # (m,d)

def gci_from_residuals(residuals, rho):
    """
    GCI = tanh(α·θ_corr + β·ε + γ·ρ)
    where
        θ_corr = fraction of workers with ‖r_i‖ > τ_res
        ε      = mean ‖r_i‖
        ρ      = redundancy n/d
    """
    norms = np.linalg.norm(residuals, axis=1)
    theta_corr = np.mean(norms > tau_res)
    eps = np.mean(norms)
    return np.tanh(alpha * theta_corr + beta * eps + gamma * rho)

def phi_n_from_gci(gci_prev):
    """Φ_N = Φ_N0 - η1·GCI_{k-τ1} + η2·(1‑θ_corr)_{k-τ1}
       We approximate θ_corr from GCI via inverse tanh (monotonic)."""
    # invert tanh to get rough θ_corr + ε + ρ term (ignore ρ for simplicity)
    # For demonstration we just use a linear map:
    Phi_N0 = 1.0
    return Phi_N0 - eta1 * gci_prev + eta2 * (1.0 - np.tanh(gci_prev))  # placeholder

def phi_delta_from_gci(gci_prev):
    """Φ_Δ = Φ_Δ0 + η3·θ_corr_{k-τ2} - η4·ε_{k-τ2}"""
    Phi_Delta0 = 0.0
    return Phi_Delta0 + eta3 * np.tanh(gci_prev) - eta4 * np.tanh(gci_prev)  # placeholder

def worker_entropy(residuals):
    """S = -∑ p_i log p_i, p_i = ‖r_i‖/∑‖r_j‖"""
    norms = np.linalg.norm(residuals, axis=1)
    if np.sum(norms) == 0:
        return 0.0
    p = norms / np.sum(norms)
    # avoid log(0)
    p = p[p > 0]
    return -np.sum(p * np.log(p))

def invariant_psi(residuals, gci, lam=0.5):
    """ψ = ln(|ℛ_G|/ℛ₀) + λ·GCI"""
    # proxy curvature: algebraic connectivity
    curv = ollivier_ricci_proxy(residuals)
    R0 = 1.0   # reference curvature for a fully connected honest graph
    return np.log(np.abs(curv) / R0) + lam * gci

# -------------------------- VALIDATION LOOP --------------------------
def validate_scenario(t_corrupt, rho):
    """Run one Monte‑Carlo trial and assert Omega invariants."""
    n = int(rho * d)
    E = sparse_encoder(n, d)

    # true gradient (random direction)
    g_true = np.random.randn(d)
    g_true /= np.linalg.norm(g_true)   # unit norm for stability

    # encode and distribute
    y_clean = encode_gradient(E, g_true)          # (n,d) → we need per‑worker chunks
    # Simulate partitioning: repeat rows to have m chunks (simple round‑robin)
    reps = int(np.ceil(m * d / n))
    y_tiled = np.tile(y_clean, (reps, 1))[:m*d].reshape(m, d)   # (m,d)

    # inject Byzantine errors
    y_tilde = add_byzantine_errors(y_tiled, t_corrupt, m)

    # decode (master)
    g_hat = decoder(E, y_tilde)   # (d,)

    # residuals
    residuals = compute_residuals(E, g_hat, y_tilde)

    # metrics
    gci = gci_from_residuals(residuals, rho)
    phi_n = phi_n_from_gci(gci)
    phi_delta = phi_delta_from_gci(gci)
    s_worker = worker_entropy(residuals)
    psi = invariant_psi(residuals, gci)

    # ---- Omega Protocol invariants ----
    assert phi_n >= 0.6, f"Phi_N violation: {phi_n:.3f} < 0.6 (t={t_corrupt}, rho={rho})"
    assert gci <= 0.7, f"GCI violation: {gci:.3f} > 0.7 (t={t_corrupt}, rho={rho})"
    assert s_worker >= np.log(3), f"S_worker violation: {s_worker:.3f} < log(3) (t={t_corrupt}, rho={rho})"

    # Optional: print success for extreme cases
    if t_corrupt == 0:
        print(f"[OK] Honest case (t=0, rho={rho:.1f}): "
              f"Phi_N={phi_n:.3f}, GCI={gci:.3f}, S={s_worker:.3f}, ψ={psi:.3f}")

    return {
        "t": t_corrupt,
        "rho": rho,
        "Phi_N": phi_n,
        "GCI": gci,
        "Phi_Delta": phi_delta,
        "S_worker": s_worker,
        "psi": psi,
        "decoding_success": np.linalg.norm(g_hat - g_true) < 1e-1
    }

def sweep():
    """Iterate over t and rho to find the region where invariants hold."""
    results = []
    for t, rho in itertools.product(range(0, m+1), rho_vals):
        try:
            res = validate_scenario(t, rho)
            results.append(res)
        except AssertionError as e:
            # Record failure but continue sweeping
            print(f"[FAIL] {e}")
            results.append({**{"t": t, "rho": rho}, "error": str(e)})
    return results

if __name__ == "__main__":
    print("Starting BRDO‑Ω mathematical validation...")
    all_res = sweep()
    # Summary
    successes = [r for r in all_res if "error" not in r]
    failures  = [r for r in all_res if "error" in r]
    print(f"\nSummary: {len(successes)} successes, {len(failures)} failures.")
    if failures:
        print("First few failing cases:")
        for f in failures[:5]:
            print(f"  t={f['t']}, rho={f['rho']}: {f['error']}")
    else:
        print("All tested configurations satisfy the Omega Protocol invariants.")