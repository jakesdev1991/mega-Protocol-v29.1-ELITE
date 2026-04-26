# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ──────────────────────────────────────────────────────────────────────────────
# Simulation Parameters
# ──────────────────────────────────────────────────────────────────────────────
Ξ_supp = 2.0          # Suppression stiffness (fixed)
Ξ_safe_0 = 0.5        # Initial safety stiffness
γ_adiabatic = 0.01    # Adiabatic integration rate (per hour)
t_max = 500           # Simulation horizon (hours)
dt = 0.1              # Time step

# ──────────────────────────────────────────────────────────────────────────────
# Model Functions
# ──────────────────────────────────────────────────────────────────────────────
def compute_COD(ΔΞ, α=2.0):
    """Chain Overlap Density: logistic function of stiffness mismatch."""
    return 1.0 / (1.0 + np.exp(α * ΔΞ))

def compute_Φ_N(COD):
    """Identity density: -log₂(1-COD)."""
    return -np.log2(1.0 - COD + 1e-9)

def compute_Φ_Δ(ψ, ΔΞ, R_max=3.0):
    """Adaptation asymmetry: ψ * tanh(max(0, ΔΞ)/R_max)."""
    return ψ * np.tanh(max(0.0, ΔΞ) / R_max)

def compute_H_trauma(ΔΞ, H_max=1.0, β=0.5):
    """Shannon conditional entropy of trauma."""
    return H_max * np.exp(-β * max(0.0, -ΔΞ))  # decays when safety > suppression

def compute_Φ_net(Ξ_safe, Ξ_supp, H_trauma):
    """Total Φ-density with audit cost."""
    ΔΞ = Ξ_supp - Ξ_safe
    COD = compute_COD(ΔΞ)
    Φ_N = compute_Φ_N(COD)
    ψ = np.log(Φ_N + 1e-9)
    Φ_Δ = compute_Φ_Δ(ψ, ΔΞ)
    ΔS_audit = np.log(2) * 6   # 6 Smith invariants
    return Φ_N + Φ_Δ - ΔS_audit, COD, Φ_N, ψ, H_trauma

def check_invariants(Ξ_safe, Ξ_supp, COD, ψ, H_trauma):
    """Return True if all invariants satisfied."""
    return (
        COD >= 0.75 and
        ψ >= np.log(0.95) and
        Ξ_safe >= Ξ_supp and
        H_trauma <= 0.80
    )

# ──────────────────────────────────────────────────────────────────────────────
# Adiabatic Integration Run
# ──────────────────────────────────────────────────────────────────────────────
t_adiabatic = np.arange(0, t_max, dt)
Ξ_safe_adiabatic = np.empty_like(t_adiabatic)
Φ_net_adiabatic = np.empty_like(t_adiabatic)
COD_adiabatic = np.empty_like(t_adiabatic)
invariant_adiabatic = np.empty_like(t_adiabatic, dtype=bool)

Ξ_safe = Ξ_safe_0
for i, t in enumerate(t_adiabatic):
    # Adiabatic update: exponential approach to Ξ_supp
    Ξ_safe = Ξ_safe_0 * np.exp(γ_adiabatic * t) + Ξ_supp * (1 - np.exp(γ_adiabatic * t))
    Ξ_safe = min(Ξ_safe, Ξ_supp)  # Clamp at equality
    Ξ_safe_adiabatic[i] = Ξ_safe
    
    ΔΞ = Ξ_supp - Ξ_safe
    H = compute_H_trauma(ΔΞ)
    Φ_net, COD, Φ_N, ψ, _ = compute_Φ_net(Ξ_safe, Ξ_supp, H)
    Φ_net_adiabatic[i] = Φ_net
    COD_adiabatic[i] = COD
    invariant_adiabatic[i] = check_invariants(Ξ_safe, Ξ_supp, COD, ψ, H)

