# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# -*- coding: utf-8 -*-
"""
FSBAM‑Ω mathematical soundness validator.
Checks that the field‑theoretic construction respects the Omega Protocol invariants
(Phi_N, Phi_Delta, J*) and the MPC‑Ω constraints.
"""

import numpy as np
from scipy.stats import genpareto
from scipy.optimize import minimize

# ----------------------------------------------------------------------
# Helper functions (synthetic data generation)
# ----------------------------------------------------------------------
def synthetic_indicators(T, seed=0):
    """Generate 5 synthetic indicator time‑series I_k(t) ∈ [0,1]."""
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 4*np.pi, T)
    # Mix of sinusoids + slow drift to mimic adoption curves
    I1 = 0.5 + 0.3*np.sin(t) + 0.1*t/(4*np.pi)          # function/seq ratio
    I2 = 0.4 + 0.2*np.sin(0.7*t) + 0.05*t/(4*np.pi)    # tool releases
    I3 = 0.3 + 0.25*np.cos(0.5*t) + 0.08*t/(4*np.pi)  # funding fraction
    I4 = 0.2 + 0.35*np.sin(0.3*t) + 0.12*t/(4*np.pi) # citation growth
    I5 = 0.6 + 0.2*np.sin(0.9*t)                     # adoption entropy (proxy)
    # Clip to [0,1] and add small noise
    I = np.vstack([I1, I2, I3, I4, I5])
    I = np.clip(I + rng.normal(0, 0.02, I.shape), 0, 1)
    return I, t

# ----------------------------------------------------------------------
# Core model components
# ----------------------------------------------------------------------
def normalise_indicators(I):
    """Scale each indicator to [0,1] using its own historical max."""
    I_max = I.max(axis=1, keepdims=True)
    I_max[I_max == 0] = 1.0
    return I / I_max

def compute_AI(I_norm, w):
    """Adoption Index as weighted sum (weights sum to 1)."""
    return np.tensordot(w, I_norm, axes=([0], [0]))  # shape (T,)

def entropy_from_indicators(I_norm):
    """Proxy entropy S_adopt = -∑ p_b log p_b using 5‑bin histogram of AI."""
    # We'll treat the 5 indicators as "sub‑fields" and compute distribution of their values at each t.
    # For each time step, build histogram over the 5 indicators (values in [0,1]).
    T = I_norm.shape[1]
    S = np.zeros(T)
    bins = np.linspace(0, 1, 6)  # 5 bins
    for ti in range(T):
        hist, _ = np.histogram(I_norm[:, ti], bins=bins, density=True)
        # Avoid zeros in log
        hist = hist[hist > 0]
        S[ti] = -np.sum(hist * np.log(hist))
    # Normalise to [0,1] (max entropy = log(5))
    return S / np.log(5)

def phi_N_mapping(AI, PhiN0=0.5, eta1=0.3, eta2=0.2, tau1=2):
    """Φ_N(t) = Φ_N0 + η1·AI(t‑τ1) – η2·(AI‑0.5)²."""
    AI_delayed = np.concatenate([np.full(tau1, AI[0]), AI[:-tau1]])
    return PhiN0 + eta1 * AI_delayed - eta2 * (AI - 0.5)**2

def phi_Delta_mapping(AI, S, PhiD0=0.2, eta3=0.25, eta4=0.15, tau2=2):
    """Φ_Δ(t) = Φ_Δ0 + η3·(1‑S(t‑τ2)) + η4·AI(t)·(1‑S(t))."""
    S_delayed = np.concatenate([np.full(tau2, S[0]), S[:-tau2]])
    return PhiD0 + eta3 * (1 - S_delayed) + eta4 * AI * (1 - S)

def frenet_serret_curvature_torsion(path):
    """
    Compute curvature κ and torsion τ for a discrete 3‑+ dimensional path.
    Uses finite differences; returns arrays of length T (kappa, tau).
    For dimensions >3 we embed into the subspace spanned by first three PCs.
    """
    # Center and reduce to 3D via PCA (first three components)
    from sklearn.decomposition import PCA
    pca = PCA(n_components=3)
    path_3d = pca.fit_transform(path.T).T  # shape (3, T)
    # First, second, third derivatives via finite differences
    dt = 1.0  # unit time step
    r = path_3d
    r_prime = np.gradient(r, dt, axis=1)
    r_double = np.gradient(r_prime, dt, axis=1)
    r_triple = np.gradient(r_double, dt, axis=1)

    # Curvature κ = |r' × r''| / |r'|³
    cross = np.cross(r_prime, r_double, axis=0)
    kappa = np.linalg.norm(cross, axis=0) / (np.linalg.norm(r_prime, axis=0)**3 + 1e-12)

    # Torsion τ = [(r' × r'')·r'''] / |r' × r''|²
    triple = np.einsum('ij,ij->j', cross, r_triple)
    denom = np.linalg.norm(cross, axis=0)**2 + 1e-12
    tau = triple / denom
    return kappa, tau

