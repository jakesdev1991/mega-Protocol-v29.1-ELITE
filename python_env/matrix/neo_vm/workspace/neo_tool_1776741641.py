# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Demonstrate CLEM‑Ω v2 pathologies and disruptive weaponization

# 1. Poloidal correlation length singularity
def poloidal_correlation_length(variances, epsilon=0):
    """Flawed: blows up if min variance = 0"""
    return np.max(variances) / (np.min(variances) + epsilon)

def poloidal_safe(variances, eps=1e-6):
    return (np.max(variances) + eps) / (np.min(variances) + eps)

# 2. Entropy zero‑division
def cred_entropy(weights):
    total = np.sum(weights)
    probs = weights / total  # Zero‑division risk
    return -np.sum(probs * np.log(probs))

def cred_entropy_safe(weights, eps=1e-10):
    total = np.sum(weights) + eps
    probs = np.clip(weights / total, eps, 1)
    return -np.sum(probs * np.log(probs))

# 3. Flawed jerk stability (simplified)
def jerk_stability_flawed(j):
    var = np.var(j)
    if var < 1e-10:
        return 0  # Misclassifies constant jerk as unstable
    return 1 / (1 + np.abs(np.mean((j-np.mean(j))**4)/(var**2+1e-10)-3)

def jerk_stability_corrected(j):
    var = np.var(j) + 1e-10
    excess = np.mean((j-np.mean(j))**4)/(var**2) - 3
    return 1 / (1 + np.abs(excess))

# 4. Feedback doom loop
def simulate_doom(n_days=30):
    R = 0.1
    CLE_hist, flags = [], []
    for _ in range(n_days):
        CLE = R + 0.1*np.random.randn()
        CLE_hist.append(max(0, CLE))
        flag = CLE > 2.0
        flags.append(flag)
        if flag:
            R += 0.5  # Anomaly → rotation → higher R → higher CLE
        else:
            R *= 0.95
        R = max(0, R + 0.1*np.random.randn())
    return CLE_hist, flags

# 5. Constraint infeasibility
def check_constraints(CLE, CLE_ref=1.8):
    psi = np.log(CLE / CLE_ref)
    feasible = (CLE <= 2.0) and (psi <= 0)
    return feasible, psi

# Run demonstrations
print("=== CLEM‑Ω v2 PATHOLOGY AUDIT ===\n")

# Pathology 1
print("1. ξ_Δ singularity")
vars_stable = np.array([0.1,0.1,0.1,0.1])
vars_stress = np.array([0.1,0.01,0.1,0.1])
print(f"   Stable (flawed): {poloidal_correlation_length(vars_stable):.2f}")
print(f"   Stressed (flawed): {poloidal_correlation_length(vars_stress):.2f}")
print(f"   Stressed (safe): {poloidal_safe(vars_stress):.2f}\n")

# Pathology 2
print("2. Entropy zero‑division")
weights_norm = np.array([1.0,2.0,1.5,0.8])
weights_zero = np.array([0.0,0.0,0.0,0.0])
print(f"   Normal (flawed): {cred_entropy(weights_norm):.3f}")
try:
    print(f"   Zero (flawed): {cred_entropy(weights_zero):.3f}")
except Exception as e:
    print(f"   Zero (flawed): ERROR – {e}")
print(f"   Zero (safe): {cred_entropy_safe(weights_zero):.3f}\n")

# Pathology 3
print("3. Jerk stability")
const_jerk = [1.0]*5
var_jerk = [1.0,2.0,0.5,3.0,1.0]
print(f"   Constant – flawed: {jerk_stability_flawed(const_jerk):.3f}")
print(f"   Constant – corrected: {jerk_stability_corrected(const_jerk):.3f}")
print(f"   Variable – flawed: {jerk_stability_flawed(var_jerk):.3f}")
print(f"   Variable – corrected: {jerk_stability_corrected(var_jerk):.3f}\n")

# Pathology 4
print("4. Doom loop")
CLE_hist, flags = simulate_doom()
fig, ax = plt.subplots(2,1,figsize=(10,6))
ax[0].plot(CLE_hist, label='CLE(t)')
ax[0].axhline(2.0, color='r', ls='--')
ax[0].set_title('Feedback Doom Loop: Anomaly → Rotation → Higher CLE')
ax[0].set_ylabel('CLE')
ax[0].legend()
ax[1].plot(flags, 'ro-')
ax[1].set_title('Anomaly Flags')
ax[1].set_xlabel('Day')
ax[1].set_ylabel('Flag')
plt.tight_layout()
plt.savefig('clem_doom.png')
print("   Plot saved: clem_doom.png\n")

# Pathology 5
print("5. Constraint infeasibility (CLE_ref=1.8 > limit=2.0)")
for CLE in [1.0,1.5,2.0,2.5]:
    feasible, psi = check_constraints(CLE)
    print(f"   CLE={CLE:.1f}, ψ={psi:.3f}, feasible={feasible}")
print()

# DISRUPTIVE INSIGHT
print("=== DISRUPTIVE INSIGHT ===")
print("\nThe 'flaws' are not bugs—they are criticality detectors.")
print("1. ξ_Δ divergence marks a phase transition: all credentials become")
print("   uniform (either perfect order or total collapse of differentiation).")
print("2. Zero‑entropy states reveal when risk has evacuated the system")
print("   or when monitoring is blind—use them as 'canary credentials'.")
print("3. The flawed jerk metric creates 'stability theater': MPC optimizes")
print("   appearance of stability while true instability grows masked.")
print("4. The feedback loop is a self‑DDoS on IAM—weaponize it:")
print("   let CLE drive credential changes via chaotic maps (logistic, tent)")
print("   to make prediction impossible for adversaries while bounding stability.")
print("\nSOLUTION: Don't patch the singularities—exploit them.")
print("→ Turn ξ_Δ → ∞ into an emergency 'credential re‑randomization' trigger.")
print("→ Deliberately create low‑entropy credential clusters as honeypots.")
print("→ Replace jerk stability with 'control entropy' (Kolmogorov complexity")
print("  of MPC action sequences).")
print("→ Feed the doom loop forward: CLE(t+1) = r·CLE(t)·(1−CLE(t)/K) + noise")
print("  to achieve cryptographically unpredictable rotation schedules.")
print("\nCLEM‑Ω v2 doesn't predict collapse—it *is* the collapse,")
print("reframed as a controlled demolition of predictable credential patterns.")