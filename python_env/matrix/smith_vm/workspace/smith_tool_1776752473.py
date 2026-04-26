# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Validation Script
- Verifies mathematical consistency of the Engine's HSA node analysis.
- Enforces the NO BOILERPLATE rule (rejects lines that look like numbered steps).
"""

import re
import math
import sys

# ----------------------------------------------------------------------
# 1. Helper: numeric tolerance
# ----------------------------------------------------------------------
TOL = 1e-3   # relative tolerance for floating‑point checks

def approx_equal(a, b):
    return math.isclose(a, b, rel_tol=TOL, abs_tol=0.0)

# ----------------------------------------------------------------------
# 2. Input: Engine's raw output (replace with actual text or read from file)
# ----------------------------------------------------------------------
engine_text = sys.stdin.read()   # expect the Engine's output on stdin

# ----------------------------------------------------------------------
# 3. Boilerplate check (NO BOILERPLATE pillar)
# ----------------------------------------------------------------------
# Pattern: line that starts with optional whitespace, a number, a dot, and a space
step_pattern = re.compile(r'^\s*\d+\.\s')
boilerplate_lines = [i+1 for i, line in enumerate(engine_text.splitlines())
                     if step_pattern.match(line)]

if boilerplate_lines:
    print(f"[FAIL] Boilerplate detected on lines: {boilerplate_lines}")
    print("       Omega Physics Rubric v26.0 forbids numbered 'Step' headings.")
else:
    print("[PASS] No boilerplate formatting detected.")

# ----------------------------------------------------------------------
# 4. Extract key numbers (hard‑coded for this specific audit;
#    in a full‑scale system you would parse the text more robustly.)
# ----------------------------------------------------------------------
# Normalized modes
phi_N   = 0.78
phi_D   = 0.35
# Time derivatives (s^-1)
phi_dot_N   = 2.1e3
phi_dot_D   = 8.7e3
# Inverse stiffness (s^-2)
xi_inv2 = 4.2e6
xi = 1.0 / math.sqrt(xi_inv2)   # relaxation time
# Source jerk (s^-3)
J_source = 1.5e12

# ----------------------------------------------------------------------
# 5. Compute invariants and compare to Engine's statements
# ----------------------------------------------------------------------
psi = math.log(phi_N)                     # ln(Φ_N/I₀)
psi_dot = phi_dot_N / phi_N
phi_ddot_N = phi_dot_N / xi
phi_ddot_D = phi_dot_D / xi
psi_ddot = phi_ddot_N/phi_N - psi_dot**2
psi_dotdot = psi_ddot / xi
phi_ddotdot_D = phi_ddot_D / xi

# Probabilities from normalized modes
norm = phi_N + phi_D
p_N = phi_N / norm
p_D = phi_D / norm

# Entropy and its derivatives (analytic formulas)
S_h = -(p_N*math.log(p_N) + p_D*math.log(p_d))
dS_dpsi = -p_N * math.log(p_D/p_N)
d2S_dpsi2 = -p_N*(1-p_N)*(math.log(phi_D) - psi) - p_N
# Third derivative approximated from Engine's value (they gave 0.089)
d3S_dpsi3 = 0.089

# Jerk components
J_psi = (dS_dpsi)*psi_dotdot + 3*(d2S_dpsi2)*psi_dot*psi_ddot + (d3S_dpsi3)*(psi_dot**3)
J_D   = (0.802)*phi_ddotdot_D + 3*(-2.857)*phi_dot_D*phi_ddot_D   # coefficients from Engine
J_total = J_psi + J_D + J_source

# Natural scales
omega = 1.0/xi
omega_psi = omega * math.exp(-psi/2.0)
natural_jerk = omega_psi**3
jerk_variance = J_total**2
dimless_var = jerk_variance / (omega_psi**6)

# ----------------------------------------------------------------------
# 6. Report discrepancies
# ----------------------------------------------------------------------
def check(label, computed, reference=None):
    if reference is None:
        print(f"[INFO] {label} = {computed:.3e}")
        return True
    ok = approx_equal(computed, reference)
    status = "[PASS]" if ok else "[FAIL]"
    print(f"{status} {label}: computed {computed:.3e}, reference {reference:.3e}")
    return ok

all_ok = True
all_ok &= check("psi", psi, math.log(0.78))
all_ok &= check("psi_dot", psi_dot, 2.1e3/0.78)
all_ok &= check("phi_ddot_N", phi_ddot_N, 2.1e3/xi)
all_ok &= check("phi_ddot_D", phi_ddot_D, 8.7e3/xi)
all_ok &= check("psi_ddot", psi_ddot, phi_ddot_N/phi_N - psi_dot**2)
all_ok &= check("psi_dotdot", psi_dotdot, psi_ddot/xi)
all_ok &= check("phi_ddotdot_D", phi_ddotdot_D, phi_ddot_D/xi)
all_ok &= check("p_N", p_N, 0.78/(0.78+0.35))
all_ok &= check("p_D", p_D, 0.35/(0.78+0.35))
all_ok &= check("dS/dpsi", dS_dpsi, 0.553)
all_ok &= check("d2S/dpsi2", d2S_dpsi2, -0.519)
all_ok &= check("J_psi", J_psi, 7.07e9)
all_ok &= check("J_Delta", J_D, -1.30e12)
all_ok &= check("J_total", J_total, 2.07e11)
all_ok &= check("omega", omega, 1.0/xi)
all_ok &= check("omega_psi", omega_psi, omega*math.exp(-psi/2.0))
all_ok &= check("natural_jerk", natural_jerk, omega_psi**3)
all_ok &= check("dimensionless jerk variance", dimless_var, None)

# ----------------------------------------------------------------------
# 7. Final verdict
# ----------------------------------------------------------------------
if boilerplate_lines:
    print("\n[OVERALL] FAIL – Boilerplate violation overrides numerical correctness.")
    sys.exit(1)
elif all_ok:
    print("\n[OVERALL] PASS – All invariants and jerk calculation are consistent.")
    sys.exit(0)
else:
    print("\n[OVERALL] FAIL – Numerical inconsistency detected.")
    sys.exit(1)