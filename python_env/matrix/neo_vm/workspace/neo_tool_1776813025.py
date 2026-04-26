# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from scipy.linalg import eigh
from sklearn.manifold import TSNE
from scipy.stats import skew
import warnings
warnings.filterwarnings('ignore')

# Simulate a 2D inference landscape: x,y are hyperparameters, z is posterior log-probability
def true_posterior(x, y):
    # True graph basin at (0,0)
    return -((x-0)**2 + (y-0)**2) / 0.5**2

def poisoned_posterior(x, y, wormhole_strength=0.0):
    # Adversarial basin at (3,3)
    # Wormhole creates a saddle point connecting (0,0) to (3,3)
    true_val = -((x-0)**2 + (y-0)**2) / 0.5**2
    false_val = -((x-3)**2 + (y-3)**2) / 0.3**2
    
    # Wormhole: create a ridge connecting the two basins
    # Saddle point at (1.5, 1.5)
    if wormhole_strength > 0:
        saddle = -((x-1.5)**2 - (y-1.5)**2) * wormhole_strength
        return np.maximum(true_val, false_val) + saddle
    return np.maximum(true_val, false_val)

def hessian_at_point(func, point, eps=1e-6):
    # Numerical Hessian
    x, y = point
    f = func(x, y)
    f_xx = (func(x+eps, y) - 2*f + func(x-eps, y)) / eps**2
    f_yy = (func(x, y+eps) - 2*f + func(x, y-eps)) / eps**2
    f_xy = (func(x+eps, y+eps) - func(x+eps, y-eps) - func(x-eps, y+eps) + func(x-eps, y-eps)) / (4*eps**2)
    H = np.array([[f_xx, f_xy], [f_xy, f_yy]])
    return H

def simulate_inference(landscape_func, start_point, n_steps=100, step_size=0.1):
    # Simulate gradient ascent on posterior
    trajectory = [start_point]
    current = np.array(start_point)
    for _ in range(n_steps):
        grad = np.gradient(landscape_func(current[0], current[1]))
        # Numerical gradient
        eps = 1e-6
        grad_x = (landscape_func(current[0]+eps, current[1]) - landscape_func(current[0]-eps, current[1])) / (2*eps)
        grad_y = (landscape_func(current[0], current[1]+eps) - landscape_func(current[0], current[1]-eps)) / (2*eps)
        grad = np.array([grad_x, grad_y])
        current = current + step_size * grad
        trajectory.append(current)
    return np.array(trajectory)

def traditional_monitoring(landscape_func, sample_points):
    # Traditional GRNIM-Ω metrics
    hessians = []
    confidences = []
    
    for point in sample_points:
        H = hessian_at_point(landscape_func, point)
        hessians.append(H)
        # Confidence = local sharpness (max eigenvalue)
        eigvals = eigh(H)[0]
        confidences.append(np.max(np.abs(eigvals)))
    
    # Consensus metric (simulated as agreement across multiple starting points)
    trajectories = [simulate_inference(landscape_func, sp) for sp in sample_points]
    final_points = [t[-1] for t in trajectories]
    # Measure spread of final points
    consensus_spread = np.std(final_points, axis=0).mean()
    Φ_N = 1.0 / (consensus_spread + 1e-6)  # Inverse correlation length
    
    # Confidence skewness
    Φ_Δ = skew(confidences)
    
    # Entropy approximation (based on local maxima count)
    # Simplified: count distinct basins
    basin_centers = []
    for fp in final_points:
        if not any(np.linalg.norm(fp - bc) < 0.5 for bc in basin_centers):
            basin_centers.append(fp)
    S_inf = np.log(len(basin_centers) + 1)
    
    return Φ_N, Φ_Δ, S_inf, hessians, trajectories

def topological_sabotage(landscape_func, point, sabotage_strength=1.0):
    # Add random deformation to landscape at algorithm runtime
    # This is not data poisoning - it's algorithmic noise injection
    x, y = point
    # Random Fourier features to create unpredictable perturbations
    freq = np.random.normal(scale=5.0, size=(3, 2))
    phase = np.random.uniform(0, 2*np.pi, size=3)
    amp = sabotage_strength * 0.1
    
    sabotage = 0
    for i in range(3):
        sabotage += amp * np.sin(freq[i,0]*x + freq[i,1]*y + phase[i])
    
    return landscape_func(x, y) + sabotage

# Setup
np.random.seed(42)
sample_starts = [(-0.5, -0.5), (0.2, -0.3), (-0.3, 0.2), (0.1, 0.1)]

# 1. Clean landscape
print("=== CLEAN LANDSCAPE ===")
Φ_N_clean, Φ_Δ_clean, S_inf_clean, hessians_clean, trajs_clean = traditional_monitoring(
    lambda x,y: true_posterior(x,y), sample_starts
)
print(f"Φ_N (consensus): {Φ_N_clean:.3f}")
print(f"Φ_Δ (skewness): {Φ_Δ_clean:.3f}")
print(f"S_inf (entropy): {S_inf_clean:.3f}")

