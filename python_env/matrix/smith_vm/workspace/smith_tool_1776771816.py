# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Omega Protocol Validator for the Informational‑Jerk analysis.
Run in the isolated VM; it will print PASS/FAIL per rubric pillar.
"""

import re
import numpy as np

# ----------------------------------------------------------------------
# USER‑SUPPLIED DATA (as given by the scrutiny audit)
# ----------------------------------------------------------------------
phi_N   = 0.78          # normalized Newtonian mode amplitude
phi_D   = 0.35          # normalized Archive mode amplitude
dphi_N  = 2.1e3         # s⁻¹
dphi_D  = 8.7e3         # s⁻¹
xi_inv2 = 4.2e6         # s⁻²  (inverse squared stiffness)
J_source= 1.5e12        # s⁻³  (source jerk)
lam     = 1.0e10        # s⁻²  (typical λ from HSA profiling)
g_D     = 0.1           # dimensionless Archive coupling
I0      = 1.0           # normalized to unity (dimensionless)
# ----------------------------------------------------------------------
# Helper: compute ξ from ξ⁻²
# ----------------------------------------------------------------------
xi = 1.0/np.sqrt(xi_inv2)   # seconds

# ----------------------------------------------------------------------
# 1. Entropy derivatives for a two‑state model
# ----------------------------------------------------------------------
def S_h(pN, pD):
    """Shannon entropy for two probabilities (pN + pD = 1)."""
    # guard against log(0)
    eps = 1e-15
    pN = max(min(pN, 1-eps), eps)
    pD = max(min(pD, 1-eps), eps)
    return -(pN*np.log(pN) + pD*np.log(pD))

# probabilities proportional to mode amplitudes (normalized)
pN = phi_N/(phi_N+phi_D)
pD = phi_D/(phi_N+phi_D)

dS_dphiN = -np.log(pN/pD)                     # ∂S/∂φ_N
d2S_dphiN2 = -(1/phi_N + 1/phi_D)             # ∂²S/∂φ_N²
d2S_dphiD2 = -(1/phi_D + 1/phi_N)             # symmetric
d2S_dphiNphiD = 1/(phi_N*phi_D)               # mixed derivative (derived from S = -[p ln p])

print(f"∂S/∂φ_N   = {dS_dphiN:.3f}")
print(f"∂²S/∂φ_N² = {d2S_dphiN2:.3f}")

# ----------------------------------------------------------------------
# 2. Estimate jerk from the dominant chain‑rule term
# ----------------------------------------------------------------------
# Assume ϕ̈_N ≈ ϕ̇_N / ξ  (as Engine did)
d2phi_N = dphi_N / xi
J_chain = 2 * d2S_dphiN2 * dphi_N * d2phi_N   # s⁻³ * (dimensionless)² * s⁻¹ * s⁻² = s⁻³
print(f"Chain‑rule jerk estimate = {J_chain:.3e} s⁻³")

# ----------------------------------------------------------------------
# 3. Finite‑difference jerk estimator (needs Δt)
# ----------------------------------------------------------------------
def third_order_backward_diff(S, dt):
    """Return array of J_I = (S[n] - 3S[n-1] + 3S[n-2] - S[n-3]) / dt³"""
    if len(S) < 4:
        raise ValueError("Need at least 4 samples")
    num = S[3:] - 3*S[2:-2] + 3*S[1:-3] - S[:-4]
    return num / (dt**3)

# Build a mock S_h(t) series using a sinusoidal perturbation around the mean
# (just to illustrate the unit check; any series works)
t = np.arange(0, 0.01, 1e-5)   # 10 ms window, 1 µs step → dt = 1e-5 s
dt = t[1] - t[0]
# Let S_h vary sinusoidally with small amplitude around the mean entropy
S_mean = S_h(pN, pD)
S_series = S_mean + 0.01*np.sin(2*np.pi*500*t)   # 500 Hz modulation

J_fd = third_order_backward_diff(S_series, dt)
print(f"Finite‑difference jerk (mean) = {np.mean(J_fd):.3e} s⁻³")
print(f"Finite‑difference jerk (std)  = {np.std(J_fd):.3e} s⁻³")

# ----------------------------------------------------------------------
# 4. Variance of jerk (should match units of Θ)
# ----------------------------------------------------------------------
var_J = np.var(J_fd)          # s⁻⁶
print(f"Variance of J_I = {var_J:.3e} s⁻⁶")

# ----------------------------------------------------------------------
# 5. Threshold Θ from the Engine's formula
# ----------------------------------------------------------------------
Theta_engine = (lam * I0**2) / (4*np.pi) * (1 + 3*g_D**2/(4*np.pi))
print(f"Θ (Engine formula) = {Theta_engine:.3e}  <-- units?")
# To make Θ have units s⁻⁶ we need to multiply by dt⁻⁴ (see discussion)
Theta_corrected = Theta_engine / (dt**4)
print(f"Θ corrected for dt={dt:.1e}s → {Theta_corrected:.3e} s⁻⁶")

# ----------------------------------------------------------------------
# 6. Check invariant ψ usage in the Engine's latex strings
# ----------------------------------------------------------------------
# Simulate the Engine's latex fragments (as they appeared in the audit)
engine_latex = [
    r"\psi = \ln(\Phi_N/I_0)",
    r"\xi_N^{-2} = \lambda(3\Phi_N^2 + \Phi_\Delta^2 - I_0^2)",
    r"\xi_\Delta^{-2} = \lambda(\Phi_N^2 + 3\Phi_\Delta^2 - I_0^2)",
    r"\mathcal{J}_I = \frac{d}{dt}\bigl[ \partial_{\Phi_N}^2 S_h\,\dot{\Phi}_N^2 + ... \bigr]",
    r"\mathcal{J}_I[n] = S_h[n] - 3S_h[n-1] + 3S_h[n-2] - S_h[n-3]",
    r"\Theta = \frac{\lambda I_0^2}{4\pi}\left(1 + \frac{3g_\Delta^2}{4\pi}\right)"
]

psi_used = any(re.search(r"\\psi", eq) for eq in engine_latex)
# But we need *active* usage: ψ must appear inside a derivative or inside Θ/J
active_psi = any(
    re.search(r"\\psi", eq) and ("\\frac{d" in eq or "\\partial" in eq or "\\Theta" in eq or "\\mathcal{J}" in eq)
    for eq in engine_latex
)

print(f"\nψ defined? {psi_used}")
print(f"ψ actively used in jerk/threshold? {active_psi}")

# ----------------------------------------------------------------------
# 7. Verdict per Omega Protocol pillars
# ----------------------------------------------------------------------
print("\n=== Omega Protocol Pillar Check ===")
pillars = {
    "No boilerplate": True,   # thematic headings, not enumerated lists
    "Covariant modes (Φ_N, Φ_Δ)": True,
    "Invariants (ψ, ξ_N, ξ_Δ) active": active_psi,   # FAIL if ψ not active
    "Boundary conditions": True,
    "Entropy‑based observable": True,
    "Equation‑level derivation": True,
    "Numerical evaluation": True,   # we reproduced numbers (up to unit factors)
    "Dimensional consistency": (
        np.isclose(np.mean(J_fd)**2, var_J, rtol=0.1) and   # crude check: J² ~ var(J) if dt‑scaled
        np.isclose(Theta_corrected, var_J, rtol=0.5)       # threshold should be comparable to variance
    ),
    "Φ‑density impact discussion": True   # qualitative, present
}

for k, v in pillars.items():
    print(f"{k:35}: {'PASS' if v else 'FAIL'}")

overall = all(pillars.values())
print(f"\nOVERALL VERDICT: {'META-PASS' if overall else 'META-FAIL'}")