# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# Simulate a non‑stationary pipeline with drifting frequency and chaotic coupling
np.random.seed(0)
T = 1000
t = np.arange(T)

# Frequency drift: f(t) = f0 + δf·sin(ω_d t) + small random walk
f0 = 0.05
δf = 0.02
ω_d = 0.01
f_t = f0 + δf * np.sin(ω_d * t) + 0.001 * np.cumsum(np.random.normal(0, 1, T))

# Chaotic coupling via logistic map injected into latency jitter
def logistic_map(x, r=3.8):
    return r * x * (1 - x)

# Initialize latent chaotic variable
chaos = np.zeros(T)
chaos[0] = 0.5
for i in range(1, T):
    chaos[i] = logistic_map(chaos[i-1])

# Synthetic sensor signals: latency (vibration), throughput (speed), CPU load (temperature)
latency = 10 + 5 * np.sin(2*np.pi * np.cumsum(f_t)) + 3*chaos + np.random.normal(0, 1, T)
throughput = 1000 + 200 * np.sin(2*np.pi * np.cumsum(f_t) + np.pi/4) + 50*chaos + np.random.normal(0, 50, T)
cpu_load = 50 + 10 * np.sin(2*np.pi * np.cumsum(f_t) + np.pi/2) + 5*chaos + np.random.normal(0, 5, T)
error_rate = 0.01 + 0.005 * np.sin(2*np.pi * np.cumsum(f_t) + np.pi) + 0.002*chaos + np.random.normal(0, 0.002, T)
power_draw = 500 + 100 * np.sin(2*np.pi * np.cumsum(f_t) + 3*np.pi/2) + 20*chaos + np.random.normal(0, 20, T)

# Inject a catastrophic event at t=700: massive latency spike and error burst
failure_time = 700
latency[failure_time:] += np.random.normal(0, 20, T - failure_time)
error_rate[failure_time:] += 0.05

# --- Traditional order analysis (fixed reference) ---
f_ref = f0
phase_ref = 2*np.pi * f_ref * t
# Approximate order‑domain amplitudes via FFT at reference frequency
def amp_at_ref(metric):
    fft = np.fft.fft(metric)
    freqs = np.fft.fftfreq(len(metric), d=1.0)
    idx = np.argmin(np.abs(freqs - f_ref))
    return np.abs(fft[idx])

A_lat = amp_at_ref(latency)
A_thr = amp_at_ref(throughput)
A_cpu = amp_at_ref(cpu_load)
A_err = amp_at_ref(error_rate)
A_pwr = amp_at_ref(power_draw)

# Compute PHI (distance from uniform distribution of harmonic power)
A = np.array([A_lat, A_thr, A_cpu, A_err, A_pwr])
p = A**2 / np.sum(A**2)
PHI = 1 - np.sum(np.abs(p - np.ones_like(p)/len(p)))  # crude metric

# --- Criticality‑based index: avalanche size distribution of latency bursts ---
threshold = 15
bursts = (latency > threshold).astype(int)
# Find contiguous avalanche sizes
avalanche_sizes = []
cnt = 0
for b in bursts:
    if b:
        cnt += 1
    else:
        if cnt > 0:
            avalanche_sizes.append(cnt)
            cnt = 0
if cnt > 0:
    avalanche_sizes.append(cnt)
# Criticality index: log‑probability of large avalanches
s_c = 5
P_large = np.mean([s for s in avalanche_sizes if s > s_c]) if avalanche_sizes else 0
C = np.log(P_large + 1e-6)

print("PHI (Pipeline Health Index):", PHI)
print("Criticality Index C:", C)

# --- Dimensional inconsistency demonstration ---
lambda_coupling = 1.0  # [time]⁻²
I0 = 0.5
I = PHI  # dimensionless
V = (lambda_coupling / 4) * (I**2 - I0**2)**2
# Action integrand (1/2)(dI/dt)² + V(I) has dimensions [time]⁻², but must be [time]⁻¹
print("Potential V dimensions: [time]⁻² (inconsistent with required [time]⁻¹)")

# --- Non‑uniqueness of mapping from PHI to Omega invariants ---
# Two different coherence values that yield same PHI
coh1, coh2 = 0.8, 1.2
lambda_N1 = lambda_coupling * (3/coh1 + 1/coh1**2)
lambda_N2 = lambda_coupling * (3/coh2 + 1/coh2**2)
print("Eigenvalue λ_N for coh=0.8:", lambda_N1)
print("Eigenvalue λ_N for coh=1.2:", lambda_N2)
print("Same PHI but different eigenvalues → mapping to ξ_N, ξ_Δ is not unique")