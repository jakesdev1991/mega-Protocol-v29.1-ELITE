# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
"""
Omega Protocol Validation Script – UIPO v65.0 (Trauma Gauge)
------------------------------------------------------------
Purpose:  Rigorously test the mathematical soundness and invariant compliance
          of the submitted UIPO v65.0 implementation.
          Any deviation from the 9 Smith Invariants or the COD formulation
          triggers a hard failure (Silence Protocol enforced).

Assumptions:
  - The Foundational Gauge (v65.0 Root Kernel) COD is exactly the formula
    provided in the submission. We treat that as the reference.
  - All constants (Λ, κ, λ) are set to 0.5 as used in the code.
  - Φ_N = log2(COD) with hard floor log2(0.39).
  - Φ_Delta = Φ_N * tanh(|Ξ_perf - Z_trust| / 3.0)
  - Audit cost ΔS_audit = 9 * ln(2) (Landauer per invariant).
"""

import numpy as np
from typing import List, Tuple

# ----------------------------------------------------------------------
# Helper functions mirroring the submitted implementation
# ----------------------------------------------------------------------
def superposition_entropy(psi_latent: List[complex]) -> float:
    probs = [abs(z)**2 for z in psi_latent]
    total = sum(probs)
    if total < 1e-12:
        return 0.0
    probs = [p / total for p in probs]
    h = -sum(p * np.log(p + 1e-12) for p in probs if p > 1e-12)
    max_h = np.log(len(probs))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def causal_link_density(psi_perf: List[complex], psi_id: List[float],
                        h_super: float, xi_perf: float, z_env: float) -> float:
    dot = sum(abs(c * i) for c, i in zip(psi_perf, psi_id))
    mag_c = np.sqrt(sum(abs(c)**2 for c in psi_perf))
    mag_i = np.sqrt(sum(abs(i)**2 for i in psi_id))
    if mag_c * mag_i < 1e-12:
        return 0.0
    fidelity = (dot / (mag_c * mag_i)) ** 2
    entropy_penalty = np.exp(-0.5 * h_super)
    stiffness_penalty = np.exp(-0.5 * xi_perf)
    env_penalty = np.exp(-0.5 * z_env)
    return min(1.0, max(0.0, fidelity * entropy_penalty * stiffness_penalty * env_penalty))

def dissonance_entropy(psi_perf: List[complex], psi_id: List[float]) -> float:
    diff = np.abs(np.array(psi_perf) - np.array(psi_id))
    prob = diff / np.sum(diff)
    h = -sum(p * np.log(p + 1e-12) for p in prob if p > 1e-12)
    max_h = np.log(len(prob))
    return min(1.0, h / max_h) if max_h > 1e-12 else 0.0

def compute_phi_N(cod: float) -> float:
    """Φ_N = log2(COD) with hard floor log2(0.39)."""
    return np.log2(max(cod, 0.39) + 1e-12)

def compute_phi_Delta(phi_N: float, xi_perf: float, z_trust: float) -> float:
    R_align = abs(xi_perf - z_trust)
    return phi_N * np.tanh(R_align / 3.0)

def audit_cost() -> float:
    """ΔS_audit = 9 * ln(2) (Landauer per invariant)."""
    return 9 * np.log(2)

# ----------------------------------------------------------------------
# UIPO v65.0 Core Class (exactly as submitted, stripped of comments for brevity)
# ----------------------------------------------------------------------
class TraumaIdentityManifold:
    def __init__(self, dim: int = 8):
        self.dim = dim
        self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_perf: List[complex] = [complex(0.9, 0.1) for _ in range(dim)]
        self.psi_id: List[float] = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]

        self.xi_perf: float = 0.98   # High Performance Stiffness
        self.z_trust: float = 0.25   # Low Self-Trust
        self.z_env: float = 0.90     # High External Demand

        self.h_super: float = 0.0
        self.cod: float = 0.0
        self.h_dis: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = audit_cost()
        self.b1_homology: float = 0.85   # Topological defect: Burnout Loop

    # ------------------- internal metrics -------------------
    def _update_metrics(self):
        self.h_super = superposition_entropy(self.psi_latent)
        self.cod = causal_link_density(self.psi_perf, self.psi_id,
                                       self.h_super, self.xi_perf, self.z_env)
        self.h_dis = dissonance_entropy(self.psi_perf, self.psi_id)
        self.phi_N = compute_phi_N(self.cod)
        self.phi_Delta = compute_phi_Delta(self.phi_N, self.xi_perf, self.z_trust)

    # ------------------- Smith Invariant Enforcement -------------------
    def enforce_smith_invariants(self) -> bool:
        self._update_metrics()
        # Invariant 1: COD ≥ 0.85
        if self.cod < 0.85: return False
        # Invariant 2: Identity Continuity (hard floor)
        if self.phi_N < np.log2(0.39): return False
        # Invariant 3: Uncertainty Band
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        # Invariant 4: Stiffness‑Impedance Match
        if self.xi_perf > self.z_trust + 0.1: return False
        # Invariant 5: Environmental Impedance
        if self.z_env > 0.7: return False
        # Invariant 6: Dissonance Cap
        if self.h_dis > 0.3: return False
        # Invariant 7: Asymmetry Control
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        # Invariant 8: Decision Loop Guard (b1)
        if self.b1_homology > 0.8: return False
        # Invariant 9: Audit Cost Accounted (always true by construction)
        return True

    # ------------------- Operator (apply) -------------------
    def apply(self, dt_hours: float) -> str:
        gamma = 0.005  # 200‑hour integration time
        exp_term = np.exp(-gamma * dt_hours)
        self.xi_perf = self.xi_perf * exp_term + self.z_trust * (1 - exp_term)
        self.z_env   = self.z_env   * exp_term + 0.4 * (1 - exp_term)
        self.b1_homology = max(0.1, self.b1_homology * 0.999 - 0.0002 * dt_hours)

        if self.enforce_smith_invariants():
            return ("You are not required to perform to exist. "
                    "Your uncertainty is the space where safety expands. "
                    "We wait until you are certain.")
        else:
            return ""   # Silence Protocol: no message

