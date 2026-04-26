# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Invariant & Numeric Validator
--------------------------------------------
- Checks that the invariant ψ = ln(Φ_N/I₀) appears actively in the derivation.
- Verifies the Engine's numeric jerk, variance, and threshold against re‑computed values.
"""

import re
import math
from typing import Tuple

# ----------------------------------------------------------------------
# 1. NUMERICAL VALIDATION
# ----------------------------------------------------------------------
def validate_numbers() -> Tuple[bool, str]:
    # Supplied audit data (normalized, v = I0 = 1)
    phi_N   = 0.78
    phi_D   = 0.35
    dphi_N  = 2.1e3      # s^-1
    dphi_D  = 8.7e3      # s^-1
    xi_inv2 = 4.2e6      # s^-2
    J_source= 1.5e12     # s^-3

    # Derived quantities
    xi = 1.0 / math.sqrt(xi_inv2)               # s
    d2phi_N = dphi_N / xi                       # s^-2 (approx)

    # Entropy derivatives for two‑state model
    dS_dphiN   = -math.log(phi_N/phi_D)
    d2S_dphiN2 = -1.0/phi_N - 1.0/phi_D

    # Dominant chain‑rule term for jerk
    J_dom = 2.0 * d2S_dphiN2 * dphi_N * d2phi_N   # s^-3
    J_total = J_dom + J_source                     # s^-3

    # Variance assuming ±20% fluctuation
    sigma_J = 0.20 * abs(J_total)
    var_J   = sigma_J**2                           # s^-6

    # Threshold Θ (λ=1e10, gΔ=0.1)
    lam   = 1.0e10                                 # s^-2
    gD    = 0.1
    I0    = 1.0
   Theta  = lam * I0**2 / (4.0*math.pi) * (1.0 + 3.0*gD**2/(4.0*math.pi))

    # Engine's reported values (from the text)
    J_engine   = 1.43e12
    var_engine = 8.18e22
    Theta_engine = 8.0e8

    tol = 1e-2   # 1% tolerance
    ok = (abs(J_engine   - J_total)   / abs(J_total)   < tol and
          abs(var_engine - var_J)     / abs(var_J)     < tol and
          abs(Theta_engine - Theta)   / abs(Theta)     < tol)

    msg = (f"Numeric check: {'PASS' if ok else 'FAIL'}\n"
           f"  J_total   = {J_total:.3e} (engine {J_engine:.3e})\n"
           f"  var_J     = {var_J:.3e} (engine {var_engine:.3e})\n"
           f"  Theta     = {Theta:.3e} (engine {Theta_engine:.3e})")
    return ok, msg

# ----------------------------------------------------------------------
# 2. INVARIANT USAGE CHECK
# ----------------------------------------------------------------------
def invariant_used(derivation_text: str) -> Tuple[bool, str]:
    """
    Returns True if ψ (or ln(Φ_N/I₀)) appears in a *dynamic* context:
    - inside a derivative (d/dt, ∂/∂, dot)
    - multiplied/divided by another variable
    - inside the threshold expression Θ
    - or inside the jerk formula 𝒥_I.
    Mere definition like "ψ = ln(Φ_N/I₀)" does NOT count.
    """
    # Normalise whitespace
    txt = derivation_text.replace('\n', ' ')

    # Patterns that indicate active use:
    #   dψ/dt, ∂ψ/∂, ψ̇, ψ * something, something / ψ, ψ inside Θ or 𝒥_I
    active_patterns = [
        r'dψ\s*/\s*dt',          # dψ/dt
        r'∂ψ\s*/\s*∂t',          # ∂ψ/∂t
        r'ψ̇',                    # ψ̇
        r'ψ\s*[\*/]\s*[A-Za-z_]',# ψ * or / something
        r'[A-Za-z_]\s*[\*/]\s*ψ',# something * or / ψ
        r'Θ\s*=\s*.*ψ',          # Θ = ... ψ ...
        r'𝒥_I\s*=\s*.*ψ',        # 𝒥_I = ... ψ ...
        r'ln\s*\(\s*Φ_N\s*/\s*I₀\s*\)', # the explicit form inside another expr
    ]

    for pat in active_patterns:
        if re.search(pat, txt, flags=re.IGNORECASE):
            return True, f"Invariant ψ found active via pattern: {pat}"

    # If we only see a bare definition, reject
    if re.search(r'ψ\s*=\s*ln\s*\(\s*Φ_N\s*/\s*I₀\s*\)', txt, flags=re.IGNORECASE):
        return False, "Invariant ψ appears only as a definition, not used dynamically."
    return False, "No active use of invariant ψ detected."

# ----------------------------------------------------------------------
# 3. MAIN DRIVER (example usage)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # ---- Numeric validation ----
    num_ok, num_msg = validate_numbers()
    print(num_msg)
    print("-"*60)

    # ---- Invariant usage check ----
    # Paste the Engine's derivation text here (trimmed for brevity)
    engine_derivation = """
    The analysis begins with the Omega Action for information flow...
    V(I) = λ/4 (I² - I₀²)².
    This yields covariant modes Φ_N and Φ_Δ...
    ψ = ln(Φ_N/I₀)   [defined but not used further]
    The Shannon conditional entropy S_h(t) = -∑ p_i ln p_i...
    𝒥_I = d/dt[ ∂²S_h/∂Φ_N² Φ̇_N² + … ].
    For practical computation: 𝒥_I[n] = S_h[n] - 3S_h[n-1] + 3S_h[n-2] - S_h[n-3].
    Source jerk: 𝒥_source = 1.5×10¹² s⁻³.
    Using supplied data: φ_N=0.78, φ_Δ=0.35, φ̇_N=2.1×10³ s⁻¹, φ̇_Δ=8.7×10³ s⁻¹,
    ξ⁻²=4.2×10⁶ s⁻² → ξ≈4.9×10⁻⁴ s, φ̈_N≈φ̇_N/ξ≈4.3×10⁶ s⁻².
    ∂S_h/∂φ_N≈-0.80, ∂²S_h/∂φ_N²≈-4.1.
    𝒥_I ≈ 2·(-4.1)·(2.1×10³)·(4.3×10⁶) ≈ -7.4×10¹⁰ s⁻³.
    Adding source: 𝒥_I≈1.43×10¹² s⁻³.
    σ_𝒥² ≈ (0.2·𝒥_I)² ≈ 8.18×10²² s⁻⁶.
    Θ ≈ λ I₀²/(4π) (1+3g_Δ²/(4π)) ≈ 8.0×10⁸ s⁻⁶.
    Since σ_𝒥² ≫ Θ → unstable.
    """
    inv_ok, inv_msg = invariant_used(engine_derivation)
    print("Invariant usage check:", "PASS" if inv_ok else "FAIL")
    print(inv_msg)

    # Final verdict
    if num_ok and inv_ok:
        print("\n>>> OMEGA PROTOCOL VALIDATION: PASS")
    else:
        print("\n>>> OMEGA PROTOCOL VALIDATION: FAIL")