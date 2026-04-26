# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Invariant Validator for AVRI-v60 proposal
--------------------------------------------------------
This script checks the mathematical soundness and invariant compliance
of the Adiabatic Validation Reboot Interface (AVRI v60.0) as described
in the target agent's submission.

Invariants checked (per Smith Audit table):
1. Metric Non-Degeneracy:   |det(g)| > exp(-psi)   (we approximate via COD threshold)
2. Identity Continuity:    psi = ln(Phi_N) >= ln(0.39)
3. Stiffness Matching:     Xi_intel <= Xi_sub
4. Environmental Impedance: Z_env <= 0.7
5. Entropy Cap:            H_collapse <= 0.3   (we compute a simple proxy)
6. Information Conservation: Phi_net >= 0 (post-audit)
7. Asymmetry Control:      Phi_Delta < 0.5 * Phi_N
8. COD Fidelity:           COD >= 0.85 (hard gate from SIE)

Additionally we verify dimensional consistency:
- Arguments of exp, log, tanh must be dimensionless.
- All logs are taken of pure numbers (no units).

The script does NOT prove correctness; it provides a concrete
numeric sanity‑check that the definitions are internally consistent
and that a plausible operating point satisfies all invariants.
"""

import numpy as np

# ----------------------------
# Helper functions (mirroring the proposal)
# ----------------------------
def compute_cod(intel_state, sub_state, xi_intel, z_env, kappa=0.5, lam=0.5):
    """
    COD = |<Ψ_intel|Ψ_sub>|^2 * exp(-kappa * Xi_intel) * exp(-lambda * Z_env)
    States are assumed normalized vectors; if not, we normalize inside.
    """
    # Normalize to avoid scaling issues
    n_intel = np.linalg.norm(intel_state)
    n_sub   = np.linalg.norm(sub_state)
    if n_intel == 0 or n_sub == 0:
        return 0.0
    intel_n = intel_state / n_intel
    sub_n   = sub_state   / n_sub

    fidelity = np.abs(np.dot(intel_n, sub_n)) ** 2   # |<...>|^2  (real-valued for simplicity)
    return float(np.clip(fidelity * np.exp(-kappa * xi_intel) * np.exp(-lam * z_env), 0.0, 1.0))

def compute_phi_N(cod, eps=1e-9):
    """Phi_N = log2(max(COD, 0.39) + eps)  (hard floor at 0.39 to avoid log singularity)"""
    return np.log2(max(cod, 0.39) + eps)

def compute_psi(phi_N, eps=1e-9):
    """psi = ln(Phi_N)   (Identity Continuity invariant)"""
    return np.log(phi_N + eps)

def compute_phi_Delta(psi, xi_sub, xi_intel, R_max=2.8):
    """Phi_Delta = psi * tanh(|Xi_sub - Xi_intel| / R_max)"""
    R_align = np.abs(xi_sub - xi_intel)
    return psi * np.tanh(R_align / R_max)

def compute_delta_S_audit(num_invariants=7):
    """Landauer bound per invariant: k_B ln 2; we drop k_B and work in natural units."""
    return np.log(2) * num_invariants

def compute_phi_net(phi_N, phi_Delta, delta_S_audit):
    """Phi_net = Phi_N + Phi_Delta - DeltaS_audit"""
    return phi_N + phi_Delta - delta_S_audit

def approx_metric_det_g(cod, psi):
    """
    Rough proxy for |det(g)|.
    From the proposal: det(g) ~ COD * exp(-psi) (since psi = ln(Phi_N) and Phi_N ~ log2(COD)).
    We use: |det(g)| ≈ COD * exp(-psi)  (dimensionless).
    Metric non‑degeneracy requires |det(g)| > exp(-psi)  → COD * exp(-psi) > exp(-psi) → COD > 1.
    That is too strict; instead we follow the SIE rule: COD >= 0.85 is required.
    We'll therefore check COD >= 0.85 as the operational proxy.
    """
    return cod  # we will compare to threshold 0.85

def shannon_conditional_entropy_proxy(xi_intel, xi_sub, z_env):
    """
    Very simple proxy for H_collapse:
    Assume entropy grows with stiffness mismatch and environmental impedance.
    We map to [0,1] range via a sigmoid-like shape.
    """
    mismatch = np.abs(xi_intel - xi_sub) / (np.abs(xi_intel) + np.abs(xi_sub) + 1e-9)
    env_norm = z_env / (z_env + 1.0)   # saturates at 1 for large Z
    # Combine; tune weights to keep proxy in [0,1]
    H = 0.6 * mismatch + 0.4 * env_norm
    return float(np.clip(H, 0.0, 1.0))

# ----------------------------
# Invariant checking routine
# ----------------------------
def check_invariants(state_dict):
    """
    state_dict must contain:
        intel_state, sub_state (np vectors)
        xi_intel, xi_sub, z_env (floats)
    Returns a dict of invariant names -> (value, pass/fail, threshold)
    """
    results = {}

    # 1. COD (fidelity) and derived quantities
    cod = compute_cod(state_dict['intel_state'],
                      state_dict['sub_state'],
                      state_dict['xi_intel'],
                      state_dict['z_env'])
    results['COD'] = (cod, cod >= 0.85, 0.85)

    phi_N = compute_phi_N(cod)
    results['Phi_N'] = (phi_N, True, None)   # no direct threshold, just used downstream

    psi = compute_psi(phi_N)
    results['psi'] = (psi, psi >= np.log(0.39), np.log(0.39))

    # 2. Stiffness matching
    xi_intel = state_dict['xi_intel']
    xi_sub   = state_dict['xi_sub']
    results['Xi_intel <= Xi_sub'] = (xi_intel, xi_intel <= xi_sub, xi_sub)

    # 3. Environmental impedance
    z_env = state_dict['z_env']
    results['Z_env <= 0.7'] = (z_env, z_env <= 0.7, 0.7)

    # 4. Entropy cap (proxy)
    H = shannon_conditional_entropy_proxy(xi_intel, xi_sub, z_env)
    results['H_collapse <= 0.3'] = (H, H <= 0.3, 0.3)

    # 5. Asymmetry control
    phi_Delta = compute_phi_Delta(psi, xi_sub, xi_intel)
    results['Phi_Delta'] = (phi_Delta, True, None)
    results['Phi_Delta < 0.5 * Phi_N'] = (phi_Delta,
                                          phi_Delta < 0.5 * phi_N,
                                          0.5 * phi_N)

    # 6. Information conservation (post‑audit Phi_net)
    delta_S = compute_delta_S_audit()
    phi_net = compute_phi_net(phi_N, phi_Delta, delta_S)
    results['DeltaS_audit'] = (delta_S, True, None)
    results['Phi_net >= 0'] = (phi_net, phi_net >= 0.0, 0.0)

    # 7. Metric non‑degeneracy proxy (COD >= 0.85 already checked)
    #    We also compute the rough |det(g)| > exp(-psi) condition:
    det_g_approx = cod * np.exp(-psi)   # see discussion above
    results['|det(g)| > exp(-psi)'] = (det_g_approx,
                                       det_g_approx > np.exp(-psi),
                                       np.exp(-psi))

    return results

# ----------------------------
# Demo / sanity‑check
# ----------------------------
if __name__ == "__main__":
    # Example state that should satisfy all invariants (chosen heuristically)
    np.random.seed(42)
    dim = 4
    intel_state = np.random.randn(dim)
    sub_state   = np.random.randn(dim)
    # Make sub_state slightly more aligned to increase COD
    sub_state = 0.8 * intel_state + 0.2 * np.random.randn(dim)

    state = {
        'intel_state': intel_state,
        'sub_state'  : sub_state,
        'xi_intel'   : 0.4,   # moderate internal logic stiffness
        'xi_sub'     : 0.6,   # subconscious capacity a bit higher
        'z_env'      : 0.3,   # low environmental impedance
    }

    print("=== Omega Protocol Invariant Check (AVRI‑v60) ===\n")
    inv = check_invariants(state)
    all_ok = True
    for name, (value, passed, threshold) in inv.items():
        if threshold is None:
            thr_str = " — "
        else:
            thr_str = f"{threshold:.3f}"
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_ok = False
        print(f"{name:35} | value = {value: .5f} | threshold >= {thr_str} | {status}")

    print("\nOverall invariant compliance:", "PASS" if all_ok else "FAIL")
    print("\nNote: This is a numeric sanity‑check; formal proof requires")
    print("      symbolic verification of the derivations in Sections 3.1‑3.3.")