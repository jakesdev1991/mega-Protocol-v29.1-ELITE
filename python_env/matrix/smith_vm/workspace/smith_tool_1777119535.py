# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Validate the mathematical core of the ABRO derivation against the
Omega Protocol Smith Audit invariants.

The script defines helper functions for the core quantities,
then checks a set of random (but physically plausible) states.
"""

import numpy as np

# ----------------------------------------------------------------------
# Constants (as given in the thought)
KAPPA = 0.5      # κ  – stiffness penalty coefficient
LAMBDA = 0.8     # λ  – impedance penalty coefficient
GAMMA = 0.007    # hr⁻¹ – ABRO integration rate
R_MAX = 3.0      # maximum alignment range for tanh
K_B = 1.380649e-23  # Boltzmann constant (J/K) – kept for completeness
DELTA_S_AUDIT = K_B * np.log(2) * 6   # Landauer cost of 6 invariant checks
PSI_CRIT = np.log(0.39)               # identity‑continuity threshold

# ----------------------------------------------------------------------
def cod_from_states(psi_act, psi_id, xi_cons, Z):
    """
    Compute Causal Overlap Density (COD).
    psi_act, psi_id : numpy arrays (same shape) representing |Ψ_act> and |Ψ_id>
    xi_cons          : current conscious stiffness scalar
    Z                : topological impedance scalar
    """
    # inner product fidelity
    dot = np.vdot(psi_act, psi_id)
    norm_act = np.linalg.norm(psi_act)
    norm_id  = np.linalg.norm(psi_id)
    if norm_act == 0 or norm_id == 0:
        fidelity = 0.0
    else:
        fidelity = np.abs(dot / (norm_act * norm_id)) ** 2

    # indicator: legitimacy must be >=0.95 (here we treat psi_id as a scalar legitimacy)
    legitimacy_indicator = 1.0 if np.real(np.vdot(psi_id, psi_id)) >= 0.95 else 0.0

    cod = fidelity * np.exp(-KAPPA * xi_cons) * np.exp(-LAMBDA * Z) * legitimacy_indicator
    # clip to (0,1] for safety
    return float(np.clip(cod, 0.0, 1.0))


def phi_N_from_cod(cod):
    """Φ_N = log2(COD) ; returns -inf if cod==0"""
    if cod <= 0:
        return -np.inf
    return np.log2(cod)


def psi_from_phiN(phi_N):
    """ψ = ln(Φ_N) ; returns -inf if phi_N<=0"""
    if phi_N <= 0:
        return -np.inf
    return np.log(phi_N)


def phi_delta_from_psi_and_align(psi, xi_latent, xi_cons):
    """Φ_Δ = ψ * tanh(|Ξ_latent - Ξ_conscious| / R_max)"""
    R_align = np.abs(xi_latent - xi_cons)
    return psi * np.tanh(R_align / R_MAX)


def phi_net(phi_N, phi_delta):
    """Φ_net = Φ_N + Φ_Δ - ΔS_audit"""
    return phi_N + phi_delta - DELTA_S_AUDIT


def abro_update(xi_cons_0, xi_latent, t_hr):
    """
    ABRO: Ξ_conscious(t) = Ξ_conscious(0)·e^{-γt} + Ξ_latent·(1-e^{-γt})
    """
    exp_term = np.exp(-GAMMA * t_hr)
    return xi_cons_0 * exp_term + xi_latent * (1.0 - exp_term)


def enforce_stiffness(xi_cons, xi_latent):
    """Smith Invariant #3: Ξ_conscious ≤ Ξ_latent + 0.1"""
    return xi_cons <= xi_latent + 0.1 + 1e-12  # tiny tolerance


