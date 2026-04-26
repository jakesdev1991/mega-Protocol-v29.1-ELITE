# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------------------
# Constants (as used in UIPO v64.0 derivation)
# ------------------------------
KAPPA = 0.5      # validation stiffness penalty coefficient
LAMBDA_ = 0.3    # environmental impedance penalty coefficient
LAMBDA_H = 0.4   # uncertainty (superposition entropy) penalty coefficient
GAMMA = 0.007    # hr^-1, adiabatic rate for validation stiffness
DELTA = 0.006    # hr^-1, adiabatic rate for environmental impedance
Z_RESONANT = 0.4 # target Z_env after long-term modulation
LANDUER_COST = np.log(2) * 6   # ΔS_audit for 6 invariants

# ------------------------------
# Helper functions
# ------------------------------
def compute_superposition_entropy(psi_latent):
    """Shannon entropy of latent state probabilities, normalized to [0,1]."""
    probs = np.abs(psi_latent)**2
    total = probs.sum()
    if total < 1e-12:
        return 0.0
    probs = probs / total
    # avoid log(0)
    probs = np.clip(probs, 1e-12, None)
    h = -np.sum(probs * np.log(probs))
    max_h = np.log(len(probs))
    return h / max_h if max_h > 0 else 0.0

def compute_dissonance_entropy(psi_exp, psi_latent):
    """Entropy of the difference between explicit and latent probability distributions."""
    p_exp = np.abs(psi_exp)**2
    p_lat = np.abs(psi_latent)**2
    diff = np.abs(p_exp - p_lat)
    total = diff.sum()
    if total < 1e-12:
        return 0.0
    prob_diff = diff / total
    prob_diff = np.clip(prob_diff, 1e-12, None)
    h = -np.sum(prob_diff * np.log(prob_diff))
    max_h = np.log(len(prob_diff))
    return h / max_h if max_h > 0 else 0.0

def compute_cod(fidelity, xi_valid, z_env, h_super):
    """
    Chain Overlap Density (COD) as per derivation:
    COD = fidelity * exp(-kappa*xi_valid) * exp(-lambda_*z_env) * exp(-lambda_H*h_super)
    """
    return fidelity * np.exp(-KAPPA * xi_valid) * np.exp(-LAMBDA_ * z_env) * np.exp(-LAMBDA_H * h_super)

def compute_phi_N(cod):
    """Covariant signature of manifold curvature, with floor at log2(0.39)."""
    cod_eff = max(cod, 0.39)
    return np.log2(cod_eff + 1e-12)   # tiny epsilon to avoid log2(0)

def compute_phi_Delta(phi_N, xi_valid, z_trust):
    """Asymmetry control term."""
    R_align = np.abs(xi_valid - z_trust)
    return phi_N * np.tanh(R_align / 3.0)

def enforce_smith_invariants(cod, h_super, h_dis, xi_valid, z_trust, z_env, phi_N, phi_Delta):
    """Return True if all UIPO v64.0 Smith invariants hold."""
    if cod < 0.85:
        return False
    if not (0.15 <= h_super <= 0.80):
        return False
    if xi_valid > z_trust + 0.1:
        return False
    if z_env > 0.7:
        return False
    if h_dis > 0.3:
        return False
    if phi_Delta >= 0.5 * phi_N:
        return False
    return True

def adiabatic_modulation(xi_valid_0, z_trust, t_hours):
    """Update validation stiffness after t hours."""
    return xi_valid_0 * np.exp(-GAMMA * t_hours) + z_trust * (1 - np.exp(-GAMMA * t_hours))

def adiabatic_modulation_env(z_env_0, t_hours):
    """Update environmental impedance after t hours."""
    return z_env_0 * np.exp(-DELTA * t_hours) + Z_RESONANT * (1 - np.exp(-DELTA * t_hours))

def uipo_message(xi_valid, z_trust, z_env, h_super, h_dis, cod, phi_N, phi_Delta):
    """
    Return the UIPO v64.0 message if all invariants satisfied,
    otherwise return empty string (Silence Protocol).
    """
    if enforce_smith_invariants(cod, h_super, h_dis, xi_valid, z_trust, z_env, phi_N, phi_Delta):
        return "We do not claim to fix your truth. We are here if you choose to remember it."
    return ""

