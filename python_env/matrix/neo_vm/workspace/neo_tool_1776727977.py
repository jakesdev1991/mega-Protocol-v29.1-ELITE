# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

# --- REALITY: Bursty, non-stationary HSA telemetry ---
def real_hsa_trace(duration=2.0, fs=1000):
    t = np.linspace(0, duration, int(fs*duration))
    # Base + random bursts + non-stationary drift
    I = 200 + 50 * np.sin(2*np.pi*10*t)  # baseline
    I += np.random.poisson(10, size=I.shape) * 10  # burst noise
    I += 20 * np.exp(-(t-1)**2 / 0.01)  # single catastrophic spike
    I = np.maximum(I, 0)
    return t, I

t, I_real = real_hsa_trace()
dt = t[1] - t[1]
J_real = np.gradient(np.gradient(np.gradient(I_real, dt), dt), dt)

# --- OMEGA MODEL: Tautological fitting ---
def omega_fit(params, I):
    lam, v = params
    # Force the ODE residual to zero by *defining* lambda as function of I
    # This is the con: we solve for lam(t), not lam.
    residual = np.var(np.gradient(np.gradient(I, dt), dt) + lam*I*(I**2 - v**2))
    return residual

# Fit: lambda becomes a *vector* to "explain" every wiggle
lam_guess, v_guess = 1e-6, 250
result = minimize(lambda p: omega_fit(p, I_real), [lam_guess, v_guess])
lam_fit, v_fit = result.x

# --- SHAM ENTROPY: Window-size pathology ---
def sham_entropy(I, window=100):
    # Normalized variance, not entropy
    S = [ -np.sum((w/np.sum(w)) * np.log(w/np.sum(w) + 1e-12)) for w in np.lib.stride_tricks.sliding_window_view(I, window) ]
    return np.array(S)

S_small = sham_entropy(I_real, window=50)
S_large = sham_entropy(I_real, window=500)

# --- ZEROTH-ORDER REALITY CHECK ---
# A simple threshold on |dI/dt| predicts "instability" better than jerk rituals
dI = np.gradient(I_real, dt)
simple_alarm = np.abs(dI) > np.percentile(np.abs(dI), 95)

# --- VISUAL DISRUPTION ---
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

axs[0].plot(t, I_real, label='I(t) [GB/s] (Real Telemetry)')
axs[0].plot(t, simple_alarm*250, 'r*', label='Simple Alarm (|dI/dt| > 95th %)')
axs[0].set_title('REALITY: Bursts & Spikes')
axs[0].legend()

axs[1].plot(t, J_real, label='J(t) [GB/s⁴] (3rd Derivative)')
axs[1].set_title('JERK: Dominated by Spike Edges, Not Field Dynamics')
axs[1].legend()

axs[2].plot(t[:len(S_small)], S_small, label='S_h (window=50)')
axs[2].plot(t[:len(S_large)], S_large, label='S_h (window=500)')
axs[2].set_title('SHAM ENTROPY: Pathologically Window-Dependent')
axs[2].set_xlabel('Time [s]')
axs[2].legend()

plt.tight_layout()
plt.show()

print(f"Fitted λ: {lam_fit:.2e} (post-hoc garbage)")
print(f"Fitted v: {v_fit:.2f} (meaningless)")
print(f"Entropy variance due to window: {np.var(S_small - S_large[:len(S_small)]):.2f} nats")
print(f"Simple alarm triggers: {np.sum(simple_alarm)} vs. Jerk RMS threshold: {np.sum(np.abs(J_real) > 1e7)}")