def compute_psi(AI, kappa, tau, kappa0=1e-3, tau0=1e-3, lam=0.5):
    """ψ = ln(κ τ / (κ₀ τ₀)) + λ·AI."""
    return np.log((kappa * tau) / (kappa0 * tau0) + 1e-12) + lam * AI

def stiffness_from_eff_potential(PhiN, PhiD):
    """
    Approximate V_eff as a simple quadratic well around the operating point:
        V_eff ≈ 0.5 * kN * (Φ_N - ΦN0)² + 0.5 * kΔ * (Φ_Δ - ΦΔ0)²
    Then ξ_N⁻² = kN, ξ_Δ⁻² = kΔ.
    We infer kN, kΔ from the empirical variance of Φ_N, Φ_Δ.
    """
    kN = 1.0 / (np.var(PhiN) + 1e-9)
    kD = 1.0 / (np.var(PhiD) + 1e-9)
    return kN, kD  # these are ξ⁻²

def mpc_qp(AI, S, PhiN, PhiD, AI_opt=0.5, S_target=0.5,
           w_AI=1.0, w_S=1.0, w_PhiN=1.0, w_PhiD=0.5):
    """
    Solve a one‑step QP: minimise
        w_AI*(AI-AI_opt)² + w_S*(S-S_target)² + w_PhiN*max(0,0.6-PhiN)² + w_PhiD*PhiD²
    subject to:
        0.3 ≤ AI ≤ 0.7
        S ≥ S_min (0.2)
        Φ_N ≥ 0.6
    We return the optimal control adjustment (delta_AI, delta_S) that would
    bring the state closer to the optimum while respecting bounds.
    """
    # Decision variables: adjustments to AI and S (clipped later)
    def objective(x):
        dAI, dS = x
        AI_new = np.clip(AI + dAI, 0, 1)
        S_new  = np.clip(S + dS, 0, 1)
        PhiN_new = phi_N_mapping(AI_new)  # ignore delay for simplicity
        PhiD_new = phi_Delta_mapping(AI_new, S_new)
        penalty = (w_AI*(AI_new - AI_opt)**2 +
                   w_S*(S_new - S_target)**2 +
                   w_PhiN*max(0.0, 0.6 - PhiN_new)**2 +
                   w_PhiD*PhiD_new**2)
        return penalty

    bounds = [(-0.2, 0.2), (-0.2, 0.2)]  # max step per iteration
    # Simple projection onto constraints after optimisation
    res = minimize(objective, x0=[0.0, 0.0], bounds=bounds, method='L-BFGS-B')
    dAI_opt, dS_opt = res.x
    # Apply and then enforce hard constraints
    AI_adj = np.clip(AI + dAI_opt, 0.3, 0.7)
    S_adj  = np.max(S + dS_opt, 0.2)   # S ≥ S_min
    PhiN_adj = phi_N_mapping(AI_adj)
    PhiD_adj = phi_Delta_mapping(AI_adj, S_adj)
    return {
        "AI_adj": AI_adj,
        "S_adj": S_adj,
        "PhiN_adj": PhiN_adj,
        "PhiD_adj": PhiD_adj,
        "cost": res.fun
    }

def gpd_anomaly_score(psi_history, u_quantile=0.95):
    """Fit GPD to exceedances over threshold u and compute survival probability."""
    u = np.quantile(np.abs(psi_history), u_quantile)
    exceed = np.abs(psi_history) - u
    exceed = exceed[exceed > 0]
    if len(exceed) < 5:
        # Not enough data – return neutral score
        return 0.5
    # Fit shape (c), loc=0, scale
    c, loc, scale = genpareto.fit(exceed, floc=0)
    # Survival function for current |psi|
    current = np.abs(psi_history[-1])
    if current <= u:
        return 1.0  # no exceedance -> low anomaly
    z = current - u
    sf = genpareto.sf(z, c, loc, scale)  # P(X > z)
    return sf  # anomaly score (small = anomalous)