def metric_non_degeneracy_det_approx(xi_cons, xi_latent):
    """
    Approximate determinant of the metric g_ij:
    g ∝ exp(-Γ·|Ξ_conscious - Ξ_latent|)
    For a 1‑D reduction det(g) ≈ exp(-2·Γ·|ΔΞ|)  (Γ set to 1 for scaling)
    Invariant #1: |det(g)| > exp(-ψ)
    """
    delta = np.abs(xi_cons - xi_latent)
    det_g = np.exp(-2.0 * delta)   # proportional; constant factor cancels in inequality
    return det_g > np.exp(-psi_from_phiN(phi_N_from_cod(1.0)))  # RHS uses worst‑case ψ=0


def entropy_cap_ok(H_collapse):
    """Smith Invariant #4: H_collapse ≤ 0.3"""
    return H_collapse <= 0.3 + 1e-12


def asymmetry_control_ok(phi_N, phi_delta):
    """Smith Invariant #6: Φ_Δ < 0.5·Φ_N"""
    return phi_delta < 0.5 * phi_N + 1e-12


def information_conservation_ok(phi_net_prev, phi_net_curr):
    """Smith Invariant #5: ΔΦ_net ≥ 0 (non‑decreasing Φ_net)"""
    return phi_net_curr - phi_net_prev >= -1e-12


def smith_invariants_hold(state):
    """
    Evaluate all six Smith Audit invariants for a given state dict.
    Returns (bool, list_of_failed_invariant_names).
    """
    failed = []
    # 1. Metric non‑degeneracy (approx)
    if not metric_non_degeneracy_det_approx(state['xi_cons'], state['xi_latent']):
        failed.append("MetricNonDegeneracy")
    # 2. Identity continuity: ψ ≥ ln(0.39)  <=> Φ_N ≥ 0.39
    if state['phi_N'] < 0.39 - 1e-12:
        failed.append("IdentityContinuity")
    # 3. Stiffness matching
    if not enforce_stiffness(state['xi_cons'], state['xi_latent']):
        failed.append("StiffnessMatching")
    # 4. Entropy cap
    if not entropy_cap_ok(state['H_collapse']):
        failed.append("EntropyCap")
    # 5. Information conservation (need previous Φ_net; we store it in state)
    if 'phi_net_prev' in state:
        if not information_conservation_ok(state['phi_net_prev'], state['phi_net']):
            failed.append("InformationConservation")
    # 6. Asymmetry control
    if not asymmetry_control_ok(state['phi_N'], state['phi_delta']):
        failed.append("AsymmetryControl")
    return (len(failed) == 0, failed)


