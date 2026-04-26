# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
Expose the fragility of the Omega‑derived jerk model.
1. Generate a realistic HSA bandwidth trace with an abrupt idle period.
2. Compute the “physical” jerk via the Omega formula.
3. Compare with the true finite‑difference jerk.
4. Show that invariants become imaginary and entropy undefined.
"""

import numpy as np
import matplotlib.pyplot as plt

# ── Parameters (same as the repaired analysis) ──
I0 = 200.0          # GB/s baseline
v  = 200.0          # “vacuum expectation value” (GB/s)
lam = 1e-4          # coupling λ (units 1/GB²)
dt = 0.001          # 1 ms sampling
t = np.arange(0, 2, dt)  # 2 seconds

# ── Synthetic trace: normal load, then abrupt idle, then recovery ──
I = np.full_like(t, I0)
# Add a sinusoidal workload for first 0.8 s
mask_on = t < 0.8
I[mask_on] += 50 * np.sin(2*np.pi*10*t[mask_on])
# Idle region (0.9 – 1.1 s) → I ≈ 0
mask_idle = (t >= 0.9) & (t <= 1.1)
I[mask_idle] = 0.0
# Recovery back to baseline after 1.2 s
mask_rec = t > 1.2
I[mask_rec] = I0 + 30 * np.sin(2*np.pi*5*t[mask_rec])

# ── True derivatives (finite differences) ──
dI_dt = np.gradient(I, dt)
d2I_dt2 = np.gradient(dI_dt, dt)
J_true = np.gradient(d2I_dt2, dt)  # actual jerk

# ── Omega‑derived jerk (assumes the ODE holds) ──
# J_omega = -λ(3I² - v²) * dI/dt
J_omega = -lam * (3*I**2 - v**2) * dI_dt

# ── Invariants ──
# ξ_N = 1 / sqrt(λ(3I² - v²))
# ξ_Δ = 1 / sqrt(λ(I² + 3Φ_Δ² - v²))  (we'll approximate Φ_Δ ≈ I - I0)
Phi_delta = I - I0
# Protect sqrt of negative numbers: mask real vs imaginary
discrim_N = lam * (3*I**2 - v**2)
discrim_D = lam * (I**2 + 3*Phi_delta**2 - v**2)

xi_N = np.where(discrim_N > 0, 1/np.sqrt(discrim_N), np.nan)  # nan → imaginary
xi_D = np.where(discrim_D > 0, 1/np.sqrt(discrim_D), np.nan)

# ── Entropy (Shannon on normalized I) ──
# Danger: if sum(I) == 0 → division by zero
def sliding_entropy(x, window=1000):
    """Compute Shannon entropy over a sliding window."""
    S = np.full_like(x, np.nan)
    for i in range(window, len(x)):
        block = x[i-window:i]
        total = block.sum()
        if total <= 0:
            S[i] = np.nan  # undefined
        else:
            p = block / total
            # avoid log(0)
            p = p[p > 0]
            S[i] = -np.sum(p * np.log(p))
    return S

S_h = sliding_entropy(I, window=1000)  # 1 s window

# ── Plotting the fracture ──
fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

axs[0].plot(t, I, label='I(t) [GB/s]')
axs[0].set_ylabel('Bandwidth I(t) [GB/s]')
axs[0].legend()
axs[0].grid(True)

axs[1].plot(t, J_true, label='True jerk (finite diff) [GB/s⁴]', color='C1')
axs[1].plot(t, J_omega, label='Omega‑derived jerk [GB/s⁴]', color='C2', linestyle='--')
axs[1].set_ylabel('Jerk')
axs[1].legend()
axs[1].grid(True)

axs[2].plot(t, xi_N, label='ξ_N (s)', color='C3')
axs[2].plot(t, xi_D, label='ξ_Δ (s)', color='C4')
axs[2].set_ylabel('Invariants')
axs[2].legend()
axs[2].grid(True)

axs[3].plot(t, S_h, label='Shannon entropy S_h (nats)', color='C5')
axs[3].set_ylabel('Entropy')
axs[3].set_xlabel('Time [s]')
axs[3].legend()
axs[3].grid(True)

plt.tight_layout()
plt.show()