# ----------------------------------------------------------------------
# Validation routine
# ----------------------------------------------------------------------
def validate_FSBAM_Omega(T=80):
    print("=== FSBAM‑Ω Omega‑Protocol Validation ===")
    I_raw, t = synthetic_indicators(T, seed=42)
    I_norm = normalise_indicators(I_raw)

    # Learn weights w via ridge regression against a dummy "ground truth"
    # (here we just use the mean of indicators as proxy)
    gt = I_norm.mean(axis=0)
    from sklearn.linear_model import Ridge
    ridge = Ridge(alpha=1.0).fit(I_norm.T, gt)
    w = ridge.coef_
    w = w / w.sum()  # enforce sum‑to‑1
    print(f"Learned weights: {w}")

    AI = compute_AI(I_norm, w)
    S = entropy_from_indicators(I_norm)

    PhiN = phi_N_mapping(AI)
    PhiD = phi_Delta_mapping(AI, S)

    kappa, tau = frenet_serret_curvature_torsion(I_norm.T)
    psi = compute_psi(AI, kappa, tau)

    xiN2, xiD2 = stiffness_from_eff_potential(PhiN, PhiD)  # these are ξ⁻²

    # ----- Omega‑Protocol invariant checks -----
    # 1. Phi_N (connectivity) must be non‑negative; we additionally require ≥0.6 per MPC.
    assert np.all(PhiN >= 0), "Phi_N negative – violates connectivity invariant."
    print(f"Phi_N min/max: {PhiN.min():.3f}/{PhiN.max():.3f}")

    # 2. Phi_Delta (asymmetry) must be non‑negative.
    assert np.all(PhiD >= 0), "Phi_Delta negative – violates asymmetry invariant."
    print(f"Phi_Delta min/max: {PhiD.min():.3f}/{PhiD.max():.3f}")

    # 3. Stiffness invariants (inverse squared relaxation times) must be positive.
    assert np.all(xiN2 > 0) and np.all(xiD2 > 0), "Stiffness non‑positive."
    print(f"xi_N^-2 mean: {xiN2.mean():.3f}, xi_D^-2 mean: {xiD2.mean():.3f}")

    # 4. psi should be finite (no NaN/inf).
    assert np.all(np.isfinite(psi)), "Psi contains non‑finite values."
    print(f"Psi min/max: {psi.min():.3f}/{psi.max():.3f}")

    # 5. MPC‑Ω constraints (hard bounds)
    assert np.all((AI >= 0.3) & (AI <= 0.7)), "AI out of [0.3,0.7] band."
    assert np.all(S >= 0.2), "Adoption entropy below S_min."
    assert np.all(PhiN >= 0.6), "Phi_N below connectivity threshold 0.6."
    print("All hard MPC constraints satisfied.")

    # 6. Anomaly detection sanity check
    anomaly_score = gpd_anomaly_score(psi)
    print(f"Anomaly score (survival prob): {anomaly_score:.4f}")
    # If score < 0.01 we would trigger an alert – ensure we also check Phi thresholds
    if anomaly_score < 0.01 and (PhiD[-1] > 0.7 or PhiN[-1] < 0.5):
        print(">>> ANOMALY TRIGGERED (would issue MPC alert) <<<")
    else:
        print("No anomaly trigger at final time step.")

    # 7. Demonstrate one MPC optimisation step
    mpc_res = mpc_qp(AI[-1], S[-1], PhiN[-1], PhiD[-1])
    print("\nOne‑step MPC‑Ω adjustment:")
    print(f"  AI   : {AI[-1]:.3f} → {mpc_res['AI_adj']:.3f}")
    print(f"  S    : {S[-1]:.3f} → {mpc_res['S_adj']:.3f}")
    print(f"  Phi_N: {PhiN[-1]:.3f} → {mpc_res['PhiN_adj']:.3f}")
    print(f"  Phi_D: {PhiD[-1]:.3f} → {mpc_res['PhiD_adj']:.3f}")
    print(f"  Cost : {mpc_res['cost']:.6f}")

    print("\nValidation PASSED – all Omega‑Protocol invariants respected.")
    return True

if __name__ == "__main__":
    validate_FSBAM_Omega()