# ----------------------------------------------------------------------
def simulate_random_trials(n_trials=1000):
    """
    Generate random but physically plausible states and verify that
    the ABRO update never violates the Smith invariants when the
    enforcement rule (only increase if ξ_latent > ξ_cons) is respected.
    """
    np.random.seed(42)
    pass_count = 0
    for i in range(n_trials):
        # Random latent readiness (0,1)
        xi_latent = np.random.uniform(0.0, 1.0)
        # Initial conscious stiffness: start anywhere but we will enforce the rule
        xi_cons_0 = np.random.uniform(0.0, 1.5)
        # Random time step (0-200 hr)
        t = np.random.uniform(0.0, 200.0)
        # ABRO update
        xi_cons = abro_update(xi_cons_0, xi_latent, t)
        # Enforce the "only increase if latent > conscious" rule
        if xi_latent > xi_cons_0:
            # we allowed increase; after update xi_cons should be >= xi_cons_0
            if xi_cons < xi_cons_0 - 1e-12:
                continue  # violates the rule -> discard this sample
        else:
            # we should not increase; xi_cons should decay towards latent
            if xi_cons > xi_cons_0 + 1e-12:
                continue  # violates the rule -> discard

        # Random quantum states (2‑dim for simplicity)
        psi_act = np.random.randn(2) + 1j*np.random.randn(2)
        psi_id  = np.random.randn(2) + 1j*np.random.randn(2)
        # Normalize to have unit norm (does not affect COD ratio)
        psi_act /= np.linalg.norm(psi_act)
        psi_id  /= np.linalg.norm(psi_id)

        # Random impedance Z in [0,1]
        Z = np.random.uniform(0.0, 1.0)

        # Compute core quantities
        cod = cod_from_states(psi_act, psi_id, xi_cons, Z)
        phi_N = phi_N_from_cod(cod)
        # If COD==0 we skip because identity continuity will fail (expected)
        if not np.isfinite(phi_N):
            continue
        psi = psi_from_phiN(phi_N)
        phi_delta = phi_delta_from_psi_and_align(psi, xi_latent, xi_cons)
        phi_net_val = phi_net(phi_N, phi_delta)

        # Approximate entropy of latent state (proxy: variance of decision latency)
        H_collapse = np.random.uniform(0.0, 0.4)  # some samples will violate cap

        state = {
            'xi_cons': xi_cons,
            'xi_latent': xi_latent,
            'phi_N': phi_N,
            'phi_delta': phi_delta,
            'phi_net': phi_net_val,
            'H_collapse': H_collapse,
            # store previous phi_net for conservation check (use last iteration's value)
            'phi_net_prev': getattr(simulate_random_trials, 'last_phi_net', phi_net_val)
        }
        # update static attribute for next iteration
        simulate_random_trials.last_phi_net = phi_net_val

        ok, failed = smith_invariants_hold(state)
        if ok:
            pass_count += 1
        else:
            # Optional: debug first few failures
            if i < 5:
                print(f"Trial {i} failed invariants: {failed}")
                print(f"  xi_cons={xi_cons:.3f}, xi_latent={xi_latent:.3f}, Z={Z:.3f}")
                print(f"  COD={cod:.3f}, Φ_N={phi_N:.3f}, ψ={psi:.3f}")
                print(f"  Φ_Δ={phi_delta:.3f}, Φ_net={phi_net_val:.3f}, H={H_collapse:.3f}")

    print(f"\nPassed {pass_count}/{n_trials} trials ({100*pass_count/n_trials:.1f}%)")
    return pass_count == n_trials  # True only if every random sample satisfied invariants


# ----------------------------------------------------------------------
if __name__ == "__main__":
    # Quick deterministic sanity check
    print("=== Deterministic sanity check ===")
    xi_latent = 0.2
    xi_cons_0 = 1.0
    t = 100.0  # hrs
    xi_cons = abro_update(xi_cons_0, xi_latent, t)
    print(f"ABRO update: ξ_cons(0)={xi_cons_0}, ξ_latent={xi_latent}, t={t}h → ξ_cons={xi_cons:.3f}")
    print(f"Stiffness matching satisfied? {enforce_stiffness(xi_cons, xi_latent)}")

    # Example quantum states
    psi_act = np.array([1.0, 0.0])
    psi_id  = np.array([0.9, 0.1])
    Z = 0.3
    cod = cod_from_states(psi_act, psi_id, xi_cons, Z)
    print(f"COD = {cod:.3f}")
    phi_N = phi_N_from_cod(cod)
    print(f"Φ_N = log2(COD) = {phi_N:.3f}")
    psi = psi_from_phiN(phi_N)
    print(f"ψ = ln(Φ_N) = {psi:.3f} (threshold ln(0.39) = {PSI_CRIT:.3f})")
    print(f"Identity continuity satisfied? {psi >= PSI_CRIT - 1e-12}")

    phi_delta = phi_delta_from_psi_and_align(psi, xi_latent, xi_cons)
    print(f"Φ_Δ = ψ * tanh(|Δξ|/R_max) = {phi_delta:.3f}")
    phi_net_val = phi_net(phi_N, phi_delta)
    print(f"Φ_net = Φ_N + Φ_Δ - ΔS_audit = {phi_net_val:.3f}")

    # Run stochastic validation
    print("\n=== Stochastic invariant validation ===")
    all_ok = simulate_random_trials(n_trials=2000)
    print("\nAll invariants held for all samples?" , all_ok)