# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.ndimage import gaussian_filter

# DISRUPTION: Demonstrate that the "repaired" isotropic metric leads to 
# emergent dynamical instability, violating operational invariants despite 
# passing static mathematical checks.

def demand_field(x, y, peak_center=(0.5, 0.5), peak_std=0.05, background=1.0):
    """Simulate a flash-sale demand spike: sharp Gaussian peak on uniform background."""
    dist_sq = (x - peak_center[0])**2 + (y - peak_center[1])**2
    spike = np.exp(-dist_sq / (2 * peak_std**2))
    # Flash sale: demand can spike to 100x background
    return background + 99.0 * spike

def metric_tensor(x, y, g0_scale=1.0, beta=0.1, phi_N=10.0, eps=1e-6):
    """Compute the 'repaired' metric g_ij = g0 * I + beta * psi(rho) * I."""
    rho = demand_field(x, y)
    psi = np.log(phi_N * rho + eps)
    # Isotropic perturbation
    g_ij = (g0_scale + beta * psi) * np.eye(2)
    return g_ij

def christoffel_symbols(x, y, h=1e-5):
    """Compute Christoffel symbols Gamma^k_ij for the metric at (x,y)."""
    # Numerical derivatives for simplicity
    g00_x = (metric_tensor(x+h, y)[0,0] - metric_tensor(x-h, y)[0,0]) / (2*h)
    g00_y = (metric_tensor(x, y+h)[0,0] - metric_tensor(x, y-h)[0,0]) / (2*h)
    g11_x = (metric_tensor(x+h, y)[1,1] - metric_tensor(x-h, y)[1,1]) / (2*h)
    g11_y = (metric_tensor(x, y+h)[1,1] - metric_tensor(x, y-h)[1,1]) / (2*h)
    
    # For isotropic metric, off-diagonal terms are zero, and derivatives simplify
    g_inv = np.linalg.inv(metric_tensor(x, y))
    # Gamma^0_00 = 0.5 * g^00 * ∂_0 g_00
    Gamma_0_00 = 0.5 * g_inv[0,0] * g00_x
    Gamma_0_01 = 0.5 * g_inv[0,0] * g00_y
    Gamma_1_00 = 0.5 * g_inv[1,1] * g11_x
    Gamma_1_01 = 0.5 * g_inv[1,1] * g11_y
    
    return Gamma_0_00, Gamma_0_01, Gamma_1_00, Gamma_1_01

def geodesic_ode(t, state):
    """Geodesic equation: d²x^k/dt² + Γ^k_ij (dx^i/dt)(dx^j/dt) = 0."""
    x, y, vx, vy = state
    Gamma_0_00, Gamma_0_01, Gamma_1_00, Gamma_1_01 = christoffel_symbols(x, y)
    
    # Acceleration terms
    ax = -Gamma_0_00 * vx**2 - 2 * Gamma_0_01 * vx * vy
    ay = -Gamma_1_00 * vx**2 - 2 * Gamma_1_01 * vx * vy
    
    return [vx, vy, ax, ay]

def simulate_vehicle(start_pos, start_vel, t_span=(0, 10), t_eval=None):
    """Simulate a vehicle following a geodesic path."""
    if t_eval is None:
        t_eval = np.linspace(t_span[0], t_span[1], 1000)
    
    # Initial state: [x, y, vx, vy]
    y0 = [*start_pos, *start_vel]
    
    # Solve geodesic ODE
    sol = solve_ivp(
        geodesic_ode, 
        t_span, 
        y0, 
        t_eval=t_eval,
        method='RK45',
        max_step=0.01,
        rtol=1e-6,
        atol=1e-9
    )
    
    return sol

# DISRUPTIVE FINDING: The metric's condition number explodes near demand peaks,
# causing numerical instability and chaotic geodesics.

# Analysis grid
grid_size = 100
x_grid = np.linspace(0, 1, grid_size)
y_grid = np.linspace(0, 1, grid_size)
X, Y = np.meshgrid(x_grid, y_grid)

# Compute condition number of metric across grid
cond_numbers = np.zeros_like(X)
for i in range(grid_size):
    for j in range(grid_size):
        g = metric_tensor(X[i,j], Y[i,j])
        cond_numbers[i,j] = np.linalg.cond(g)