# ──────────────────────────────────────────────────────────────────────────────
# Quench-Induced Phase Transition (QIPT) Run
# ──────────────────────────────────────────────────────────────────────────────
t_quench = np.arange(0, t_max, dt)
Ξ_safe_quench = np.empty_like(t_quench)
Φ_net_quench = np.empty_like(t_quench)
COD_quench = np.empty_like(t_quench)
invariant_quench = np.empty_like(t_quench, dtype=bool)

Ξ_safe = Ξ_safe_0
quench_triggered = False
for i, t in enumerate(t_quench):
    # Trigger quench at t = 100h: invert stiffness, then nucleate new manifold
    if t >= 100.0 and not quench_triggered:
        # Phase 1: Inversion (0.1·Ξ_supp) for 1 hour
        Ξ_safe = 0.1 * Ξ_supp
        quench_triggered = True
    elif t >= 101.0 and quench_triggered:
        # Phase 2: Nucleation (2·Ξ_supp) instantaneously
        Ξ_safe = 2.0 * Ξ_supp
    # After nucleation, clamp at new high safety
    Ξ_safe = max(Ξ_safe, 2.0 * Ξ_supp)  # keep high
    Ξ_safe_quench[i] = Ξ_safe
    
    ΔΞ = Ξ_supp - Ξ_safe
    H = compute_H_trauma(ΔΞ)
    Φ_net, COD, Φ_N, ψ, _ = compute_Φ_net(Ξ_safe, Ξ_supp, H)
    Φ_net_quench[i] = Φ_net
    COD_quench[i] = COD
    invariant_quench[i] = check_invariants(Ξ_safe, Ξ_supp, COD, ψ, H)

# ──────────────────────────────────────────────────────────────────────────────
# Results
# ──────────────────────────────────────────────────────────────────────────────
final_adiabatic_Φ = Φ_net_adiabatic[-1]
final_quench_Φ = Φ_net_quench[-1]
final_adiabatic_COD = COD_adiabatic[-1]
final_quench_COD = COD_quench[-1]
adiabatic_invariant_ok = invariant_adiabatic[-1]
quench_invariant_ok = invariant_quench[-1]

print("─" * 70)
print(f"Final Adiabatic: Φ_net = {final_adiabatic_Φ:.3f}, COD = {final_adiabatic_COD:.3f}, Invariants OK = {adiabatic_invariant_ok}")
print(f"Final Quench:    Φ_net = {final_quench_Φ:.3f}, COD = {final_quench_COD:.3f}, Invariants OK = {quench_invariant_ok}")
print("─" * 70)

# Plotting
fig, ax = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

ax[0].plot(t_adiabatic, Ξ_safe_adiabatic, label='Adiabatic Ξ_safe')
ax[0].plot(t_quench, Ξ_safe_quench, label='Quench Ξ_safe')
ax[0].axhline(Ξ_supp, color='k', linestyle='--', label='Ξ_supp')
ax[0].set_ylabel('Safety Stiffness')
ax[0].legend()
ax[0].set_title('Stiffness Dynamics: Adiabatic vs Quench')

ax[1].plot(t_adiabatic, Φ_net_adiabatic, label='Adiabatic Φ_net')
ax[1].plot(t_quench, Φ_net_quench, label='Quench Φ_net')
ax[1].axhline(0, color='k', linestyle=':')
ax[1].set_ylabel('Φ‑density')
ax[1].legend()
ax[1].set_title('Φ‑density Evolution')

ax[2].plot(t_adiabatic, COD_adiabatic, label='Adiabatic COD')
ax[2].plot(t_quench, COD_quench, label='Quench COD')
ax[2].axhline(0.75, color='r', linestyle='--', label='Invariant Threshold')
ax[2].set_xlabel('Time (hours)')
ax[2].set_ylabel('COD')
ax[2].legend()
ax[2].set_title('Chain Overlap Density')

plt.tight_layout()
plt.show()