# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Omega Protocol Jerk‑Stability Validator
---------------------------------------
Validates the Informational Jerk Stability (IJS) computation
against the mathematical definitions and Omega Protocol invariants:
    Phi_N   >= 0
    Phi_Delta <= Phi_N
    |j|_max <= J_star   (protocol‑defined jerk bound)

Usage:
    >>> import numpy as np
    >>> I = np.random.rand(100) * 1e9   # synthetic I(t) [bytes/s]
    >>> dt = 0.01                       # 10 ms sampling
    >>> J_star = 5.0e9                  # example jerk bound [bytes/s^4]
    >>> result = validate_ijs(I, dt, J_star)
    >>> print(result)
"""

from __future__ import annotations
import numpy as np
from scipy.signal import savgol_filter

def validate_ijs(
    I: np.ndarray,
    dt: float,
    J_star: float,
    sg_window: int = 5,
    sg_order: int = 2,
) -> dict:
    """
    Compute IJS and check Omega Protocol invariants.

    Parameters
    ----------
    I : np.ndarray
        Raw information‑flow rate samples [bytes/s].
    dt : float
        Sampling interval [s].
    J_star : float
        Protocol‑defined maximum allowed jerk magnitude [bytes/s^4].
    sg_window : int, optional
        Window length for Savitzky–Golay smoothing (must be odd and > sg_order).
    sg_order : int, optional
        Polynomial order for Savitzky–Golay filter.

    Returns
    -------
    dict
        {
            'IJS': float,
            'sigma_j': float,
            'j_max': float,
            'phi_n': float,
            'phi_delta': float,
            'compliant': bool,
            'violations': list[str]
        }
    """
    if I.ndim != 1:
        raise ValueError("I must be a 1‑D array.")
    if len(I) < 3:
        raise ValueError("Need at least 3 samples to compute jerk.")
    if dt <= 0:
        raise ValueError("dt must be positive.")
    if sg_window % 2 == 0 or sg_window < sg_order + 1:
        raise ValueError("Invalid Savitzky–Golay window parameters.")

    # 1. Smooth the raw signal to suppress noise before differentiation
    I_smooth = savgol_filter(I, window_length=sg_window, polyorder=sg_order, deriv=0)

    # 2. Finite‑difference derivatives (forward differences)
    v = np.diff(I_smooth) / dt                     # [bytes/s^2]
    a = np.diff(v) / dt                            # [bytes/s^3]
    j = np.diff(a) / dt                            # [bytes/s^4]

    # 3. Statistics of jerk
    j_mean = np.mean(j)
    sigma_j = np.std(j, ddof=0)                    # population stddev as in the spec
    IJS = 1.0 / (1.0 + sigma_j)

    # 4. Build Omega‑Protocol observables
    phi_n = IJS                                    # non‑negative norm proxy
    phi_delta = 1.0 - IJS                          # simple asymmetry measure (0 when perfectly stable)
    j_max = np.max(np.abs(j))

    # 5. Invariant checks
    violations = []
    if phi_n < 0:
        violations.append("Phi_N < 0")
    if phi_delta > phi_n:
        violations.append("Phi_Delta > Phi_N")
    if j_max > J_star:
        violations.append(f"|j|_max = {j_max:.3e} > J_star = {J_star:.3e}")

    compliant = len(violations) == 0

    return {
        "IJS": float(IJS),
        "sigma_j": float(sigma_j),
        "j_max": float(j_max),
        "phi_n": float(phi_n),
        "phi_delta": float(phi_delta),
        "compliant": compliant,
        "violations": violations,
    }

# ----------------------------------------------------------------------
# Example usage (can be removed or commented out when imported as a module)
if __name__ == "__main__":
    # Synthetic stable workload: low‑variance jerk
    t = np.arange(0, 1.0, 0.01)               # 100 points, 10 ms
    I_stable = 1e9 + 0.1e9 * np.sin(2*np.pi*2*t)  # mild oscillation
    res = validate_ijs(I_stable, dt=0.01, J_star=5e9)
    print("Stable case:", res)

    # Synthetic unstable workload: high‑variance jerk spikes
    I_unstable = I_stable.copy()
    spikes = np.random.rand(len(t)) > 0.95
    I_unstable[spikes] += 5e9 * np.random.randn(np.sum(spikes))
    res2 = validate_ijs(I_unstable, dt=0.01, J_star=5e9)
    print("Unstable case:", res2)