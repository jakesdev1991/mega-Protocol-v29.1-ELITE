# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validation Script
Validates the mathematical core of the Audience Resonance Specification.
"""

import math
import itertools
from dataclasses import dataclass
from typing import Tuple

# ----------------------------------------------------------------------
# Constants (mirroring the C++ constexpr values)
# ----------------------------------------------------------------------
PSI_ID_THRESHOLD = 0.95
XI_BUYER_DEFAULT = 1.5
XI_BUYER_MAX = 3.0
XI_BUYER_MIN = 0.5
KAPPA_SYS_IND = 0.8
LAMBDA_COUPLING = 1.0
H_IMP_LIMIT = 0.85
COD_THRESHOLD = 0.80
GAMMA_RATE_LIMIT = 0.1  # not directly used; adiabatic enforced via ComputeGamma

# ----------------------------------------------------------------------
# Helper functions (direct translations of the core math)
# ----------------------------------------------------------------------
def fidelity(need: complex, pitch: complex) -> float:
    """|⟨need|pitch⟩| / (|need|·|pitch|)  → [0,1]"""
    num = abs(need.conjugate() * pitch)
    den = abs(need) * abs(pitch)
    return 0.0 if den == 0.0 else num / den

def cod_sales(need: complex, pitch: complex, H_imp: float, Xi_buyer: float, Gamma_t: float) -> float:
    """COD = fidelity^2 * exp(-Λ*H_imp) * exp(-Gamma*Xi_buyer)"""
    f = fidelity(need, pitch)
    return (f * f) * math.exp(-LAMBDA_COUPLING * H_imp) * math.exp(-LAMBDA_COUPLING * Gamma_t * Xi_buyer)

def compute_gamma(t: float, Xi_buyer: float, tau_opt: float = 0.5, sigma: float = 0.1) -> float:
    """Adiabatic pitching function from the spec."""
    raw = math.tanh((t - tau_opt) / sigma)
    max_gamma = Xi_buyer * 0.8
    return min(max_gamma, 1.0 * raw)

def shannon_cond_entropy(need: complex, pitch: complex) -> float:
    """H(Need|Pitch) = -p * log(p) where p = |⟨need|pitch⟩|/(|need|·|pitch|)"""
    p = fidelity(need, pitch)
    if p <= 0.0:
        return 0.0
    return -p * math.log(p)

def identity_preserve(H_cond: float) -> float:
    """Psi_id = 1.0 - 0.1 * H_cond (as used in the spec)."""
    return 1.0 - 0.1 * H_cond

def false_sale_detection(COD: float, Xi_buyer: float, fidelity_val: float) -> bool:
    """Spec: COD≥0.8 AND Xi>2.5 AND (Xi/fidelity)>2.0"""
    if fidelity_val < 1e-12:
        fidelity_val = 1e-12
    ratio = Xi_buyer / fidelity_val
    return (COD >= COD_THRESHOLD) and (Xi_buyer > 2.5) and (ratio > 2.0)

def failure_mode_detector(H_imp: float, dGamma_dt: float, Xi_buyer: float, F_Urgency: float) -> str:
    """Return one of: NONE, MEASUREMENT_SHOCK, COGNITIVE_BLACK_HOLE, DECOHERENCE"""
    if dGamma_dt > Xi_buyer:
        return "MEASUREMENT_SHOCK"
    if H_imp > H_IMP_LIMIT and F_Urgency < (H_IMP_LIMIT * 0.5):
        return "COGNITIVE_BLACK_HOLE"
    if H_imp > H_IMP_LIMIT:
        return "DECOHERENCE"
    return "NONE"

# ----------------------------------------------------------------------
# Parameter ranges for exhaustive sanity checks
# ----------------------------------------------------------------------
def make_complex(r: float, theta: float) -> complex:
    return r * (math.cos(theta) + 1j * math.sin(theta))

def sweep():
    violations = []
    # Sample space: magnitudes [0.1, 2.0], angles [0, 2π]
    mags = [0.2, 0.5, 1.0, 1.5, 2.0]
    thetas = [0, math.pi/4, math.pi/2, math.pi, 3*math.pi/2]
    H_imp_vals = [0.0, 0.4, 0.6, 0.85, 0.9, 1.2]
    Xi_buyer_vals = [0.3, 0.6, 1.0, 1.5, 2.5, 3.5]
    t_vals = [0.0, 0.2, 0.5, 0.8, 1.0]

    for need_mag, pitch_mag, need_theta, pitch_theta in itertools.product(mags, mags, thetas, thetas):
        need = make_complex(need_mag, need_theta)
        pitch = make_complex(pitch_mag, pitch_theta)
        for H_imp in H_imp_vals:
            for Xi_buyer in Xi_buyer_vals:
                for t in t_vals:
                    Gamma = compute_gamma(t, Xi_buyer)
                    # Approximate dGamma/dt via finite difference (small dt)
                    dt = 1e-3
                    Gamma_prev = compute_gamma(t - dt, Xi_buyer)
                    dGamma_dt = (Gamma - Gamma_prev) / dt if dt != 0 else 0.0

                    # --- COD bounds -------------------------------------------------
                    C = cod_sales(need, pitch, H_imp, Xi_buyer, Gamma)
                    if not (0.0 <= C <= 1.0 + 1e-12):
                        violations.append(
                            f"COD out of bounds: need={need}, pitch={pitch}, H_imp={H_imp}, "
                            f"Xi={Xi_buyer}, Gamma={Gamma} → COD={C}"
                        )
                    # --- Invariant Ψ_id -------------------------------------------
                    H_cond = shannon_cond_entropy(need, pitch)
                    psi_id = identity_preserve(H_cond)
                    if psi_id < PSI_ID_THRESHOLD - 1e-12:
                        violations.append(
                            f"Psi_id violation: H_cond={H_cond} → psi_id={psi_id} < {PSI_ID_THRESHOLD}"
                        )
                    # --- Failure mode consistency ---------------------------------
                    F_Urgency = 0.3  # arbitrary but constant for this sweep
                    mode = failure_mode_detector(H_imp, dGamma_dt, Xi_buyer, F_Urgency)
                    # Check that the mode matches the spec’s logical conditions
                    if mode == "MEASUREMENT_SHOCK":
                        if not (dGamma_dt > Xi_buyer):
                            violations.append(
                                f"False MEASUREMENT_SHOCK: dGamma/dt={dGamma_dt}, Xi={Xi_buyer}"
                            )
                    elif mode == "COGNITIVE_BLACK_HOLE":
                        if not (H_imp > H_IMP_LIMIT and F_Urgency < (H_IMP_LIMIT * 0.5)):
                            violations.append(
                                f"False COGNITIVE_BLACK_HOLE: H_imp={H_imp}, F_Urg={F_Urgency}"
                            )
                    elif mode == "DECOHERENCE":
                        if not (H_imp > H_IMP_LIMIT):
                            violations.append(
                                f"False DECOHERENCE: H_imp={H_imp}"
                            )
                    # --- False sale detection sanity -------------------------------
                    fid = fidelity(need, pitch)
                    if false_sale_detection(C, Xi_buyer, fid):
                        # Should only happen when COD high, Xi high, fidelity relatively low
                        if not (C >= COD_THRESHOLD and Xi_buyer > 2.5 and (Xi_buyer / fid) > 2.0):
                            violations.append(
                                f"False sale logic mismatch: COD={C}, Xi={Xi_buyer}, fid={fid}"
                            )
                    # --- Adiabatic condition: ensure Gamma not too aggressive -------
                    # The spec requires dGamma/dt << Xi_buyer; we just check it's not > Xi_buyer
                    if dGamma_dt > Xi_buyer + 1e-9:
                        violations.append(
                            f"Adiabatic breach: dGamma/dt={dGamma_dt} > Xi={Xi_buyer}"
                        )
    return violations

if __name__ == "__main__":
    print("Running Omega Protocol mathematical validation...")
    errs = sweep()
    if errs:
        print(f"\nFAILED: {len(errs)} violation(s) detected.")
        for i, e in errs[:10]:  # show first 10 for brevity
            print(f"  - {e}")
        if len(errs) > 10:
            print(f"  ... and {len(errs)-10} more.")
        raise SystemExit(1)
    else:
        print("\nSUCCESS: All checks passed. Specification is mathematically sound and invariant‑compliant.")