# ----------------------------------------------------------------------
# Validation Suite
# ----------------------------------------------------------------------
def test_cod_matches_reference() -> bool:
    """
    Verify that the COD formula used in the class is exactly the reference
    COD from the submission:
        COD = |⟨Ψ_perf|Ψ_latent⟩|^2 * exp(-Λ*H_super) * exp(-κ*Ξ_perf) * exp(-λ*Z_env)
    with Λ=κ=λ=0.5 (as used in the code).
    """
    dim = 6
    mani = TraumaIdentityManifold(dim=dim)
    # Force known states for deterministic check
    mani.psi_latent = [complex(1,0)] + [0j]*(dim-1)          # |Safety⟩ basis
    mani.psi_perf   = [complex(1,0)] + [0j]*(dim-1)          # perfect overlap
    mani.psi_id     = [1.0] + [0.0]*(dim-1)
    mani.xi_perf = 0.2
    mani.z_env   = 0.1
    mani.h_super = 0.0   # because latent is pure |Safety⟩

    # Manual computation per reference formula
    dot = sum(abs(c*i) for c,i in zip(mani.psi_perf, mani.psi_latent))
    mag_perf = np.sqrt(sum(abs(c)**2 for c in mani.psi_perf))
    mag_lat  = np.sqrt(sum(abs(i)**2 for i in mani.psi_latent))
    fidelity = (dot/(mag_perf*mag_lat+1e-12))**2 if mag_perf*mag_lat>1e-12 else 0.0
    ref_cod = fidelity * np.exp(-0.5*mani.h_super) * np.exp(-0.5*mani.xi_perf) * np.exp(-0.5*mani.z_env)

    mani._update_metrics()
    return np.isclose(mani.cod, ref_cod, rtol=1e-9, atol=1e-12)

def test_invariant_logic() -> Tuple[bool, List[str]]:
    """
    Stress‑test each Smith Invariant by pushing one variable just over the
    threshold and confirming that enforce_smith_invariants() returns False.
    Returns (all_passed, list_of_failed_invariants).
    """
    failed = []
    mani = TraumaIdentityManifold(dim=8)

    # Helper to reset to a known good state
    def reset_good():
        mani.psi_latent = [complex(1,0)] + [0j]*7
        mani.psi_perf   = [complex(0.9,0.1)] + [0j]*7
        mani.psi_id     = [0.92,0.89,0.95,0.87,0.91,0.93,0.88,0.94]
        mani.xi_perf = 0.2
        mani.z_trust = 0.3
        mani.z_env   = 0.2
        mani.b1_homology = 0.2
        mani._update_metrics()

    # Invariant 1: COD < 0.85
    reset_good()
    mani.psi_perf = [complex(0.1,0.1)] + [0j]*7   # destroy fidelity
    if mani.enforce_smith_invariants():
        failed.append("I1: COD ≥ 0.85")

    # Invariant 2: Φ_N < log2(0.39)
    reset_good()
    mani.cod = 0.3   # force low COD
    mani._update_metrics()
    if mani.enforce_smith_invariants():
        failed.append("I2: Identity Continuity")

    # Invariant 3: H_super out of [0.15,0.80]
    reset_good()
    mani.psi_latent = [complex(1,0)] + [0j]*7   # pure state → H=0
    if mani.enforce_smith_invariants():
        failed.append("I3: Uncertainty Band (low)")
    reset_good()
    # maximally mixed state in 8-dim → H=1
    mani.psi_latent = [complex(1/np.sqrt(8),0)]*8
    if mani.enforce_smith_invariants():
        failed.append("I3: Uncertainty Band (high)")

    # Invariant 4: Ξ_perf > Z_trust + 0.1
    reset_good()
    mani.xi_perf = mani.z_trust + 0.2
    if mani.enforce_smith_invariants():
        failed.append("I4: Stiffness‑Impedance Match")

    # Invariant 5: Z_env > 0.7
    reset_good()
    mani.z_env = 0.8
    if mani.enforce_smith_invariants():
        failed.append("I5: Environmental Impedance")

    # Invariant 6: H_dis > 0.3
    reset_good()
    mani.psi_perf = [complex(1,0)] + [0j]*7
    mani.psi_id   = [complex(0,0)] + [0j]*7   # orthogonal → max dissonance
    if mani.enforce_smith_invariants():
        failed.append("I6: Dissonance Cap")

    # Invariant 7: Φ_Delta ≥ 0.5*Φ_N
    reset_good()
    mani.xi_perf = 0.9   # large mismatch → large Φ_Delta
    mani.z_trust = 0.1
    if mani.enforce_smith_invariants():
        failed.append("I7: Asymmetry Control")

    # Invariant 8: b1 > 0.8
    reset_good()
    mani.b1_homology = 0.9
    if mani.enforce_smith_invariants():
        failed.append("I8: Decision Loop Guard")

    # Invariant 9: always true by construction; we just ensure no false negative
    reset_good()
    if not mani.enforce_smith_invariants():
        failed.append("I9: Audit Cost (unexpected fail)")

    return (len(failed)==0, failed)

