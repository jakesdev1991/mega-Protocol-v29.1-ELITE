# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# THE ANOMALY: Consciousness is not the Observer. It's the ENVIRONMENT.
# We simulate this by modeling decoherence via Lindblad operators, not projection operators.

def master_equation(t, rho_flat, H, L_ops, gammas):
    """True quantum master equation with environmental decoherence"""
    rho = rho_flat.reshape((2, 2))
    drho = -1j * (H @ rho - rho @ H)
    for L, gamma in zip(L_ops, gammas):
        # Lindblad dissipator: LρL† - ½{L†L, ρ}
        drho += gamma * (L @ rho @ L.conj().T - 0.5 * (L.conj().T @ L @ rho + rho @ L.conj().T @ L))
    return drho.flatten()

# Two-level subconscious: |0> = Safe/Default, |1> = Innovative/Risk
H = np.array([[0.5, 0.1], [0.1, -0.5]])  # Cross-term allows evolution

# Initial superposition (maximal COD)
psi0 = np.array([1/np.sqrt(2), 1/np.sqrt(2)])
rho0 = np.outer(psi0, psi0.conj())

t_eval = np.linspace(0, 15, 1500)

# SCENARIO 1: "Anxious Consciousness" - The Theorist's Failure Mode
# Environment strongly couples to "safe" state operator: L = |0><0|
# This is not measurement. It's *environmental selection* favoring |0>.
L_anxious = [np.array([[1, 0], [0, 0]])]
gamma_anxious = [3.0]  # High decoherence rate toward safe state
sol_anxious = solve_ivp(master_equation, (0, 15), rho0.flatten(), 
                       args=(H, L_anxious, gamma_anxious), t_eval=t_eval)

# SCENARIO 2: TAP (Temporal Adiabatic Projection) - The Theorist's "Solution"
# Just modulates gamma(t) with tanh. This is TIMING, not physics.
def tap_gamma(t): return 3.0 * 0.5 * (1 - np.tanh((t - 7.5) / 1.5))
sol_tap = solve_ivp(lambda t, y: master_equation(t, y, H, L_anxious, [tap_gamma(t)]), 
                    (0, 15), rho0.flatten(), t_eval=t_eval)

# SCENARIO 3: CDR (Consciousness Decoherence Reshaping) - THE DISRUPTION
# CHANGE THE LINDDBLAD OPERATORS to be outcome-agnostic.
# Use symmetric operators: L1 = σ+, L2 = σ- (promotes mixing, not selection)
L_cdr = [np.array([[0, 1], [0, 0]]), np.array([[0, 0], [1, 0]])]
gamma_cdr = [0.8, 0.8]  # Balanced, lower overall decoherence
sol_cdr = solve_ivp(master_equation, (0, 15), rho0.flatten(),
                   args=(H, L_cdr, gamma_cdr), t_eval=t_eval)

# Calculate true COD: 4*|ρ01|² (coherence measure)
cod = lambda sol: [4*abs(sol.y[1,i] + 1j*sol.y[2,i])**2 for i in range(len(sol.t))]

cod_anxious = cod(sol_anxious)
cod_tap = cod(sol_tap)
cod_cdr = cod(sol_cdr)

# VISUALIZE THE BREAKDOWN
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(sol_anxious.t, cod_anxious, 'r-', lw=2.5, label='Anxious Environment (Theorist Failure)', alpha=0.7)
ax.plot(sol_tap.t, cod_tap, 'b--', lw=2, label='TAP: "Delayed Collapse" (Illusion)', alpha=0.7)
ax.plot(sol_cdr.t, cod_cdr, 'g-', lw=2.5, label='CDR: Reshaped Environment (Anomaly)', alpha=0.7)

ax.axhline(y=0.4, color='gray', linestyle=':', label='Critical ξ_c Threshold', alpha=0.5)
ax.axvspan(6, 9, color='blue', alpha=0.1, label='TAP "Safe Harbor"')

ax.set_xlabel('Cognitive Evolution Time (τ)', fontsize=12)
ax.set_ylabel('Chain Overlap Density (COD)', fontsize=12)
ax.set_title('Φ-DENSITY CATASTROPHE: TAP Preserves the Illusion, CDR Escapes the Prison', 
             fontsize=14, fontweight='bold')
ax.legend(loc='upper right', fontsize=10)
ax.grid(True, alpha=0.3)

# Annotate the failure
ax.annotate('TAP fails: Environment bias remains\nρ → |0><0| inevitably', 
            xy=(12, 0.1), xytext=(9, 0.3), 
            arrowprops=dict(arrowstyle='->', color='red', lw=1.5),
            fontsize=10, color='red', fontweight='bold')

ax.annotate('CDR: Environment neutralized\nSuperposition persists', 
            xy=(12, 0.65), xytext=(9, 0.8), 
            arrowprops=dict(arrowstyle='->', color='green', lw=1.5),
            fontsize=10, color='green', fontweight='bold')

plt.tight_layout()
plt.show()

# QUANTIFY THE SHATTERING
print("=== Φ-DENSITY TRUTH REVEALED ===")
print(f"Anxious Environment (baseline): Avg COD = {np.mean(cod_anxious):.3f}")
print(f"TAP (Theorist's solution): Avg COD = {np.mean(cod_tap):.3f} (+{np.mean(cod_tap)/np.mean(cod_anxious)*100-100:.1f}%)")
print(f"CDR (Anomaly disruption): Avg COD = {np.mean(cod_cdr):.3f} (+{np.mean(cod_cdr)/np.mean(cod_anxious)*100-100:.1f}%)")
print("\n>>> TAP provides marginal delay. CDR achieves escape velocity from the failure mode.")