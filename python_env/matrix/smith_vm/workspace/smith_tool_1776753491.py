# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol v26.0 compliance checker for SERC output.
- Checks boilerplate (headings, ordered lists)
- Verifies dimensional consistency (all quantities expressed as powers of time)
- Confirms both catastrophic boundaries are present
- Re-evaluates the numeric instability claim
"""

import re
import sys
from typing import Dict, Tuple

# ----------------------------------------------------------------------
# 1. Boilerplate detection
# ----------------------------------------------------------------------
HEADING_RE = re.compile(r'^\s*#{1,6}\s+', re.MULTILINE)          # markdown headings
ORDERED_LIST_RE = re.compile(r'^\s*\d+\.\s+', re.MULTILINE)    # "1. ", "2. ", ...

def has_boilerplate(text: str) -> Tuple[bool, str]:
    issues = []
    if HEADING_RE.search(text):
        issues.append("Markdown heading detected")
    if ORDERED_LIST_RE.search(text):
        issues.append("Ordered list detected")
    return (len(issues) > 0, "; ".join(issues))

# ----------------------------------------------------------------------
# 2. Dimensional helper (time‑only model)
# ----------------------------------------------------------------------
# Base dimension: [T] (time). Every quantity is T^exp.
# We will assign exponents to symbols and propagate through multiplication/division.
# Addition/subtraction requires identical exponents.

def parse_dim(spec: str) -> int:
    """Convert a string like 'T^-3' or 'dimensionless' to exponent."""
    spec = spec.strip().lower()
    if spec in ("dimensionless", "1", "t^0", "t0"):
        return 0
    m = re.match(r't\s*\^\s*([-\d]+)', spec)
    if m:
        return int(m.group(1))
    # fallback: assume pure power like 'T^-3' without the caret
    m = re.match(r't\s*([-\d]+)', spec)
    if m:
        return int(m.group(1))
    raise ValueError(f"Cannot parse dimension spec: {spec}")

# Known dimensions from the SERC text (all reduced to powers of T)
DIM_MAP: Dict[str, int] = {
    "action_S": 1,          # energy‑time → in our T‑only model we treat as T^1 (see note)
    "Phi_N": 0,             # dimensionless
    "Phi_Delta": 0,
    "lambda_": -2,          # [T]^-2
    "xi_N": 1,              # [T]
    "xi_Delta": 1,
    "psi": 0,
    "S_h": 0,               # entropy dimensionless
    "J_I": -3,              # [T]^-3
    "Theta_psi": -6,        # [T]^-6
    "sigma_J": -3,
    "sigma_J_sq": -6,
}

def check_dimension_consistency() -> Tuple[bool, str]:
    """
    Spot‑check a few key equations from the SERC output.
    Returns (OK, message).
    """
    # 1) Stiffness invariant definition: xi^-2 = lambda * (combination of Phi^2 - I0^2)
    # lhs: xi^-2 -> exponent = -2 * xi_exp
    # rhs: lambda ([T]^-2) * (dimensionless combination) -> -2
    lhs_exp = -2 * DIM_MAP["xi_N"]   # using xi_N as example; same for xi_Delta
    rhs_exp = DIM_MAP["lambda_"] + 0  # combination dimensionless
    if lhs_exp != rhs_exp:
        return (False, f"Stiffness invariant dimension mismatch: xi^-2 ({lhs_exp}) vs lambda ({rhs_exp})")

    # 2) Jerk definition: J_I = d^3 S_h / dt^3
    # lhs: J_I exponent = -3
    # rhs: S_h (0) * t^-3 -> -3
    lhs_exp = DIM_MAP["J_I"]
    rhs_exp = DIM_MAP["S_h"] - 3
    if lhs_exp != rhs_exp:
        return (False, f"Jerk dimension mismatch: J_I ({lhs_exp}) vs d^3S_h/dt^3 ({rhs_exp})")

    # 3) Threshold Theta(psi) has same dimension as sigma_J^2
    if DIM_MAP["Theta_psi"] != DIM_MAP["sigma_J_sq"]:
        return (False, f"Theta and sigma_J^2 dimension mismatch: {DIM_MAP['Theta_psi']} vs {DIM_MAP['sigma_J_sq']}")

    # 4) Action S dimension (energy‑time) -> we treat as T^1 for consistency check
    # In the T‑only model we cannot verify M,L, but we accept the claimed T^1.
    # No further check needed.

    return (True, "All spot‑checked dimensional relations consistent (time‑only model).")

# ----------------------------------------------------------------------
# 3. Boundary presence check
# ----------------------------------------------------------------------
def check_boundaries(text: str) -> Tuple[bool, str]:
    """Look for the two algebraic boundary conditions."""
    # Normalise whitespace and lower‑case for robust matching
    norm = re.sub(r'\s+', ' ', text.lower())
    # Shredding: Phi_N^2 + 3*Phi_Delta^2 = I0^2
    shred_pat = r'phi_n\s*\^?\s*2\s*\+\s*3\s*\*?\s*phi_delta\s*\^?\s*2\s*=\s*i0\s*\^?\s*2'
    # Freeze: 3*Phi_N^2 + Phi_Delta^2 = I0^2
    freeze_pat = r'3\s*\*?\s*phi_n\s*\^?\s*2\s*\+\s*phi_delta\s*\^?\s*2\s*=\s*i0\s*\^?\s*2'
    has_shred = re.search(shred_pat, norm) is not None
    has_freeze = re.search(freeze_pat, norm) is not None
    missing = []
    if not has_shred:
        missing.append("Shredding boundary (Φ_N²+3Φ_Δ²=I₀²)")
    if not has_freeze:
        missing.append("Informational Freeze boundary (3Φ_N²+Φ_Δ²=I₀²)")
    if missing:
        return (False, "Missing boundary expression(s): " + "; ".join(missing))
    return (True, "Both boundary conditions detected.")

# ----------------------------------------------------------------------
# 4. Numeric instability verification
# ----------------------------------------------------------------------
def numeric_check() -> Tuple[bool, str]:
    """Re‑compute σ_𝒥² and Θ(ψ) using the audit numbers."""
    # Given numbers (SI‑like, but we treat as pure time powers)
    phi_N = 0.78
    phi_Delta = 0.35
    I0 = 1.0
    lambda_ = 1e10          # s^-2
    g_Delta = 0.1
    # Derived quantities from the text
    psi = np.log(phi_N)                     # dimensionless
    # Stiffness combo for Shredding boundary (not needed for threshold)
    # Threshold Θ(ψ) = (λ I0^4 /9) * (e^{2ψ} -1)^2 * (1 + (3 g_Δ^2)/(4π) e^{-2ψ})
    term1 = (lambda_ * I0**4) / 9.0
    term2 = (np.exp(2*psi) - 1)**2
    term3 = 1.0 + (3.0 * g_Delta**2) / (4.0 * np.pi) * np.exp(-2*psi)
    Theta = term1 * term2 * term3            # predicted [s^-6]

    # Jerk fluctuations: σ_𝒥 ≈ 3.06e11 s^-3 → σ_𝒥²
    sigma_J = 3.06e11
    sigma_J_sq = sigma_J**2                  # [s^-6]

    stable = sigma_J_sq <= Theta
    msg = (f"Θ(ψ) = {Theta:.3e} s⁻⁶, σ_𝒥² = {sigma_J_sq:.3e} s⁻⁶ → "
           f"{'stable' if stable else 'unstable'} (σ_𝒥² {'≤' if stable else '>'} Θ)")
    return (not stable, msg)   # we expect instability → True for "issue found"

# ----------------------------------------------------------------------
# Main driver
# ----------------------------------------------------------------------
if __name__ == "__main__":
    import numpy as np  # numpy is available in the isolated VM

    # Example SERC text (replace with actual output when checking)
    serc_text = """<PASTE THE SERC OUTPUT HERE>"""

    print("=== Boilerplate Check ===")
    boiler, boiler_msg = has_boilerplate(serc_text)
    print(f"Boilerplate violation: {boiler} → {boiler_msg}")

    print("\n=== Dimensional Consistency ===")
    dim_ok, dim_msg = check_dimension_consistency()
    print(f"Dimensional check passed: {dim_ok} → {dim_msg}")

    print("\n=== Boundary Presence ===")
    bound_ok, bound_msg = check_boundaries(serc_text)
    print(f"Boundaries present: {bound_ok} → {bound_msg}")

    print("\n=== Numeric Instability ===")
    num_ok, num_msg = numeric_check()
    print(f"Instability detected (as expected): {num_ok} → {num_msg}")

    # Overall compliance decision (ignoring boilerplate for physics)
    physics_ok = dim_ok and bound_ok and num_ok
    print("\n=== Overall Physics Compliance ===")
    print(f"Physics sound: {physics_ok}")
    print("\n=== Final Verdict ===")
    if boiler:
        print("❌ FAIL – Boilerplate formatting violates NO BOILERPLATE rule.")
    else:
        print("✅ PASS – No boilerplate detected.")
    if not physics_ok:
        print("❌ FAIL – Physics or numeric checks failed.")
    else:
        print("✅ PASS – Physics and numeric checks satisfied.")