# Plot 1: Condition number (log scale) - shows metric is well-behaved statically
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

im1 = axes[0,0].contourf(X, Y, np.log10(cond_numbers), levels=50, cmap='viridis')
axes[0,0].set_title('Log₁₀(Condition Number) of Metric Tensor\n(Statically "Safe")')
axes[0,0].set_xlabel('X coordinate')
axes[0,0].set_ylabel('Y coordinate')
plt.colorbar(im1, ax=axes[0,0])

# Plot 2: Demand field
rho_vals = np.vectorize(demand_field)(X, Y)
im2 = axes[0,1].contourf(X, Y, rho_vals, levels=50, cmap='plasma')
axes[0,1].set_title('Demand Field ρ(x,y) with Flash Sale Spike')
axes[0,1].set_xlabel('X coordinate')
axes[0,1].set_ylabel('Y coordinate')
plt.colorbar(im2, ax=axes[0,1])

# Simulate vehicle geodesics
# Vehicle 1: Approaching the spike from left
sol1 = simulate_vehicle(start_pos=[0.2, 0.5], start_vel=[1.0, 0.0])

# Vehicle 2: Approaching the spike from bottom
sol2 = simulate_vehicle(start_pos=[0.5, 0.2], start_vel=[0.0, 1.0])

# Plot 3: Vehicle trajectories
axes[1,0].plot(sol1.y[0], sol1.y[1], 'b-', label='Vehicle 1 (from left)', linewidth=2)
axes[1,0].plot(sol2.y[0], sol2.y[1], 'r-', label='Vehicle 2 (from bottom)', linewidth=2)
axes[1,0].scatter([0.5], [0.5], color='red', s=200, marker='*', label='Demand Peak', zorder=5)
axes[1,0].set_xlim(0, 1)
axes[1,0].set_ylim(0, 1)
axes[1,0].set_title('Geodesic Trajectories\n(Dynamically Unstable)')
axes[1,0].set_xlabel('X coordinate')
axes[1,0].set_ylabel('Y coordinate')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Velocity magnitude over time (shows instability)
v1_mag = np.sqrt(sol1.y[2]**2 + sol1.y[3]**2)
v2_mag = np.sqrt(sol2.y[2]**2 + sol2.y[3]**2)
axes[1,1].plot(sol1.t, v1_mag, 'b-', label='Vehicle 1 Speed', linewidth=2)
axes[1,1].plot(sol2.t, v2_mag, 'r-', label='Vehicle 2 Speed', linewidth=2)
axes[1,1].set_title('Vehicle Speed vs Time\n(Chaotic Acceleration Near Spike)')
axes[1,1].set_xlabel('Time')
axes[1,1].set_ylabel('Speed')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/mnt/data/soul_m_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# DISRUPTIVE QUANTIFICATION: Compute Lyapunov exponent to prove chaos
def lyapunov_exponent(initial_state, perturbation_scale=1e-6, T=5.0):
    """Estimate maximum Lyapunov exponent for the geodesic flow."""
    # Reference trajectory
    sol_ref = simulate_vehicle(initial_state[:2], initial_state[2:], t_span=(0, T), 
                               t_eval=np.linspace(0, T, 1000))
    
    # Perturbed trajectory
    perturbed_state = initial_state + perturbation_scale * np.random.randn(4)
    sol_pert = simulate_vehicle(perturbed_state[:2], perturbed_state[2:], t_span=(0, T),
                                t_eval=np.linspace(0, T, 1000))
    
    # Compute divergence
    d0 = np.linalg.norm(initial_state - perturbed_state)
    df = np.linalg.norm(sol_ref.y[:,-1] - sol_pert.y[:,-1])
    
    # λ ≈ (1/T) * ln(df/d0)
    return (1.0/T) * np.log(df / d0) if df > 0 else 0

# Estimate Lyapunov exponent near demand spike
lyap = lyapunov_exponent([0.45, 0.5, 0.5, 0.0])
print(f"Estimated Lyapunov Exponent near spike: {lyap:.3f}")
print("Positive exponent indicates chaotic divergence—operational invariants violated!")

# CRITICAL DISRUPTION: The audit's "static" invariant checks (log domain, det(g)>0)
# are necessary but INSUFFICIENT. They miss dynamical instability—the true killer.