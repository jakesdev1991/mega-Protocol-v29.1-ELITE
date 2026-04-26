# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ------------------------------------------------------------
# PART 1: Jerk-threshold is a mirage
# ------------------------------------------------------------
def compute_jerk_variance(noise_amplitude, dt=1e-4, T=1.0):
    """Simulate a random information field I(t) and compute jerk variance."""
    t = np.arange(0, T, dt)
    I = np.cumsum(noise_amplitude * np.random.randn(len(t)))  # random walk
    # Compute Shannon entropy S_h(t) = -p ln p with p = sigmoid(I)
    p = 1 / (1 + np.exp(-I))
    S = -(p * np.log(p + 1e-12) + (1-p) * np.log(1-p + 1e-12))
    # Finite-difference jerk
    J = (S[3:] - 3*S[2:-1] + 3*S[1:-2] - S[:-3]) / dt**3
    return np.var(J)

# Show that variance scales with noise_amplitude^2 (i.e., arbitrary)
amps = np.logspace(-2, 2, 5)
variances = [compute_jerk_variance(a) for a in amps]
print("Jerk variance vs noise amplitude:")
for a, v in zip(amps, variances):
    print(f"amp={a:.2e}, var={v:.2e}")

# ------------------------------------------------------------
# PART 2: Oscillator order parameter r(t) captures real instability
# ------------------------------------------------------------
def simulate_oscillators(N=100, coupling=0.5, jitter_sigma=1e-5, T=0.01, dt=1e-6):
    """
    N phase oscillators with contention coupling K_ij(t-tau) = exp(-|t-tau|/tau0) * sign(t-tau).
    Jitter is added to the GPU scheduler.
    """
    tau0 = 5e-6
    theta = np.random.uniform(0, 2*np.pi, N)
    omega = np.random.normal(1e3, 50, N)  # intrinsic frequencies (rad/s)
    r_history = []
    t = np.arange(0, T, dt)
    for idx, ti in enumerate(t):
        # Jitter: random shift in scheduler time
        jitter = np.random.normal(0, jitter_sigma, N)
        # Compute coupling influence from past (simplified exponential kernel)
        influence = coupling * np.exp(-(ti - t[:idx]) / tau0) if idx > 0 else 0
        # Update phases (Euler)
        dtheta = (omega + jitter) * dt
        if idx > 0:
            # Contention: each oscillator feels a pull toward the mean phase weighted by influence
            mean_phase = np.angle(np.sum(np.exp(1j * theta)))
            dtheta += coupling * influence * np.sin(mean_phase - theta) * dt
        theta += dtheta
        # Order parameter r = |<exp(i theta)>|
        r = np.abs(np.mean(np.exp(1j * theta)))
        r_history.append(r)
    return t, np.array(r_history)

# Run two scenarios: stable (low coupling) vs collapse (high coupling)
t_low, r_low = simulate_oscillators(coupling=0.2, jitter_sigma=1e-5)
t_high, r_high = simulate_oscillators(coupling=0.8, jitter_sigma=1e-5)

plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
plt.plot(t_low, r_low, label='low coupling (stable)')
plt.plot(t_high, r_high, label='high coupling (collapse)')
plt.xlabel('time (s)')
plt.ylabel('order parameter r')
plt.legend()
plt.title('Oscillator model: r(t) predicts sync vs shredding')

plt.subplot(1, 2, 2)
plt.loglog(amps, variances, '-o')
plt.xlabel('noise amplitude')
plt.ylabel('jerk variance')
plt.title('Jerk variance is tunable → threshold is meaningless')
plt.tight_layout()
plt.show()