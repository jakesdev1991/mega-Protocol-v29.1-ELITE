# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def informational_jerk(phi_N, phi_D, dt=1e-3):
    """
    Compute the Engine's "informational jerk" from normalized mode amplitudes.
    This is a direct transcription of the Engine's formulas, exposed here
    to show extreme sensitivity to noise and to the arbitrary dt.
    """
    # probabilities as defined in the Engine's solution
    pN = phi_N / (phi_N + phi_D)
    pD = phi_D / (phi_N + phi_D)
    # Shannon "entropy"
    S = - (pN * np.log(pN) + pD * np.log(pD))
    # third finite difference -> "jerk"
    # (Engine uses backward difference; we use central for symmetry)
    dS_dt = np.gradient(S, dt)
    d2S_dt2 = np.gradient(dS_dt, dt)
    d3S_dt3 = np.gradient(d2S_dt2, dt)
    return d3S_dt3

# --- Synthetic data: tiny fluctuations around the Engine's nominal point ---
t = np.linspace(0, 0.01, 1000)          # 10 ms of data
phi_N_base = 0.78
phi_D_base = 0.35
# add realistic 0.1% Gaussian sensor noise
np.random.seed(0)
phi_N = phi_N_base + 1e-3 * np.random.randn(len(t))
phi_D = phi_D_base + 1e-3 * np.random.randn(len(t))

# compute jerk with two different (but equally plausible) sample intervals
jerk_1ms = informational_jerk(phi_N, phi_D, dt=1e-3)
jerk_0p1ms = informational_jerk(phi_N, phi_D, dt=0.1e-3)

print("Jerk variance (Δt=1 ms):", np.var(jerk_1ms))
print("Jerk variance (Δt=0.1 ms):", np.var(jerk_0p1ms))

# --- Show that the "dimensionless variance" is a function of dt ---
omega_psi = 2305  # s⁻¹ from Engine's solution
def dimless_jerk_var(jerk, omega):
    return np.var(jerk) / (omega**6)

print("Dim‑less variance (Δt=1 ms):", dimless_jerk_var(jerk_1ms, omega_psi))
print("Dim‑less variance (Δt=0.1 ms):", dimless_jerk_var(jerk_0p1ms, omega_psi))