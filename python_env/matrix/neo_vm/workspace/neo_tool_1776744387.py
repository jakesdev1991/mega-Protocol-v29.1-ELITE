# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def fractal_phase(t, price_series, window=100):
    """Compute pipeline cycle phase modulated by market volatility"""
    returns = np.log(price_series[1:] / price_series[:-1])
    vol = np.std(returns[-window:])
    hurst = compute_hurst_exponent(returns)  # Detrended fluctuation
    # Fractal time dilation: dτ = dt * (1 + H(t) * vol)
    d_tau = 1 + hurst * vol * np.sin(2*np.pi*t/len(price_series))
    tau = np.cumsum(d_tau)
    theta = 2*np.pi * tau / np.max(tau)
    return theta

# Your "order analysis" now operates on event-time, not clock-time