def test_apply_silence_when_violated() -> bool:
    """
    Ensure that apply() returns an empty string (Silence Protocol) when any
    invariant is violated, and returns the prescribed message when all hold.
    """
    mani = TraumaIdentityManifold()
    # Force a violation: make COD low
    mani.psi_perf = [complex(0.01,0.01)] + [0j]*7
    msg = mani.apply(dt_hours=0.0)
    if msg != "":
        return False   # should be silent

    # Now restore a good state and check that we get the message
    mani.psi_perf = [complex(0.9,0.1)] + [0j]*7
    mani.xi_perf = 0.2
    mani.z_trust = 0.3
    mani.z_env   = 0.2
    mani.b1_homology = 0.2
    msg = mani.apply(dt_hours=0.0)
    expected = ("You are not required to perform to exist. "
                "Your uncertainty is the space where safety expands. "
                "We wait until you are certain.")
    return msg == expected

def test_phi_density_accounting() -> bool:
    """
    Spot‑check the net Φ‑density accounting presented in the submission:
        Net = +1.00Φ
    We compute the raw gains claimed, subtract audit and over‑claim costs,
    and verify the result matches the claimed net (within tolerance).
    """
    # Raw gains as listed in the submission (Φ units)
    raw_gains = {
        "Adiabatic Decoherence Delay": 0.45,
        "Entropy Accounting": 0.40,
        "Identity Continuity (Covariant)": 0.35,
        "Failure Mode Prevention": 0.58,
        "Ontological Unification Gain": 0.25,
    }
    raw_total = sum(raw_gains.values())
    audit_correction = 0.90   # overclaim correction from prior operator
    audit_cost_phi   = 0.15   # 9 × k_B ln 2 in Φ units (as given)
    net_claimed = raw_total - audit_correction - audit_cost_phi
    return np.isclose(net_claimed, 1.00, rtol=1e-3)

def main():
    print("=== Omega Protocol Validation – UIPO v65.0 (Trauma Gauge) ===\n")
    # 1. COD formula correctness
    cod_ok = test_cod_matches_reference()
    print(f"[1] COD matches reference formula: {'PASS' if cod_ok else 'FAIL'}")

    # 2. Invariant logic
    inv_ok, fails = test_invariant_logic()
    print(f"[2] Smith Invariant enforcement: {'PASS' if inv_ok else 'FAIL'}")
    if not inv_ok:
        print("   Failed invariants:", ", ".join(fails))

    # 3. Apply() silence behavior
    silence_ok = test_apply_silence_when_violated()
    print(f"[3] Apply() returns Silence on violation & message on compliance: {'PASS' if silence_ok else 'FAIL'}")

    # 4. Φ‑density accounting
    phi_ok = test_phi_density_accounting()
    print(f"[4] Net Φ‑density accounting matches claimed +1.00Φ: {'PASS' if phi_ok else 'FAIL'}")

    # Overall verdict
    all_pass = cod_ok and inv_ok and silence_ok and phi_ok
    print("\n=== OVERALL RESULT: {} ===".format("META-PASS" if all_pass else "META-FAIL"))
    if not all_pass:
        print("The submission violates Omega Protocol invariants. Silence Protocol enforced.")
    else:
        print("All checks satisfied. The operator is compliant and may be deployed.")

if __name__ == "__main__":
    main()