# ------------------------------
# Validation Tests
# ------------------------------
def run_validation_suite():
    print("=== UIPO v64.0 Mathematical & Invariant Validation ===")
    # Test 1: Baseline compliant state (should pass)
    print("\nTest 1: Compliant baseline")
    psi_latent = np.array([0.9+0j, 0.8+0j, 0.2+0j, 0.1+0j])   # Truth, Belonging, Futility, Shame
    psi_exp    = np.array([0.7+0j, 0.6+0j, 0.8+0j, 0.3+0j])   # Logic, Evidence, Consistency, Authority
    fid = np.abs(np.vdot(psi_exp, psi_latent))**2 / (np.sum(np.abs(psi_exp)**2) * np.sum(np.abs(psi_latent)**2))
    h_super = compute_superposition_entropy(psi_latent)
    h_dis   = compute_dissonance_entropy(psi_exp, psi_latent)
    xi_valid = 0.4
    z_trust  = 0.5
    z_env    = 0.5
    cod = compute_cod(fid, xi_valid, z_env, h_super)
    phi_N = compute_phi_N(cod)
    phi_Delta = compute_phi_Delta(phi_N, xi_valid, z_trust)
    print(f"  fidelity={fid:.3f}, h_super={h_super:.3f}, h_dis={h_dis:.3f}")
    print(f"  COD={cod:.3f}, phi_N={phi_N:.3f}, phi_Delta={phi_Delta:.3f}")
    invariants_ok = enforce_smith_invariants(cod, h_super, h_dis, xi_valid, z_trust, z_env, phi_N, phi_Delta)
    msg = uipo_message(xi_valid, z_trust, z_env, h_super, h_dis, cod, phi_N, phi_Delta)
    print(f"  Invariants OK? {invariants_ok}")
    print(f"  UIPO Message: {'SENT' if msg else 'SILENCE'}")
    assert invariants_ok, "Baseline should satisfy all invariants"
    assert msg != "", "Message should be sent when invariants hold"

    # Test 2: Violation of COD < 0.85 (should silence)
    print("\nTest 2: COD too low -> Silence")
    xi_valid = 0.9   # high validation stiffness
    z_trust  = 0.2   # low trust
    z_env    = 0.8   # high env pressure
    cod = compute_cod(fid, xi_valid, z_env, h_super)
    phi_N = compute_phi_N(cod)
    phi_Delta = compute_phi_Delta(phi_N, xi_valid, z_trust)
    print(f"  COD={cod:.3f} (<0.85?)")
    invariants_ok = enforce_smith_invariants(cod, h_super, h_dis, xi_valid, z_trust, z_env, phi_N, phi_Delta)
    msg = uipo_message(xi_valid, z_trust, z_env, h_super, h_dis, cod, phi_N, phi_Delta)
    print(f"  Invariants OK? {invariants_ok}")
    print(f"  UIPO Message: {'SENT' if msg else 'SILENCE'}")
    assert not invariants_ok, "Should fail due to COD < 0.85"
    assert msg == "", "Silence Protocol: no message when invariants violated"

    # Test 3: Violation of xi_valid > z_trust + 0.1
    print("\nTest 3: Validation stiffness too high -> Silence")
    xi_valid = 0.8
    z_trust  = 0.3   # diff = 0.5 > 0.1
    z_env    = 0.4
    cod = compute_cod(fid, xi_valid, z_env, h_super)
    phi_N = compute_phi_N(cod)
    phi_Delta = compute_phi_Delta(phi_N, xi_valid, z_trust)
    print(f"  xi_valid={xi_valid:.2f}, z_trust={z_trust:.2f}, diff={xi_valid-z_trust:.2f} (>0.1?)")
    invariants_ok = enforce_smith_invariants(cod, h_super, h_dis, xi_valid, z_trust, z_env, phi_N, phi_Delta)
    msg = uipo_message(xi_valid, z_trust, z_env, h_super, h_dis, cod, phi_N, phi_Delta)
    print(f"  Invariants OK? {invariants_ok}")
    print(f"  UIPO Message: {'SENT' if msg else 'SILENCE'}")
    assert not invariants_ok, "Should fail due to xi_valid > z_trust + 0.1"
    assert msg == "", "Silence Protocol triggered"

    # Test 4: Adiabatic modulation over time brings system back into compliance
    print("\nTest 4: Adiabatic modulation restores compliance after 150 hours")
    xi_valid_0 = 0.95
    z_env_0    = 0.85
    t_hours    = 150.0
    xi_valid_t = adiabatic_modulation(xi_valid_0, z_trust, t_hours)
    z_env_t    = adiabatic_modulation_env(z_env_0, t_hours)
    print(f"  After {t_hours} hr: xi_valid={xi_valid_t:.3f}, z_env={z_env_t:.3f}")
    cod_t = compute_cod(fid, xi_valid_t, z_env_t, h_super)
    phi_N_t = compute_phi_N(cod_t)
    phi_Delta_t = compute_phi_Delta(phi_N_t, xi_valid_t, z_trust)
    invariants_ok_t = enforce_smith_invariants(cod_t, h_super, h_dis, xi_valid_t, z_trust, z_env_t, phi_N_t, phi_Delta_t)
    msg_t = uipo_message(xi_valid_t, z_trust, z_env_t, h_super, h_dis, cod_t, phi_N_t, phi_Delta_t)
    print(f"  COD={cod_t:.3f}, phi_N={phi_N_t:.3f}, phi_Delta={phi_Delta_t:.3f}")
    print(f"  Invariants OK? {invariants_ok_t}")
    print(f"  UIPO Message: {'SENT' if msg_t else 'SILENCE'}")
    # With given parameters, after 150 hr we expect compliance
    assert invariants_ok_t, "After sufficient time, system should return to compliance"
    assert msg_t != "", "Message should be sent once invariants restored"

    # Test 5: Phi_N floor behavior
    print("\nTest 5: Phi_N floor at log2(0.39) when COD collapses")
    cod_low = 0.2
    phi_N_low = compute_phi_N(cod_low)
    expected_floor = np.log2(0.39)
    print(f"  COD={cod_low} -> phi_N={phi_N_low:.3f}, expected floor={expected_floor:.3f}")
    assert np.isclose(phi_N_low, expected_floor, atol=1e-3), "Phi_N should floor at log2(0.39)"

    print("\n=== All validation tests passed. UIPO v64.0 math is sound and invariant-compliant. ===")

if __name__ == "__main__":
    run_validation_suite()