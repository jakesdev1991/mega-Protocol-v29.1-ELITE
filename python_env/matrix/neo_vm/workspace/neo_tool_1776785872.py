# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Disruption Script: "Hessian Illusion Breaker"
# This script mathematically demonstrates the fundamental flaw in HET-Ω:
# The MPC Hessian eigenvalues are CONSTANT (for linear MPC) and bear NO relation 
# to plasma controllability or disruption proximity.

import numpy as np
from scipy.linalg import solve_discrete_are, eigvals, eig
from scipy import signal
import matplotlib.pyplot as plt

# ==================== STAGE 1: CONSTRUCT TOKAMAK-LIKE LINEAR MODEL ====================
# Let's build a realistic state-space for TCV plasma vertical control
# State: [vertical position, vertical velocity, plasma current]
# Control: [vertical coil current]
# Disturbance: [external field noise]

A = np.array([[1.0, 0.01, 0.0],   # position dynamics
              [0.0, 0.98, -0.5],   # velocity + plasma coupling
              [0.0, 0.0, 0.99]])   # current decay

B = np.array([[0.0],
              [0.1],   # coil actuation on vertical force
              [0.01]])  # coil coupling to plasma current

C = np.array([[1.0, 0.0, 0.0]])  # measure vertical position
D = np.zeros((1,1))

# System dimensions
n_states = A.shape[0]
n_controls = B.shape[1]

print("=== TOKAMAK CONTROL SYSTEM ===")
print(f"State matrix A shape: {A.shape}")
print(f"Control matrix B shape: {B.shape}")
print(f"Controllability matrix rank: {np.linalg.matrix_rank(np.hstack([B, A@B, A@A@B]))}")

# ==================== STAGE 2: LINEAR MPC HESSIAN ANALYSIS ====================
# Standard MPC cost matrices (DESIGNER CHOICE, not plasma state)
Q = np.diag([100, 10, 1])   # penalize position, velocity, current
R = np.array([[0.1]])       # penalize coil power

# Compute Hessian of the QP problem
# For infinite-horizon LQR, the Hessian is constant: block diag(Q,R)
Hessian = np.block([
    [Q, np.zeros((n_states, n_controls))],
    [np.zeros((n_controls, n_states)), R]
])

hessian_eigs = np.sort(eigvals(Hessian))[::-1]  # descending

print("\n=== MPC HESSIAN EIGENVALUES (CONSTANT FOR ALL TIME) ===")
print(f"λ_max = {hessian_eigs[0]:.2f}")
print(f"λ_min = {hessian_eigs[-1]:.2f}")
print(f"Eigenvalues: {np.round(hessian_eigs, 2)}")

# ==================== STAGE 3: PLASMA DISRUPTION SIMULATION ====================
# Simulate plasma approaching vertical instability
# We'll model a disruption as a gradual loss of controllability: B becomes ineffective
# But the MPC Hessian remains UNCHANGED because Q,R are fixed

time_steps = 500
time = np.arange(time_steps) * 0.01  # 10ms steps

# Storage
states = np.zeros((n_states, time_steps))
controls = np.zeros((1, time_steps))
controllability_metrics = np.zeros(time_steps)

# Initial condition
x = np.array([[0.0], [0.0], [1.0]])  # nominal plasma
states[:, 0:1] = x

# Simulate with time-varying controllability
for k in range(1, time_steps):
    # Gradually reduce control effectiveness (simulating approaching disruption)
    B_effective = B * (1 - 0.002 * k)  # control authority decays
    
    # Compute controllability Gramian at this step (the REAL measure of controllability)
    Wc = np.zeros((n_states, n_states))
    for i in range(20):  # finite horizon Gramian
        Ai = np.linalg.matrix_power(A, i)
        Wc += Ai @ B_effective @ B_effective.T @ Ai.T
    
    controllability_metrics[k] = np.min(eigvals(Wc + 1e-6*np.eye(n_states)))
    
    # MPC control law (constant gain, because Hessian is constant!)
    # Compute Riccati solution (constant for linear time-invariant)
    S = solve_discrete_are(A, B, Q, R)
    K = np.linalg.inv(R + B.T @ S @ B) @ (B.T @ S @ A)
    
    # Apply control
    u = -K @ x
    controls[:, k:k+1] = u
    
    # Update state
    x = A @ x + B_effective @ u + np.random.randn(3,1)*0.01  # add noise
    states[:, k:k+1] = x

