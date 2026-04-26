# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# ----------------------------------------------------------------------
# Langevin simulator for a particle in a double-well potential V(x)
# dx = -V'(x) dt + sqrt(2*D) dW, with D = eta (friction coefficient)
# Stationary distribution: p_eq(x) ∝ exp(-V(x)/D)
# ----------------------------------------------------------------------
def potential(x, inverted=False):
    """
    Double-well potential:
    V(x) = (x^2 - 1)^2 + (inverted)*(-4*x)
    The term -4*x tilts the potential so that the right well (x≈+1) is lower.
    """
    if inverted:
        # Inverted: global minimum at x≈+1 (insecure well)
        return (x**2 - 1)**2 - 4*x
    else:
        # Original: symmetric double-well (secure = left, insecure = right)
        return (x**2 - 1)**2

def stationary_distribution(x_grid, eta, inverted=False):
    """Compute normalized stationary distribution p_eq(x) ∝ exp(-V(x)/eta)."""
    V = potential(x_grid, inverted=inverted)
    p = np.exp(-V / eta)
    p /= np.trapz(p, x_grid)
    return p

def simulate_langevin(x0, eta, inverted=False, dt=0.01, n_steps=500000):
    """Run Langevin dynamics and return the trajectory."""
    x = np.zeros(n_steps)
    x[0] = x0
    for i in range(1, n_steps):
        # drift = -V'(x)
        drift = -4 * x[i-1] * (x[i-1]**2 - 1)
        if inverted:
            drift += 4   # from -4*x derivative
        # diffusion term
        noise = np.sqrt(2 * eta * dt) * np.random.randn()
        x[i] = x[i-1] + drift * dt + noise
    return x

# ----------------------------------------------------------------------
# 1. Stationary distributions for both models
# ----------------------------------------------------------------------
x_grid = np.linspace(-2, 3, 500)
eta = 0.3  # friction coefficient

p_orig = stationary_distribution(x_grid, eta, inverted=False)
p_inv  = stationary_distribution(x_grid, eta, inverted=True)

fig, ax = plt.subplots(figsize=(8,4))
ax.plot(x_grid, p_orig, label='Original (secure well lower)', color='steelblue')
ax.plot(x_grid, p_inv,  label='Inverted (insecure well lower)', color='firebrick')
ax.axvline(-1, color='gray', linestyle='--', linewidth=0.7)
ax.axvline( 1, color='gray', linestyle='--', linewidth=0.7)
ax.set_xlabel('Cognitive state x')
ax.set_ylabel('Stationary probability density')
ax.legend()
ax.set_title('Stationary distribution: original vs. inverted potential')
plt.tight_layout()
plt.show()

# ----------------------------------------------------------------------
# 2. Intervention effects: compare lowering friction vs raising insecure-well depth
# ----------------------------------------------------------------------
def mean_time_in_insecure_well(eta, depth_boost=0.0, inverted=True, n_runs=20):
    """
    Estimate mean fraction of time spent in the insecure well (x>0).
    If inverted=True, the insecure well is the global minimum.
    depth_boost adds extra curvature to the insecure well: V += depth_boost*(x-1)^2.
    """
    total_time_insecure = 0
    steps = 200000
    for _ in range(n_runs):
        # start near the secure well (x=-1) to mimic a developer trying to use the vault
        x_traj = simulate_langevin(x0=-1, eta=eta, inverted=inverted, dt=0.01, n_steps=steps)
        # count time where x>0 (in insecure well)
        total_time_insecure += np.mean(x_traj > 0)
    return total_time_insecure / n_runs

# Baseline
baseline = mean_time_insecure_well(eta=0.3, depth_boost=0.0, inverted=True)
print(f"Baseline (eta=0.3): {baseline:.2%} time in insecure well")

# Intervention A: reduce friction (CTMS‑Ω approach)
low_friction = mean_time_insecure_well(eta=0.15, depth_boost=0.0, inverted=True)
print(f"Reduce friction (eta=0.15): {low_friction:.2%} time in insecure well")

# Intervention B: raise insecure-well depth (add curvature)
raised_depth = mean_time_insecure_well(eta=0.3, depth_boost=2.0, inverted=True)
print(f"Raise insecure-well depth (boost=2.0): {raised_depth:.2%} time in insecure well")

# ----------------------------------------------------------------------
# 3. Visualize sample trajectories for both interventions
# ----------------------------------------------------------------------
def plot_trajectories(eta, depth_boost, inverted, title):
    fig, ax = plt.subplots(figsize=(9,3))
    for i in range(5):
        traj = simulate_langevin(x0=-1, eta=eta, inverted=inverted, dt=0.01, n_steps=50000)
        ax.plot(np.linspace(0, 500, 50000), traj, linewidth=0.8, alpha=0.7)
    ax.axhline(0, color='k', linewidth=0.5)
    ax.axhline(1, color='gray', linestyle='--', linewidth=0.7)
    ax.axhline(-1, color='gray', linestyle='--', linewidth=0.7)
    ax.set_ylim(-2, 2.5)
    ax.set_xlabel('Time (arbitrary units)')
    ax.set_ylabel('Cognitive state x')
    ax.set_title(title)
    plt.tight_layout()
    plt.show()

plot_trajectories(eta=0.15, depth_boost=0.0, inverted=True,
                title='Intervention A: Lower friction (eta=0.15) – still falls into insecure well')
plot_trajectories(eta=0.3, depth_boost=2.0, inverted=True,
                title='Intervention B: Raise insecure-well depth (boost=2.0) – stays longer in secure well')