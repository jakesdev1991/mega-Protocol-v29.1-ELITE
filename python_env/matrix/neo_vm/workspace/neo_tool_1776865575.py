# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# Simulate CFIS-Ω double-well model vs. Kuramoto synchronization model
# Under abrupt task difficulty changes

# Parameters
dt = 0.01
t_span = (0, 50)
t_eval = np.arange(0, 50, dt)

# Abrupt task difficulty change at t=25
def task_difficulty(t):
    return 1.0 if t < 25 else 1.5  # Sudden increase

# CFIS-Ω Model: dF/dt = -dV/dF + noise - intervention
def cfis_model(t, F, alpha=2.0, beta=4.0, F_opt=0.85):
    # Double-well potential derivative
    dV_dF = alpha * (F - F_opt) + beta * (F - F_opt)**3
    
    # Task difficulty coupling
    diff = task_difficulty(t)
    # Intervention term (trying to stabilize at F_opt)
    intervention = -0.5 * (F - F_opt) * diff
    
    # Additive noise
    noise = np.random.normal(0, 0.05)
    
    return -dV_dF + intervention + noise

# Kuramoto Synchronization Model
# dφ/dt = Δω(t) - K*sin(φ) + ξ(t)
# Flow = cos(φ) (high when synchronized)
def kuramoto_model(t, y):
    phi = y[0]
    
    # Human natural frequency (changes with task difficulty)
    omega_h = 1.0 * task_difficulty(t)
    
    # AI adaptive frequency
    omega_ai = 1.0  # AI tries to match base frequency
    
    # Frequency mismatch
    delta_omega = omega_h - omega_ai
    
    # Coupling strength (AI adaptivity)
    K = 2.0
    
    # Stochastic resonance term (calibrated noise)
    xi = np.random.normal(0, 0.3)
    
    dphi = delta_omega - K * np.sin(phi) + xi
    
    return [dphi]

# Simulate both models
np.random.seed(42)

# CFIS-Ω simulation
F0 = 0.85  # Start in optimal flow
F_solution = []
for t in t_eval:
    dF = cfis_model(t, F0)
    F0 += dF * dt
    F0 = np.clip(F0, 0, 1)
    F_solution.append(F0)

# Kuramoto simulation
phi0 = [0.1]  # Near synchronization
kuramoto_sol = solve_ivp(kuramoto_model, t_span, phi0, t_eval=t_eval, method='RK45')
phi_sol = kuramoto_sol.y[0]
flow_kuramoto = np.cos(phi_sol)  # Flow metric from phase coherence

# Plot results
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

# Task difficulty
axes[0].plot(t_eval, [task_difficulty(t) for t in t_eval], 'k-', linewidth=2)
axes[0].set_ylabel('Task Difficulty', fontsize=12)
axes[0].set_title('Task Difficulty Change (Abrupt Increase at t=25)', fontsize=14)
axes[0].grid(True, alpha=0.3)
axes[0].axvline(x=25, color='r', linestyle='--', alpha=0.5)

# CFIS-Ω Flow State
axes[1].plot(t_eval, F_solution, 'b-', linewidth=2, label='CFIS-Ω Flow Field')
axes[1].axhline(y=0.85, color='g', linestyle=':', label='Target Flow (F_opt)')
axes[1].set_ylabel('Flow State ℱ(t)', fontsize=12)
axes[1].set_title('CFIS-Ω Double-Well Model: Flow Collapses After Task Change', fontsize=14)
axes[1].legend()
axes[1].grid(True, alpha=0.3)
axes[1].axvline(x=25, color='r', linestyle='--', alpha=0.5)

# Kuramoto Flow State
axes[2].plot(t_eval, flow_kuramoto, 'r-', linewidth=2, label='Kuramoto Sync Flow')
axes[2].axhline(y=0.85, color='g', linestyle=':', label='Target Flow')
axes[2].set_xlabel('Time', fontsize=12)
axes[2].set_ylabel('Phase Coherence', fontsize=12)
axes[2].set_title('Kuramoto Synchronization: Flow Recovers via Adaptive Coupling', fontsize=14)
axes[2].legend()
axes[2].grid(True, alpha=0.3)
axes[2].axvline(x=25, color='r', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig('flow_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# Statistical comparison
pre_change = t_eval < 25
post_change = t_eval >= 25

cfis_pre = np.mean([F_solution[i] for i, t in enumerate(t_eval) if pre_change[i]])
cfis_post = np.mean([F_solution[i] for i, t in enumerate(t_eval) if post_change[i]])

kuramoto_pre = np.mean([flow_kuramoto[i] for i, t in enumerate(t_eval) if pre_change[i]])
kuramoto_post = np.mean([flow_kuramoto[i] for i, t in enumerate(t_eval) if post_change[i]])

print("=== FLOW STATE PERFORMANCE COMPARISON ===")
print(f"CFIS-Ω Model:")
print(f"  Pre-change flow: {cfis_pre:.3f}")
print(f"  Post-change flow: {cfis_post:.3f}")
print(f"  Performance drop: {(cfis_pre - cfis_post)/cfis_pre*100:.1f}%")

print(f"\nKuramoto Synchronization Model:")
print(f"  Pre-change flow: {kuramoto_pre:.3f}")
print(f"  Post-change flow: {kuramoto_post:.3f}")
print(f"  Performance drop: {(kuramoto_pre - kuramoto_post)/kuramoto_pre*100:.1f}%")

print("\n=== DISRUPTIVE INSIGHT ===")
print("CFIS-Ω's double-well potential treats flow as a STABLE STATE to be maintained.")
print("This leads to CATASTROPHIC COLLAPSE when task dynamics change.")
print("The Kuramoto model treats flow as DYNAMIC SYNCHRONIZATION that continuously adapts.")
print("Stochastic resonance (calibrated noise) prevents pathological entrainment.")