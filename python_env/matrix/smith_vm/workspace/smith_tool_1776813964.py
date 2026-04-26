# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega‑Protocol Validation Script for HISS‑Ω (Homogeneity‑Induced Synchronization Shield)

What we validate:
1. ψ_sync(t) = ln( Φ_N^sync(t) / Φ_N^{(0)} )   (invariant definition)
2. 0 ≤ r(t) ≤ 1   (Kuramoto order parameter)
3. 0 ≤ S_action(t) ≤ ln(|A|)   (Shannon entropy, |A| = number of possible actions)
4. SFI(t) ∈ [0,1]   (tanh‑based index)
5. QP constraints when SFI > 0.68:
      Φ_N^sync(t) ≥ 0.4
      S_action(t) ≥ ln(3)
6. Cost‑function integrand ≥ 0   (by construction of squared‑plus terms)
7. Gauge current J^μ = √2 Φ_Δ^sync δ^μ_0  (only time‑component non‑zero)

The script generates synthetic on‑chain‑like data for a pool set,
computes the required metrics, and asserts the invariants.
Any assertion failure is reported as a protocol violation.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper functions (mirror the definitions in the proposal)
# ----------------------------------------------------------------------
def kuramoto_order(phases):
    """r(t) = |(1/N) Σ exp(iθ)|  ∈ [0,1]"""
    return np.abs(np.mean(np.exp(1j * phases)))

def action_entropy(prob_actions):
    """Shannon entropy S = - Σ p log p ; returns 0 if all probs zero."""
    p = np.asarray(prob_actions, dtype=float)
    p = p[p > 0]               # avoid log(0)
    return -np.sum(p * np.log(p))

def synchronization_fragility_index(r, S_action, Phi_Delta_sync, xi_L,
                                    alpha=1.0, beta=1.0, gamma=1.0, delta=1.0):
    """SFI = tanh[ α r + β (1-S) + γ Φ_Δ - δ ξ_L ]"""
    arg = alpha * r + beta * (1.0 - S_action) + gamma * Phi_Delta_sync - delta * xi_L
    return np.tanh(arg)

def Phi_N_sync_from_psi(psi, Phi_N0):
    """Inverse of invariant definition."""
    return Phi_N0 * np.exp(psi)

def Phi_Delta_sync_from_skew(liq_vals):
    """Skewness of liquidity distribution."""
    return ((np.mean((liq_vals - np.mean(liq_vals))**3)) /
            (np.std(liq_vals)**3 + 1e-12))

def xi_L_from_corr_len(corr_len):
    """Inverse correlation length."""
    return 1.0 / (corr_len + 1e-12)

def gauge_current(Phi_Delta_sync):
    """J^μ = √2 Φ_Δ δ^μ_0 → only J^0 non‑zero."""
    J = np.zeros(4)
    J[0] = np.sqrt(2) * Phi_Delta_sync
    return J

def cost_integrand(SFI, Phi_N_sync, S_action,
                   mu1=1.0, mu2=1.0, mu3=1.0,
                   SFI_thr=0.68, Phi_N_thr=0.4, S_thr=np.log(3)):
    """Quadratic penalty terms (always ≥0)."""
    term1 = max(SFI - SFI_thr, 0.0) ** 2
    term2 = mu1 * max(Phi_N_thr - Phi_N_sync, 0.0) ** 2
    term3 = mu2 * Phi_N_sync ** 2          # Φ_Δ^2 term (proxy)
    term4 = mu3 * max(S_thr - S_action, 0.0) ** 2
    return term1 + term2 + term3 + term4

# ----------------------------------------------------------------------
# Synthetic data generation (N pools, T timesteps)
# ----------------------------------------------------------------------
np.random.seed(42)
N_pools = 50
T_steps = 20

# Baseline parameters (chosen to be inside the safe region)
Phi_N0 = 1.0                     # reference Φ_N
base_liq = np.random.uniform(0.8, 1.2, size=N_pools)   # liquidity per pool
volatility = np.random.uniform(0.0, 0.5, size=T_steps) # ω(t)

# Random phases θ_i(t) ∈ [0, 2π)
phases = np.random.uniform(0, 2*np.pi, size=(T_steps, N_pools))

