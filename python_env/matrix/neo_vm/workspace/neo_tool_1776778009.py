# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def cod_overlap(subconscious, operator):
    """Compute the overlap integral ψ* O ψ (dimensionless)."""
    return np.vdot(subconscious, operator @ subconscious).real

def simulate(paradox=False, steps=200, N=8):
    """
    Simulate COD time series.
    If paradox=True, inject a self‑negating operator at the midpoint.
    """
    # Random (unobservable) "subconscious" vector
    psi = np.random.randn(N) + 1j*np.random.randn(N)
    psi /= np.linalg.norm(psi)

    # Random Hermitian "projection" operator (your P_val)
    P = np.random.randn(N, N) + 1j*np.random.randn(N, N)
    P = (P + P.conj().T) / 2

    # Stabilization fudge factor (urgency × safety)
    urgency, safety = 0.2, 0.8
    O_stab = urgency * safety

    cod_series = []
    for t in range(steps):
        # Random perturbation (cognitive "noise")
        noise = (np.random.randn(N) + 1j*np.random.randn(N)) * 0.1
        psi += noise
        psi /= np.linalg.norm(psi)

        # Apply paradox injection at t = steps//2
        if paradox and t == steps // 2:
            # Define P_bot = I - P
            P_bot = np.eye(N) - P
            # Compute both overlaps; the system must reconcile C and 1-C
            C_val = cod_overlap(psi, O_stab * P)
            C_bot = cod_overlap(psi, O_stab * P_bot)
            # Force the metric to be the difference (Gödelian inconsistency)
            cod_series.append(C_val - C_bot)
        else:
            cod_series.append(cod_overlap(psi, O_stab * P))

    return np.array(cod_series)

# Run two scenarios
np.random.seed(42)
normal_run = simulate(paradox=False)
paradox_run = simulate(paradox=True)

# Show that the "normal" COD is unstable and that the paradox run diverges
print("Normal run – mean COD: {:.3f}, std: {:.3f}".format(normal_run.mean(), normal_run.std()))
print("Paradox run – mean COD: {:.3f}, std: {:.3f}".format(paradox_run.mean(), paradox_run.std()))
print("Shredding events (|COD| < 0.1) in normal run:", (np.abs(normal_run) < 0.1).sum())
print("Shredding events in paradox run:", (np.abs(paradox_run) < 0.1).sum())