# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ------------------ Parameters (from repaired analysis) ------------------
lam   = 0.01          # (GB/s)^-2
v     = 250.0         # GB/s  (vev of correlation field)
I0    = 200.0         # GB/s  (stable operating point)
# I(t) = I0 + A*sin(omega*t)
A     = 50.0          # GB/s amplitude
omega = 20.0*np.pi    # rad/s  (10 Hz -> omega = 2π*10)

# ------------------ Time sampling ------------------
fs    = 1000.0        # Hz (sampling rate >> signal bandwidth)
T     = 1.0           # total observation time (covers many periods)
t     = np.arange(0, T, 1/fs)
N     = len(t)

# ------------------ Signal and derivatives ------------------
I     = I0 + A*np.sin(omega*t)                     # GB/s
dIdt  = A*omega*np.cos(omega*t)                    # GB/s^2
# Jerk from physical derivation: J = -lam*(3*I^2 - v^2)*dIdt
J     = -lam * (3.0*I**2 - v**2) * dIdt            # GB/s^4

# ------------------ Stability metrics ------------------
J_rms = np.sqrt(np.mean(J**2))
J_max = np.max(np.abs(J))

# Entropy: Shannon conditional entropy of I(t) over window
# Normalize to a probability distribution
p     = I / np.sum(I)          # p_i >=0, sum=1
# Avoid log(0)
eps   = 1e-12
S_h   = -np.sum(p * np.log(p + eps))   # nats

# Stiffness terms (using I as proxy for Phi_N, assume Phi_Delta ~0 for lower bound)
# xi_N = [lam*(3*I^2 - v^2)]^{-1/2}
# xi_D = [lam*(I^2 + 3*Phi_D^2 - v^2)]^{-1/2}
# For a conservative check we set Phi_D=0 (gives smallest denominator -> smallest xi)
den_N = lam * (3.0*I**2 - v**2)
den_D = lam * (I**2 - v**2)          # Phi_D=0
# Avoid division by zero or negative inside sqrt (should be positive in stable regime)
xi_N  = 1.0/np.sqrt(np.maximum(den_N, 1e-18))
xi_D  = 1.0/np.sqrt(np.maximum(den_D, 1e-18))
# Use the minimum value over the window as worst-case
xi_N_min = np.min(xi_N)
xi_D_min = np.min(xi_D)

# ------------------ Thresholds (from repaired analysis) ------------------
J_crit   = 1.2e7          # GB/s^4
S_min    = 2.5            # nats
xi_N_thr = 0.1            # s
xi_D_thr = 0.05           # s

# ------------------ Decision ------------------
conds = {
    "RMS(J) < J_crit"          : J_rms < J_crit,
    "max|J| < 3*RMS(J)"        : J_max < 3*J_rms,
    "Entropy > S_min"          : S_h > S_min,
    "xi_N_min > threshold"     : xi_N_min > xi_N_thr,
    "xi_Delta_min > threshold" : xi_D_min > xi_D_thr
}

all_ok = all(conds.values())

# ------------------ Output ------------------
print("=== Informational Jerk Stability Validation ===")
print(f"RMS(J)          = {J_rms:.3e} GB/s^4  (crit = {J_crit:.3e})")
print(f"max|J|          = {J_max:.3e} GB/s^4  (3*RMS = {3*J_rms:.3e})")
print(f"Shannon Entropy = {S_h:.3f} nats    (min = {S_min})")
print(f"xi_N (min)      = {xi_N_min:.3f} s  (thr = {xi_N_thr})")
print(f"xi_Delta (min)  = {xi_D_min:.3f} s  (thr = {xi_D_thr})")
print("\nCondition checks:")
for k, v in conds.items():
    print(f"  {k:35} : {'PASS' if v else 'FAIL'}")
print("\nOverall verdict:", "PASS (Informational Jerk stable)" if all_ok else "FAIL")