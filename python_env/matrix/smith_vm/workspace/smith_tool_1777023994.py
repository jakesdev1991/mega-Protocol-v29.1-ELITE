# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import math
from typing import Dict, Tuple, List

def validate_omega_prototype(params: Dict) -> Tuple[bool, List[str]]:
    """
    Validate a Quantum-Enhanced Children's Footwear design against the
    Omega Protocol invariants described in the audit.

    Parameters
    ----------
    params : dict
        Must contain the following keys (all values are floats unless noted):
        - b0: int or float > 0               (Betti number b0 of the adaptive lattice)
        - H_cond: float > 0                  (Shannon conditional entropy)
        - xi_N: float in [0, 1]              (Newtonian stiffness)
        - xi_Delta: float in [0, 1]          (Asymmetry stiffness)
        - R: float                           (Ricci curvature of the effective spacetime)
        - R_max: float > 0                   (curvature bound)
        - phi_n: float > 0                   (metric coupling base)
        - Psi_id_user: float                 (user‑identity continuity metric)
        - E: float                           (power consumption in Watts)
        - H_top: float                       (topological entropy measure)
        - context_match: bool                (True if bio‑ and terrain‑context intersect)

    Returns
    -------
    (is_compliant, messages) :
        is_compliant : bool
            True iff *all* invariants hold.
        messages : list of str
            Human‑readable explanations for each invariant (pass/fail).
    """
    msgs = []
    ok = True

    # ---- Helper to append result -------------------------------------------------
    def add_check(name: str, condition: bool, detail: str = ""):
        nonlocal ok
        if condition:
            msgs.append(f"[PASS] {name}" + (f": {detail}" if detail else ""))
        else:
            msgs.append(f"[FAIL] {name}" + (f": {detail}" if detail else ""))
            ok = False

    # ---- Extract parameters -------------------------------------------------------
    try:
        b0          = float(params["b0"])
        H_cond      = float(params["H_cond"])
        xi_N        = float(params["xi_N"])
        xi_Delta    = float(params["xi_Delta"])
        R           = float(params["R"])
        R_max       = float(params["R_max"])
        phi_n       = float(params["phi_n"])
        Psi_id_user = float(params["Psi_id_user"])
        E           = float(params["E"])
        H_top       = float(params["H_top"])
        context_match = bool(params["context_match"])
    except KeyError as e:
        raise ValueError(f"Missing required parameter: {e}")

    # ---- Basic domain checks ------------------------------------------------------
    add_check("b0 > 0", b0 > 0, f"b0 = {b0}")
    add_check("H_cond > 0", H_cond > 0, f"H_cond = {H_cond}")
    add_check("0 <= xi_N <= 1", 0.0 <= xi_N <= 1.0, f"xi_N = {xi_N}")
    add_check("0 <= xi_Delta <= 1", 0.0 <= xi_Delta <= 1.0, f"xi_Delta = {xi_Delta}")
    add_check("R_max > 0", R_max > 0, f"R_max = {R_max}")
    add_check("phi_n > 0 (for log)", phi_n > 0, f"phi_n = {phi_n}")

    # ---- Ricci curvature bound ----------------------------------------------------
    add_check("-R_max <= R <= R_max", -R_max <= R <= R_max,
              f"R = {R}, bound = ±{R_max}")

    # ---- Metric coupling (psi) ----------------------------------------------------
    psi = math.log(phi_n)   # natural log, as per ψ = ln(φ_n)
    add_check("psi is real (phi_n>0)", True, f"psi = ln(phi_n) = {psi:.4f}")

    # ---- Newtonian component ------------------------------------------------------
    # log2 argument must be >0
    log_arg = b0 / H_cond
    add_check("b0 / H_cond > 0", log_arg > 0,
              f"b0/H_cond = {log_arg:.4f}")
    if log_arg > 0:
        Phi_N = math.log2(log_arg) * xi_N
        add_check("Phi_N computed", True, f"Phi_N = {Phi_N:.4f}")
    else:
        Phi_N = float('-inf')
        add_check("Phi_N computed", False, "log argument non‑positive")

    # ---- Asymmetry component ------------------------------------------------------
    tanh_arg = R / R_max
    tanh_val = math.tanh(tanh_arg)
    Phi_Delta = psi * tanh_val * xi_Delta
    add_check("Phi_Delta computed", True,
              f"tanh(R/R_max) = {tanh_val:.4f}, Phi_Delta = {Phi_Delta:.4f}")

    # ---- Total Φ positivity -------------------------------------------------------
    Phi_total = Phi_N + Phi_Delta
    add_check("Φ_total >= 0", Phi_total >= 0,
              f"Φ_N + Φ_Δ = {Phi_total:.4f}")

    # ---- Newtonian floor (no informational freeze) -------------------------------
    add_check("Φ_N >= 0.1", Phi_N >= 0.1,
              f"Φ_N = {Phi_N:.4f}")

    # ---- Asymmetry ceiling (no shredding event) ----------------------------------
    add_check("Φ_Δ <= 0.95", Phi_Delta <= 0.95,
              f"Φ_Δ = {Phi_Delta:.4f}")

    # ---- Asymmetry‑to‑Newtonian ratio (safety) -----------------------------------
    if Phi_N > 0:
        ratio = Phi_Delta / Phi_N
        add_check("Φ_Δ / Φ_N < 0.5", ratio < 0.5,
                  f"ratio = {ratio:.4f}")
    else:
        add_check("Φ_Δ / Φ_N < 0.5 (Φ_N>0 required)", False,
                  f"Φ_N = {Phi_N:.4f} (must be >0)")

    # ---- Context match ------------------------------------------------------------
    add_check("Context_bio ∩ Context_terrain ≠ ∅", context_match,
              f"context_match = {context_match}")

    # ---- User‑identity continuity -------------------------------------------------
    add_check("Psi_id_user > 0.95", Psi_id_user > 0.95,
              f"Psi_id_user = {Psi_id_user:.4f}")

    # ---- Energy bound -------------------------------------------------------------
    add_check("E <= 5 W", E <= 5.0,
              f"E = {E:.2f} W")

    # ---- Topological‑entropy mode (low‑power trigger) ----------------------------
    add_check("H_top <= 0.85 (normal mode)", H_top <= 0.85,
              f"H_top = {H_top:.4f}")

    return ok, msgs


# ------------------------------------------------------------------------------
# Example usage ---------------------------------------------------------------
if __name__ == "__main__":
    # A *plausible* set of parameters that should pass all checks.
    example = {
        "b0": 2.0,               # at least one connected component + one loop
        "H_cond": 0.5,           # conditional entropy < 1 bit
        "xi_N": 0.7,
        "xi_Delta": 0.3,
        "R": 0.2,                # small positive curvature
        "R_max": 1.0,
        "phi_n": 2.0,            # ln(2) ≈ 0.693
        "Psi_id_user": 0.97,
        "E": 3.8,                # Watts
        "H_top": 0.6,
        "context_match": True
    }

    compliant, messages = validate_omega_prototype(example)
    print("\n".join(messages))
    print("\nOVERALL:", "PASS" if compliant else "FAIL")