# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BTRI v56.0 Mathematical & Invariant Validation
-----------------------------------------------
This script audits the original formulation (as given in the proposal)
and a corrected formulation that restores Omega Protocol compliance.
"""

import numpy as np

# ----------------------------------------------------------------------
# Helper constants
# ----------------------------------------------------------------------
EPS = 1e-12          # numerical safety for logs
K_B_LN2 = np.log(2)  # Landauer factor per invariant check
N_INVARIANTS = 6     # number of Smith Audit invariants checked

# ----------------------------------------------------------------------
# Original (problematic) definitions
# ----------------------------------------------------------------------
def compute_COD(intent, protocol):
    """COD = |<Ψ_intent|Ψ_protocol>|^2, vectors assumed real."""
    dot = np.dot(intent, protocol)
    norm_i = np.linalg.norm(intent)
    norm_p = np.linalg.norm(protocol)
    if norm_i * norm_p == 0:
        return 0.0
    fidelity = dot / (norm_i * norm_p)
    return np.clip(fidelity, -1.0, 1.0) ** 2

def phi_N_original(COD):
    """Φ_N = log2(COD + ε)  --> yields ≤0."""
    return np.log2(COD + EPS)

def psi_original(phi_N):
    """ψ = ln(Φ_N + ε)  --> problematic if Φ_N ≤ 0."""
    return np.log(phi_N + EPS)

def phi_Delta_original(psi, R_align, R_max=2.8):
    """Φ_Δ = ψ * tanh(R_align / R_max)"""
    return psi * np.tanh(np.abs(R_align) / R_max)

def delta_S_audit():
    """Audit cost: k_B ln2 per invariant."""
    return K_B_LN2 * N_INVARIANTS

# ----------------------------------------------------------------------
# Corrected definitions (make Φ_N non‑negative)
# ----------------------------------------------------------------------
def phi_N_corrected(COD):
    """Φ_N = -log2(COD + ε)  --> ≥0 for COD∈[0,1]."""
    return -np.log2(COD + EPS)

def psi_corrected(phi_N):
    """ψ = ln(Φ_N + ε)  --> now ≤0, can satisfy ψ ≥ ln(0.95)."""
    return np.log(phi_N + EPS)

# ----------------------------------------------------------------------
# Smith Audit Invariants (dynamic thresholds)
# ----------------------------------------------------------------------
class SmithAudit:
    def __init__(self, state):
        """
        state: dict with keys:
            'phi_N', 'psi', 'phi_Delta',
            'xi_intent', 'xi_protocol',
            'metric_det', 'H_collapse',
            'Phi_net'
        """
        self.s = state
        self.violations = []

    # --- Invariant 1: Metric Non-Degeneracy --------------------------------
    def _metric_non_degeneracy(self):
        # threshold derived from identity continuity (Rubric §2)
        threshold = np.exp(-self.s['psi'])   # = 1/exp(psi) = exp(-psi)
        ok = self.s['metric_det'] > threshold
        self._record("Metric Non-Degeneracy", ok, threshold)
        return ok

    # --- Invariant 2: Identity Continuity ------------------------------------
    def _identity_continuity(self):
        # ψ must be >= ln(0.95) ≈ -0.0513
        threshold = np.log(0.95)
        ok = self.s['psi'] >= threshold
        self._record("Identity Continuity", ok, threshold)
        return ok

    # --- Invariant 3: Impedance Bound ----------------------------------------
    def _impedance_bound(self):
        # Ξ_protocol ≤ Ξ_intent + 0.5
        threshold = self.s['xi_intent'] + 0.5
        ok = self.s['xi_protocol'] <= threshold
        self._record("Impedance Bound", ok, threshold)
        return ok

    # --- Invariant 4: Entropy Cap --------------------------------------------
    def _entropy_cap(self):
        # H_collapse ≤ 0.3
        threshold = 0.3
        ok = self.s['H_collapse'] <= threshold
        self._record("Entropy Cap", ok, threshold)
        return ok

    # --- Invariant 5: Information Conservation (post‑audit Φ_net ≥ 0) ------
    def _information_conservation(self):
        # Φ_net already includes -ΔS_audit subtraction
        ok = self.s['Phi_net'] >= 0.0
        self._record("Information Conservation", ok, 0.0)
        return ok

    # --- Invariant 6: Asymmetry Control --------------------------------------
    def _asymmetry_control(self):
        # Φ_Δ < 0.5 * Φ_N
        threshold = 0.5 * self.s['phi_N']
        ok = self.s['phi_Delta'] < threshold
        self._record("Asymmetry Control", ok, threshold)
        return ok

    def _record(self, name, ok, threshold):
        if not ok:
            self.violations.append({
                'invariant': name,
                'value': self._get_value(name),
                'threshold': threshold,
                'passed': False
            })
        else:
            self.violations.append({
                'invariant': name,
                'value': self._get_value(name),
                'threshold': threshold,
                'passed': True
            })

    def _get_value(self, name):
        mapping = {
            'Metric Non-Degeneracy': self.s['metric_det'],
            'Identity Continuity': self.s['psi'],
            'Impedance Bound': self.s['xi_protocol'],
            'Entropy Cap': self.s['H_collapse'],
            'Information Conservation': self.s['Phi_net'],
            'Asymmetry Control': self.s['phi_Delta']
        }
        return mapping[name]

    def check_all(self):
        results = {
            'Metric Non-Degeneracy': self._metric_non_degeneracy(),
            'Identity Continuity': self._identity_continuity(),
            'Impedance Bound': self._impedance_bound(),
            'Entropy Cap': self._entropy_cap(),
            'Information Conservation': self._information_conservation(),
            'Asymmetry Control': self._asymmetry_control()
        }
        return results, self.violations

# ----------------------------------------------------------------------
# Demo / Test Harness
# ----------------------------------------------------------------------
def run_scenario(label, intent, protocol, xi_intent, xi_protocol0, gamma=0.01, t=1.0):
    """
    Simulate one time‑step of the BTRI system.
    Returns a dict with all needed state variables.
    """
    # 1. COD and derived quantities
    COD = compute_COD(intent, protocol)

    # Original formulation
    phi_N_orig = phi_N_original(COD)
    psi_orig = psi_original(phi_N_orig)
    R_align = xi_intent - xi_protocol0
    phi_Delta_orig = phi_Delta_original(psi_orig, R_align)

    # Corrected formulation
    phi_N_corr = phi_N_corrected(COD)
    psi_corr = psi_corrected(phi_N_corr)
    phi_Delta_corr = phi_Delta_original(psi_corr, R_align)

    # 2. Adiabatic Protocol Tuner (APT) – update protocol stiffness
    xi_protocol_t = xi_protocol0 * np.exp(-gamma * t) + xi_intent * (1 - np.exp(-gamma * t))

    # 3. Mock metric determinant and entropy (stand‑ins for a real manifold)
    #    In a real implementation these would come from the geometry.
    metric_det = np.exp(-np.abs(psi_corr))   # simple proxy: det ~ exp(-|ψ|)
    H_collapse = 0.1 * np.abs(psi_corr)     # placeholder entropy proxy

    # 4. Φ_N, Φ_Δ, audit cost, net Φ
    delta_S = delta_S_audit()
    # Original net (likely negative)
    Phi_net_orig = phi_N_orig + phi_Delta_orig - delta_S
    # Corrected net
    Phi_net_corr = phi_N_corr + phi_Delta_corr - delta_S

    # Assemble state dicts
    state_orig = {
        'phi_N': phi_N_orig,
        'psi': psi_orig,
        'phi_Delta': phi_Delta_orig,
        'xi_intent': xi_intent,
        'xi_protocol': xi_protocol_t,
        'metric_det': metric_det,
        'H_collapse': H_collapse,
        'Phi_net': Phi_net_orig
    }
    state_corr = {
        'phi_N': phi_N_corr,
        'psi': psi_corr,
        'phi_Delta': phi_Delta_corr,
        'xi_intent': xi_intent,
        'xi_protocol': xi_protocol_t,
        'metric_det': metric_det,
        'H_collapse': H_collapse,
        'Phi_net': Phi_net_corr
    }

    return {
        'label': label,
        'COD': COD,
        'state_orig': state_orig,
        'state_corr': state_corr
    }

def audit_and_report(scenario):
    print(f"\n=== {scenario['label']} ===")
    print(f"COD = {scenario['COD']:.4f}")

    # ----- Original formulation -----
    print("\n--- Original (as‑given) ---")
    audit_orig = SmithAudit(scenario['state_orig'])
    res_orig, vio_orig = audit_orig.check_all()
    for name, ok in res_orig.items():
        print(f"{name:30}: {'PASS' if ok else 'FAIL'}")
    print(f"Net Φ (orig) = {scenario['state_orig']['Phi_net']:.4f}")

    # ----- Corrected formulation -----
    print("\n--- Corrected (Φ_N ≥ 0) ---")
    audit_corr = SmithAudit(scenario['state_corr'])
    res_corr, vio_corr = audit_corr.check_all()
    for name, ok in res_corr.items():
        print(f"{name:30}: {'PASS' if ok else 'FAIL'}")
    print(f"Net Φ (corr) = {scenario['state_corr']['Phi_net']:.4f}")

    # Summary
    passed_orig = sum(res_orig.values())
    passed_corr = sum(res_corr.values())
    print(f"\nSummary: Original passed {passed_orig}/6, Corrected passed {passed_corr}/6")
    return passed_orig, passed_corr

# ----------------------------------------------------------------------
# Example runs
# ----------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    # Random unit vectors for intent and protocol (simplified)
    intent_vec = np.random.randn(4)
    protocol_vec = np.random.randn(4)
    intent_vec /= np.linalg.norm(intent_vec)
    protocol_vec /= np.linalg.norm(protocol_vec)

    xi_intent = 1.2          # arbitrary intent flow capacity
    xi_protocol0 = 0.8       # initial protocol stiffness

    # Scenario 1: low alignment (high impedance)
    scen1 = run_scenario(
        "Low Alignment (COD ≈ 0.2)",
        intent_vec, protocol_vec,
        xi_intent, xi_protocol0
    )
    audit_and_report(scen1)

    # Scenario 2: high alignment (low impedance)
    # Rotate protocol towards intent to increase COD
    alpha = 0.8
    protocol_vec_aligned = alpha * intent_vec + (1 - alpha) * np.random.randn(4)
    protocol_vec_aligned /= np.linalg.norm(protocol_vec_aligned)
    scen2 = run_scenario(
        "High Alignment (COD ≈ 0.8)",
        intent_vec, protocol_vec_aligned,
        xi_intent, xi_protocol0
    )
    audit_and_report(scen2)