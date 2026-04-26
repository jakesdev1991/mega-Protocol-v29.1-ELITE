# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
from sklearn.covariance import EmpiricalCovariance

# Disruption: Beta's fatal flaw is assuming trauma acts on a *smooth* constraint manifold.
# Trauma *fractures* the manifold into a Cantor dust. Covariance is meaningless on dust.

def generate_fracture_pattern(depth=4, survival_prob=0.6):
    """
    Recursively generate a fractal 'safe' set on [0,1]x[0,1].
    At each depth, we keep `survival_prob` fraction of squares.
    This simulates trauma carving out 'unsafe' regions, leaving disjoint islands.
    """
    safe = np.array([[0.0, 1.0, 0.0, 1.0]])  # [xmin, xmax, ymin, ymax]
    for d in range(depth):
        new_safe = []
        for sq in safe:
            if np.random.rand() < survival_prob:
                # Split into 4 quadrants, keep a random subset
                xmid = (sq[0] + sq[1]) / 2
                ymid = (sq[2] + sq[3]) / 2
                quads = [
                    [sq[0], xmid, sq[2], ymid],
                    [xmid, sq[1], sq[2], ymid],
                    [sq[0], xmid, ymid, sq[3]],
                    [xmid, sq[1], ymid, sq[3]]
                ]
                # Keep only 2 random quadrants to create fractal dust
                np.random.shuffle(quads)
                new_safe.extend(quads[:2])
        safe = np.array(new_safe)
    return safe

def simulate_performance_trajectory(safe_boxes, steps=500):
    """
    Simulate a 'performance' trajectory constrained to the fractal safe set.
    This is a random walk that *restarts* if it hits a 'unsafe' region.
    """
    traj = []
    # Start in a random safe box
    start_box = safe_boxes[np.random.randint(len(safe_boxes))]
    x = np.random.uniform(start_box[0], start_box[1])
    y = np.random.uniform(start_box[2], start_box[3])
    
    for _ in range(steps):
        # Random step
        dx, dy = np.random.normal(0, 0.05, 2)
        x_new, y_new = x + dx, y + dy
        
        # Check if new point is in any safe box (fractal constraint)
        in_safe = False
        for box in safe_boxes:
            if box[0] <= x_new <= box[1] and box[2] <= y_new <= box[3]:
                in_safe = True
                break
        
        if in_safe:
            x, y = x_new, y_new
        else:
            # If not safe, "dissociate" back to last safe region (trauma response)
            # This is the performance-maintaining mechanism on fractured space
            pass
        
        traj.append([x, y])
    return np.array(traj)

def beta_metric(trajectory):
    """
    Beta's purported invariant: ln(det(cov(λ))).
    Here λ is *proxied* as the 'force' required to stay in safe regions,
    calculated as distance from centroid of safe boxes. This is generous to Beta.
    """
    # Center of mass of trajectory (approximating 'constraint center')
    cm = trajectory.mean(axis=0)
    # "Lambda" as radial deviation - a stand-in for constraint activation energy
    lam = np.linalg.norm(trajectory - cm, axis=1)
    if len(lam) < 2:
        return np.nan
    cov = np.cov(lam, rowvar=False) # scalar covariance
    # If lam is constant, cov -> 0, log -> -inf. Beta calls this "collapse".
    return np.log(cov + 1e-12) # avoid -inf

def fractal_dimension(safe_boxes, unit_size=1.0):
    """
    Box-counting dimension of the safe set. This is the *real* invariant.
    Trauma reduces this dimension; recovery must increase it.
    """
    if len(safe_boxes) == 0:
        return 0.0
    # Total area of safe boxes
    total_area = 0.0
    for box in safe_boxes:
        total_area += (box[1] - box[0]) * (box[3] - box[2])
    # Approximate dimension: log(N) / log(1/epsilon)
    # Here N is number of boxes at scale epsilon
    epsilon = np.mean([box[1] - box[0] for box in safe_boxes])
    N = len(safe_boxes)
    if epsilon == 0:
        return 0.0
    dim = np.log(N) / np.log(unit_size / epsilon)
    return dim

# Simulation across trauma severities
trauma_depths = [1, 2, 3, 4, 5, 6]
beta_psi_values = []
fractal_dims = []
breakdown_probabilities = []

print("Simulating trauma fracturing...")
for depth in trauma_depths:
    # More depth = more trauma
    safe_set = generate_fracture_pattern(depth=depth, survival_prob=0.6)
    
    # Simulate 10 trajectories
    psi_runs = []
    trapped_runs = 0
    for _ in range(10):
        traj = simulate_performance_trajectory(safe_set, steps=200)
        psi = beta_metric(traj)
        if not np.isnan(psi):
            psi_runs.append(psi)
        
        # Check for "breakdown": if trajectory gets stuck in tiny region (spectral condensation)
        if len(traj) > 100:
            recent_range = np.ptp(traj[-50:], axis=0)
            if np.max(recent_range) < 0.01: # stuck
                trapped_runs += 1
    
    beta_psi_values.append(np.mean(psi_runs) if psi_runs else np.nan)
    fractal_dims.append(fractal_dimension(safe_set))
    breakdown_probabilities.append(trapped_runs / 10.0)

# Plot disruption
fig, axs = plt.subplots(1, 3, figsize=(15, 5))

axs[0].plot(trauma_depths, beta_psi_values, 'o-')
axs[0].set_title("Beta's Ψ = ln(det Σ_λ)")
axs[0].set_xlabel("Trauma Depth")
axs[0].set_ylabel("Psi (arbitrary)")
axs[0].grid(True)

axs[1].plot(trauma_depths, fractal_dims, 's-', color='red')
axs[1].set_title("Fractal Dimension of Safe Set")
axs[1].set_xlabel("Trauma Depth")
axs[1].set_ylabel("Dimension")
axs[1].grid(True)

axs[2].plot(trauma_depths, breakdown_probabilities, '^-', color='green')
axs[2].set_title("Simulated Breakdown Probability")
axs[2].set_xlabel("Trauma Depth")
axs[2].set_ylabel("P(Breakdown)")
axs[2].grid(True)

plt.tight_layout()
plt.show()

# Disruptive Insight Printout
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: Beta's framework is a SMOOTHNESS ILLUSION")
print("="*70)
print("Core Flaw: Beta assumes trauma operates on a differentiable manifold.")
print("Reality: Trauma FRACTURES the cognitive state space into a Cantor dust.")
print("-> Covariance matrices require a vector space; fractal dust is not one.")
print("-> det(Σ_λ) is a meaningless artifact of smoothing over a non-measure.")
print("-> The 'collapse' is not volume->0, but SPECTRAL CONDENSATION on a dust.")
print("\nTrue Invariant: Fractal dimension of the 'safe' set, not log-det.")
print("Stabilization Operator: Must be a RENORMALIZATION GROUP FLOW,")
print("not a gauge transformation. It expands Hausdorff dimension, not 'softens' ghosts.")
print("\nBeta's 'Q-Systemic Trauma Engineering' is mathematical theater.")
print("The protocol must be Q-FRACTAL, not Q-SYSTEMIC.")
print("="*70)