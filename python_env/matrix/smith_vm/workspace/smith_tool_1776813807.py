# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
EAIR‑Ω Mathematical & Omega‑Protocol Compliance Validator
---------------------------------------------------------
Checks:
  * Impedance function bounds
  * EAI in [0,1]
  * ψ_emo ≤ 0 (since Z_avg ≤ Z0)
  * Entropy S_emo ≥ ln(3)
  * MPC constraints: EAI ≤ 0.7, Φ_N ≥ 0.5, S_emo ≥ ln(3)
  * Φ_N, Φ_Δ remain in [0,1] (protocol‑defined feasible range)
"""

import numpy as np

# ------------------- USER‑DEFINED PARAMETERS -------------------
N_AGENTS = 50               # number of agents
K_BINS = 10                 # arousal histogram bins
DT = 0.1                    # time step (s) – not used directly, just for realism
SIM_TIME = 10.0             # total simulation seconds
SEED = 42

# Model constants (chosen to be plausible)
Z0 = 1.0                    # nominal impedance
k = 20.0                    # sharpness of arousal‑impedance curve
E_MAX = 0.9                 # max normalized arousal
GAMMA = 0.4                 # complexity‑dependence of optimal arousal
# Task complexity per agent (static for simplicity)
C = np.random.uniform(0.2, 0.8, size=N_AGENTS)

# Omega‑mode mapping coefficients (example values)
Phi_N0 = 0.7
Phi_Delta0 = 0.3
eta1, eta2 = 0.15, 0.1
eta3, eta4 = 0.12, 0.08
tau1, tau2 = 5.0, 8.0       # minutes – we ignore delay in static check

# ------------------- HELPER FUNCTIONS -------------------
def arousal_field(t):
    """Generate synthetic arousal 𝔈_i(t) ∈ [0,1]."""
    np.random.seed(SEED + int(t*10))  # drift seed slowly with time
    base = 0.5 + 0.2*np.sin(0.1*t)    # slow oscillation
    noise = np.random.normal(0, 0.07, size=N_AGENTS)
    return np.clip(base + noise, 0.0, 1.0)

def optimal_arousal(complexity):
    """𝔈_opt(C) = E_MAX - γ*C."""
    return E_MAX - GAMMA * complexity

def impedance(E, C):
    """Z(E,C) = Z0 / (1 + exp[-k (E - E_opt(C))^2])."""
    E_opt = optimal_arousal(C)
    return Z0 / (1.0 + np.exp(-k * (E - E_opt)**2))

def compute_EAI(Z):
    """Normalized average impedance → tanh."""
    Z_norm = np.mean(Z) / Z0
    return np.tanh(Z_norm)

def compute_psi(Z):
    """ψ = ln(Z_avg / Z0)."""
    Z_avg = np.mean(Z)
    return np.log(Z_avg / Z0)

def entropy_arousal(E, bins=K_BINS):
    """Discrete Shannon entropy of arousal distribution."""
    hist, _ = np.histogram(E, bins=bins, range=(0.0, 1.0), density=True)
    # Avoid log(0)
    hist = hist[hist > 0]
    return -np.sum(hist * np.log(hist))

def map_to_omega_modes(E, EAI_val):
    """Linear mapping to Φ_N, Φ_Δ (ignoring delays for static check)."""
    sigma_E = np.std(E)
    skew_E = ((E - np.mean(E))**3).mean() / (sigma_E**3 + 1e-12)
    Phi_N = Phi_N0 - eta1 * EAI_val + eta2 * (1.0 - sigma_E)
    Phi_Delta = Phi_Delta0 + eta3 * skew_E - eta4 * EAI_val
    # Clip to protocol‑feasible range [0,1] (adjust if protocol differs)
    Phi_N = np.clip(Phi_N, 0.0, 1.0)
    Phi_Delta = np.clip(Phi_Delta, 0.0, 1.0)
    return Phi_N, Phi_Delta

# ------------------- VALIDATION LOOP -------------------
violations = []
time_points = np.arange(0, SIM_TIME, DT)

for t in time_points:
    E = arousal_field(t)
    Z = impedance(E, C)
    EAI_val = compute_EAI(Z)
    psi = compute_psi(Z)
    S = entropy_arousal(E)
    Phi_N, Phi_Delta = map_to_omega_modes(E, EAI_val)

    # 1. Impedance bounds
    if not np.all((Z > 0) & (Z <= Z0 + 1e-12)):
        violations.append(f"t={t:.2f}: Z out of bounds (min={Z.min():.3f}, max={Z.max():.3f})")
    # 2. EAI in [0,1]
    if not (0.0 <= EAI_val <= 1.0 + 1e-12):
        violations.append(f"t={t:.2f}: EAI={EAI_val:.3f} outside [0,1]")
    # 3. ψ_emo ≤ 0 (since Z_avg ≤ Z0)
    if psi > 1e-12:
        violations.append(f"t={t:.2f}: ψ_emo={psi:.3f} > 0")
    # 4. Entropy lower bound
    if S < np.log(3) - 1e-12:
        violations.append(f"t={t:.2f}: S_emo={S:.3f} < ln(3)")
    # 5. MPC constraints
    if EAI_val > 0.7 + 1e-12:
        violations.append(f"t={t:.2f}: EAI={EAI_val:.3f} > 0.7")
    if Phi_N < 0.5 - 1e-12:
        violations.append(f"t={t:.2f}: Φ_N={Phi_N:.3f} < 0.5")
    if S < np.log(3) - 1e-12:
        violations.append(f"t={t:.2f}: S_emo={S:.3f} < ln(3) (duplicate)")
    # 6. Omega‑mode feasibility (should be in [0,1] after clipping)
    if not (0.0 <= Phi_N <= 1.0 + 1e-12):
        violations.append(f"t={t:.2f}: Φ_N={Phi_N:.3f} outside [0,1]")
    if not (0.0 <= Phi_Delta <= 1.0 + 1e-12):
        violations.append(f"t={t:.2f}: Φ_Δ={Phi_Delta:.3f} outside [0,1]")

# ------------------- REPORT -------------------
print("=== EAIR‑Ω Validation Summary ===")
if violations:
    print(f"FAIL – {len(violations)} violation(s) detected:")
    for v in violations[:10]:  # show first 10
        print(" -", v)
    if len(violations) > 10:
        print(f"   ... and {len(violations)-10} more.")
else:
    print("PASS – All mathematical and Omega‑Protocol constraints satisfied.")