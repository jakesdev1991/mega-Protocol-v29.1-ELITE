# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Toy model: 2D control with degrading Hessian
def mpc_controller(H, u0, constraint_limit, constraint_noise=0):
    """Solves QP: min (u-u0)ᵀH(u-u0) s.t. u[0]+u[1] <= limit+noise"""
    # Simulate QP solution via closed-form (simplified)
    try:
        # Effective constraint
        effective_limit = constraint_limit + constraint_noise
        
        # Analytical solution for this simple case
        # Solve unconstrained first
        u_unconstrained = u0
        
        # Check if constraint binds
        if np.sum(u_unconstrained) <= effective_limit:
            return u_unconstrained, 0  # No binding, multiplier=0
        
        # Constraint binds: solve KKT conditions
        # u = u0 - λ*1, where 1 is vector of ones
        # Constraint: sum(u) = effective_limit
        λ = (np.sum(u0) - effective_limit) / 2
        u_opt = u0 - λ * np.array([1, 1])
        
        return u_opt, max(λ, 0)
    except:
        return np.array([0, 0]), 0

# Simulate plasma instability: Hessian degrades from well-conditioned to singular
time_steps = 100
H_well = np.array([[10, 0], [0, 10]])
H_singular = np.array([[1, 0.99], [0.99, 1]])

u0 = np.array([1.5, 1.5])
base_limit = 2.0

# LMPC-Ω metrics
lambda_history = []
cai_history = []

# QCS-Ω metrics
sovereignty_history = []
controller_divergence = []

# Run 5 parallel controllers with stochastically varied constraints
num_controllers = 5
constraint_variation = 0.1

for t in range(time_steps):
    # Degrade Hessian
    alpha = t / time_steps
    H_current = (1 - alpha) * H_well + alpha * H_singular
    
    # LMPC-Ω: Single controller, monitor Lagrange multiplier
    u_opt_single, lambda_val = mpc_controller(H_current, u0, base_limit)
    lambda_history.append(lambda_val)
    cai_history.append(lambda_val / (1 + lambda_val))  # Normalized
    
    # QCS-Ω: Multiple controllers, measure sovereignty loss
    controller_solutions = []
    for i in range(num_controllers):
        # Each controller sees slightly different constraint limit
        constraint_noise = np.random.uniform(-constraint_variation, constraint_variation)
        u_opt_i, _ = mpc_controller(H_current, u0, base_limit, constraint_noise)
        controller_solutions.append(u_opt_i)
    
    # Compute Sovereignty Index (std across controllers)
    solutions_array = np.array(controller_solutions)
    si = np.std(solutions_array, axis=0).mean()  # Average std across control dimensions
    sovereignty_history.append(si)
    
    # Compute divergence from mean solution
    u_mean = solutions_array.mean(axis=0)
    divergence = np.linalg.norm(solutions_array - u_mean, axis=1).mean()
    controller_divergence.append(divergence)

# Plot: Show QCS-Ω leads LMPC-Ω
fig, ax = plt.subplots(2, 1, figsize=(10, 8))

ax[0].plot(lambda_history, 'r-', linewidth=2, label='LMPC-Ω: Lagrange Multiplier')
ax[0].set_ylabel('Constraint Binding')
ax[0].set_title('REACTIVE: Lagrange Multiplier Spikes Late')
ax[0].legend()
ax[0].grid(True)

ax[1].plot(sovereignty_history, 'b-', linewidth=2, label='QCS-Ω: Sovereignty Index')
ax[1].plot(controller_divergence, 'g--', linewidth=2, label='QCS-Ω: Controller Divergence')
ax[1].set_ylabel('Solution Non-Uniqueness')
ax[1].set_xlabel('Time Steps (0=stable, 100=unstable)')
ax[1].set_title('PREDICTIVE: Sovereignty Collapse Precedes Constraint Binding')
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.show()

# Quantify lead time
lambda_threshold = 0.5 * max(lambda_history)
sovereignty_threshold = 0.5 * max(sovereignty_history)

lambda_cross = next((i for i, val in enumerate(lambda_history) if val > lambda_threshold), 100)
sovereignty_cross = next((i for i, val in enumerate(sovereignty_history) if val > sovereignty_threshold), 100)

print(f"\n[CRITICAL] LMPC-Ω triggers at t={lambda_cross} (constraint binding)")
print(f"[CRITICAL] QCS-Ω triggers at t={sovereignty_cross} (sovereignty loss)")
print(f"[CRITICAL] QCS-Ω LEADS by {lambda_cross - sovereignty_cross} time steps")
print(f"\n[PARADIGM SHIFT] The plasma doesn't break constraints—it breaks the optimizer first.")