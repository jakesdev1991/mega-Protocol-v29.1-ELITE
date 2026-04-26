# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulation parameters
T = 50  # time steps
psi_target = -2.0  # target psi (negative, so |psi_target| = 2.0)
initial_psi = 0.0  # starting psi
mu2 = 0.1  # control cost weight
learning_rate = 0.01
iterations = 1000

# Initialize psi trajectory
psi = np.full(T, initial_psi)

# Gradient descent to minimize the cost functional
for _ in range(iterations):
    grad = np.zeros(T)
    # Cost: sum_t [ (psi_target - psi[t])^2 + mu2 * (psi[t] - psi[t-1])^2 for t>=1 ]
    for t in range(T):
        # Term 1: (psi_target - psi[t])^2
        grad[t] += -2 * (psi_target - psi[t])
        # Term 2: control cost (only for t>=1 and t<=T-2)
        if t > 0:
            grad[t] += 2 * mu2 * (psi[t] - psi[t-1])
        if t < T-1:
            grad[t] += -2 * mu2 * (psi[t+1] - psi[t])
    # Update psi
    psi -= learning_rate * grad

# Compute xi_delta = exp(|psi|) (ignoring proportionality constant)
xi_delta = np.exp(np.abs(psi))

# Plot results
plt.figure(figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.plot(psi, 'b-', linewidth=2)
plt.axhline(y=psi_target, color='r', linestyle='--', label='psi_target')
plt.ylabel('$\psi(t)$')
plt.title('Psi Trajectory and Target')
plt.legend()
plt.grid(True)

plt.subplot(2, 1, 2)
plt.plot(xi_delta, 'g-', linewidth=2)
plt.axhline(y=np.exp(np.abs(psi_target)), color='r', linestyle='--', label='xi_delta_target')
plt.ylabel('$\xi_\Delta(t) \\propto e^{|\psi|}$')
plt.xlabel('Time Step')
plt.title('Code Distance Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Print final values
print(f"Initial psi: {initial_psi:.3f} -> initial xi_delta: {np.exp(np.abs(initial_psi)):.3f}")
print(f"Final psi: {psi[-1]:.3f} -> final xi_delta: {np.exp(np.abs(psi[-1])):.3f}")
print(f"Target psi: {psi_target:.3f} -> target xi_delta: {np.exp(np.abs(psi_target)):.3f}")
print("\nKey Observation:")
print("- Psi converges to psi_target (~ -2.0)")
print("- xi_delta converges to exp(|psi_target|) ≈ 7.389 and remains constant")
print("- xi_delta does NOT increase over time; it stabilizes after transient")
print("- Claim of increasing xi_delta (and thus increasing resilience) over time is NOT supported by the cost functional")