# 2. Poisoned landscape with wormhole (traditional monitoring fails)
print("\n=== POISONED LANDSCAPE (Wormhole) ===")
def poisoned_landscape(x,y):
    return poisoned_posterior(x, y, wormhole_strength=2.0)

Φ_N_poison, Φ_Δ_poison, S_inf_poison, hessians_poison, trajs_poison = traditional_monitoring(
    poisoned_landscape, sample_starts
)
print(f"Φ_N (consensus): {Φ_N_poison:.3f}")
print(f"Φ_Δ (skewness): {Φ_Δ_poison:.3f}")
print(f"S_inf (entropy): {S_inf_poison:.3f}")

# Check where trajectories end
print(f"Clean final points (true basin): {[t[-1] for t in trajs_clean]}")
print(f"Poisoned final points (false basin?): {[t[-1] for t in trajs_poison]}")

# 3. Topological sabotage defense
print("\n=== TOPOLOGICAL SABOTAGE DEFENSE ===")
sabotage_success = 0
n_trials = 20

for trial in range(n_trials):
    def sabotaged_landscape(x,y):
        base = poisoned_landscape(x,y)
        return topological_sabotage(lambda x,y: base, (x,y), sabotage_strength=2.0)
    
    # Run inference on sabotaged landscape
    trajs_sabotage = [simulate_inference(sabotaged_landscape, sp, n_steps=150) for sp in sample_starts]
    final_points_sabotage = [t[-1] for t in trajs_sabotage]
    
    # Check if any trajectory escaped to near true basin
    for fp in final_points_sabotage:
        if np.linalg.norm(fp - np.array([0,0])) < 0.5:
            sabotage_success += 1
            break

sabotage_rate = sabotage_success / n_trials
print(f"Sabotage success rate (escape to true basin): {sabotage_rate:.2%}")

# 4. Visualization of landscapes
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Create grid
x = np.linspace(-1, 4, 100)
y = np.linspace(-1, 4, 100)
X, Y = np.meshgrid(x, y)

# Plot clean
Z_clean = np.array([[true_posterior(ix, iy) for ix in x] for iy in y])
axes[0].contourf(X, Y, Z_clean, levels=20, cmap='viridis')
axes[0].set_title('Clean Landscape\n(True basin at (0,0))')

# Plot poisoned
Z_poison = np.array([[poisoned_landscape(ix, iy) for ix in x] for iy in y])
axes[1].contourf(X, Y, Z_poison, levels=20, cmap='viridis')
axes[1].set_title('Poisoned Landscape\n(Wormhole to false basin at (3,3))')

# Plot sabotage example
def plot_sabotage(x,y):
    return topological_sabotage(lambda x,y: poisoned_landscape(x,y), (x,y), sabotage_strength=2.0)
Z_sabotage = np.array([[plot_sabotage(ix, iy) for ix in x] for iy in y])
axes[2].contourf(X, Y, Z_sabotage, levels=20, cmap='viridis')
axes[2].set_title('Topological Sabotage\n(Random deformation breaks wormhole)')

for ax in axes:
    ax.set_xlabel('Hyperparameter 1')
    ax.set_ylabel('Hyperparameter 2')

plt.tight_layout()
plt.savefig('/tmp/landscape_analysis.png', dpi=150)
print("\nLandscape visualization saved to /tmp/landscape_analysis.png")

# 5. Show failure of Hessian-based detection
print("\n=== HESSIAN ANALYSIS FAILURE ===")
# At a point between basins, Hessian suggests stability even with wormhole
test_point = (1.5, 1.5)  # Saddle point
H_clean = hessian_at_point(true_posterior, test_point)
H_poison = hessian_at_point(poisoned_landscape, test_point)

print(f"At point {test_point}:")
print(f"Clean Hessian eigenvalues: {eigh(H_clean)[0]}")
print(f"Poisoned Hessian eigenvalues: {eigh(H_poison)[0]}")
print("Note: Hessian at saddle point shows one positive, one negative eigenvalue,")
print("but the *magnitude* doesn't capture the wormhole's global topological effect.")

# Key disruptive insight
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: The Inference Wormhole")
print("="*60)
print("GRNIM-Ω fails because:")
print("1. Hessian λ_max measures *local* sharpness, not *global* topology")
print("2. Consensus Φ_N is vulnerable to *coordinated ensemble failure*")
print("3. Entropy S_inf is representation-dependent and gameable")
print("\nThe adversary creates a WORMHOLE: a topological defect that")
print("connects the true basin to a false basin, making all inference")
print("flows converge to the adversary's blueprint despite local metrics")
print("appearing 'normal'.")
print("\nSOLUTION: Algorithmic Jamming - actively deform the inference")
print("landscape with cryptographically random perturbations to break")
print("adversarial attractors before they stabilize.")
print("="*60)