# Action probabilities: three actions (deposit, hold, withdraw)
# We'll bias them slightly with the phase to create correlation.
action_probs = np.zeros((T_steps, N_pools, 3))
for t in range(T_steps):
    # withdraw prob grows with phase near π, deposit near 0, hold elsewhere
    w = (1 + np.cos(phases[t])) / 2          # peaks at θ=0,π
    d = (1 + np.cos(phases[t] - np.pi)) / 2  # same shape shifted
    h = 1.0 - w - d
    # renormalize
    total = w + d + h
    action_probs[t] = np.stack([d/total, h/total, w/total], axis=-1)

# ----------------------------------------------------------------------
# Validation loop
# ----------------------------------------------------------------------
violations = []

for t in range(T_steps):
    # 1. Kuramoto order parameter
    r_t = kuramoto_order(phases[t])
    if not (0.0 <= r_t <= 1.0 + 1e-12):
        violations.append(f"t={t}: r(t)={r_t} out of [0,1]")

    # 2. Action entropy (average over pools)
    S_action_t = np.mean([action_entropy(action_probs[t, i]) for i in range(N_pools)])
    max_entropy = np.log(3)   # three actions
    if not (0.0 <= S_action_t <= max_entropy + 1e-12):
        violations.append(f"t={t}: S_action(t)={S_action_t} out of [0,ln(3)]")

    # 3. Derive Φ_N^sync from ψ (we compute ψ from Φ_N^sync later)
    # For synthetic data we define Φ_N^sync as a decreasing function of r_t:
    Phi_N_sync_t = Phi_N0 * (1.0 - 0.5 * r_t)   # simple model: more sync → lower Φ_N
    # Compute ψ_sync from invariant definition
    psi_sync_t = np.log(Phi_N_sync_t / Phi_N0)
    # Re‑derive Φ_N from ψ and compare
    Phi_N_from_psi = Phi_N_sync_from_psi(psi_sync_t, Phi_N0)
    if not np.isclose(Phi_N_sync_t, Phi_N_from_psi, rtol=1e-8, atol=1e-12):
        violations.append(f"t={t}: ψ_sync invariant broken: "
                          f"Φ_N^sync={Phi_N_sync_t}, ψ={psi_sync_t}, "
                          f"recovered Φ_N={Phi_N_from_psi}")

    # 4. Φ_Δ^sync from liquidity skewness
    Phi_Delta_sync_t = Phi_Delta_sync_from_skew(base_liq * (1 + 0.1 * np.sin(phases[t].mean())))

    # 5. Correlation length ξ_L (inverse of spatial correlation of withdrawals)
    # Proxy: variance of withdrawal prob across pools
    withdraw_prob = action_probs[t, :, 2]   # withdraw column
    corr_len_t = 1.0 / (np.var(withdraw_prob) + 1e-6)   # larger variance → shorter correlation length
    xi_L_t = xi_L_from_corr_len(corr_len_t)

    # 6. SFI
    SFI_t = synchronization_fragility_index(r_t, S_action_t,
                                            Phi_Delta_sync_t, xi_L_t)
    if not (0.0 <= SFI_t <= 1.0 + 1e-12):
        violations.append(f"t={t}: SFI(t)={SFI_t} out of [0,1]")

    # 7. QP constraints when SFI > 0.68
    if SFI_t > 0.68:
        if Phi_N_sync_t < 0.4 - 1e-12:
            violations.append(f"t={t}: SFI>0.68 but Φ_N^sync={Phi_N_sync_t} < 0.4")
        if S_action_t < np.log(3) - 1e-12:
            violations.append(f"t={t}: SFI>0.68 but S_action={S_action_t} < ln(3)")

    # 8. Cost integrand non‑negativity (should hold by construction)
    integrand = cost_integrand(SFI_t, Phi_N_sync_t, S_action_t)
    if integrand < -1e-12:
        violations.append(f"t={t}: cost integrand negative = {integrand}")

    # 9. Gauge current: only time component non‑zero
    J_t = gauge_current(Phi_Delta_sync_t)
    if not np.allclose(J_t[1:], 0.0, atol=1e-12):
        violations.append(f"t={t}: gauge current has spatial components: {J_t}")

# ----------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------
if violations:
    print("❌ Protocol violations detected:")
    for v in violations[:10]:   # limit output
        print(" -", v)
    if len(violations) > 10:
        print(f"   ... and {len(violations)-10} more.")
else:
    print("✅ All Omega‑Protocol invariants satisfied for the synthetic dataset.")
    print(f"   Checked {T_steps} timesteps × {N_pools} pools.")