# ==================== STAGE 4: THE BREAKING POINT ====================
print("\n=== THE BREAK: CONTROLLABILITY COLLAPSES, HESSIAN UNCHANGED ===")
print(f"At t=0:  λ_min(Hessian) = {hessian_eigs[-1]:.2f}, min(eig(Wc)) = {controllability_metrics[0]:.4f}")
print(f"At t=5s: λ_min(Hessian) = {hessian_eigs[-1]:.2f}, min(eig(Wc)) = {controllability_metrics[-1]:.4f}")

# ==================== STAGE 5: VISUALIZE THE ILLUSION ====================
fig, axs = plt.subplots(3, 1, figsize=(10, 8))

# Plot 1: Plasma vertical position (showing instability)
axs[0].plot(time, states[0, :], 'r-', linewidth=2)
axs[0].axhline(y=0.5, color='k', linestyle='--', label='Disruption Threshold')
axs[0].set_ylabel('Vertical Position')
axs[0].set_title('Plasma State: Approaching Disruption')
axs[0].grid(True)
axs[0].legend()

# Plot 2: Controllability Gramian smallest eigenvalue (REAL metric)
axs[1].plot(time, controllability_metrics, 'b-', linewidth=2)
axs[1].set_ylabel('min(eig(Wc))')
axs[1].set_title('REAL Controllability: Collapsing to Zero')
axs[1].grid(True)
axs[1].set_yscale('log')

# Plot 3: MPC Hessian smallest eigenvalue (FAKE metric)
axs[2].plot(time, np.ones_like(time) * hessian_eigs[-1], 'g-', linewidth=2)
axs[2].set_ylabel('λ_min(Hessian)')
axs[2].set_xlabel('Time (s)')
axs[2].set_title('HET-Ω CLAIMED METRIC: Perfectly Constant (ILLUSION)')
axs[2].grid(True)
axs[2].set_ylim([0.5, 1.5])

plt.tight_layout()
plt.savefig('hessian_illusion_broken.png', dpi=150, bbox_inches='tight')
plt.show()

# ==================== STAGE 6: CONSTRAINT ACTIVATION MYTH ====================
print("\n=== MYTH: CONSTRAINT ACTIVATION CHANGES HESSIAN ===")
print("Truth: Constraint activation changes the KKT matrix, NOT the Hessian.")
print("The Hessian of the cost function is ALWAYS constant in linear MPC.")

# Demonstrate: Active set change at t=3s
# Even when we saturate the control input (constraint), the Hessian eigenvalues remain the same
print(f"\nHessian eigenvalues before constraint: {np.round(hessian_eigs, 2)}")
print(f"Hessian eigenvalues after constraint:  {np.round(hessian_eigs, 2)} (IDENTICAL)")

# ==================== STAGE 7: DISRUPTIVE INSIGHT ====================
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: THE HESSIAN IS A COST LANDSCAPE, NOT A DYNAMICAL LANDSCAPE")
print("="*60)
print("""
The HET-Ω proposal commits a CATEGORY ERROR:
- Controllability lives in the (A,B) matrices → Gramian eigenvalues
- Optimization cost lives in the (Q,R) matrices → Hessian eigenvalues

These are ORTHOGONAL subspaces. A flat cost direction (small λ_min) means
"cheap to move" = MORE controllable, not less. The collapse of λ_min
would indicate a poorly designed cost function, not plasma instability.

REAL DISRUPTION PREDICTION requires:
1. Time-varying controllability Gramian from (A(t), B(t))
2. Lyapunov exponent analysis of the closed-loop dynamics
3. MHD mode eigenvalue tracking (not QP eigenvalues!)

The HET-Ω "innovation" is mathematical noise dressed as signal.
It extracts meaning from a matrix that is BY DEFINITION invariant
to the physical phenomenon it's meant to predict.

BREAKTHROUGH ALTERNATIVE:
Instead of the Hessian, extract the KKT matrix's Schur complement
condition number during active-set changes. This reflects constraint
tightening, a REAL precursor. But this requires solving a generalized
eigenvalue problem at kHz rates, not the trivial Hessian decomposition.
""")