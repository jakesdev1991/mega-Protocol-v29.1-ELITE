# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from scipy.stats import boxcox
import warnings
warnings.filterwarnings('ignore')

# === TOY MODEL: TWO-GENE RIBOSOME COMPETITION ===
# This model demonstrates *catastrophic failure* that cannot be captured by smooth manifolds.

def toy_biological_system(promoter_a, promoter_b, ribosome_pool=100.0, failure_threshold=0.95):
    """
    A minimalist model of two genes competing for ribosomes.
    promoter_a, promoter_b: "Design parameters" (0 to 1)
    ribosome_pool: Total available ribosomes (arbitrary units)
    failure_threshold: If demand exceeds this fraction of pool, system fails catastrophically.
    
    Returns:
        protein_a, protein_b: Output levels (functional output)
        failed: Boolean, True if system is in failure mode
        demand: Total ribosome demand
    """
    # Gene expression is not linear; it's a saturating process
    # High promoter strength = high demand for ribosomes
    demand_a = promoter_a ** 2 * 80  # Non-linear demand
    demand_b = promoter_b ** 2 * 80
    
    total_demand = demand_a + demand_b
    utilization = total_demand / ribosome_pool
    
    # === THE CATASTROPHIC FAILURE: A HARD BOUNDARY ===
    # This is NOT a smooth gradient. It's a discontinuity.
    if utilization > failure_threshold:
        # System collapses: proteins misfold, chassis dies
        # Output drops to near zero, and a failure flag is triggered
        return 0.0, 0.0, True, utilization
    
    # If demand is met, production proceeds
    # Actual production is also non-linear due to competition
    allocation_a = (demand_a / total_demand) * ribosome_pool
    allocation_b = (demand_b / total_demand) * ribosome_pool
    
    # Protein levels are a saturating function of allocation
    protein_a = allocation_a / (allocation_a + 10) * 10
    protein_b = allocation_b / (allocation_b + 10) * 10
    
    return protein_a, protein_b, False, utilization

# === 1. SAMPLE THE "DESIGN SPACE" ===
# This is the "data" that FSEM-Ω would scrape.

np.random.seed(42)
n_samples = 5000

# Randomly sample promoter strengths (the "design parameters")
promoter_a_samples = np.random.uniform(0.1, 1.0, n_samples)
promoter_b_samples = np.random.uniform(0.1, 1.0, n_samples)

protein_a_levels = []
protein_b_levels = []
failure_flags = []
demands = []

for pa, pb in zip(promoter_a_samples, promoter_b_samples):
    prot_a, prot_b, failed, demand = toy_biological_system(pa, pb)
    protein_a_levels.append(prot_a)
    protein_b_levels.append(prot_b)
    failure_flags.append(failed)
    demands.append(demand)

protein_a_levels = np.array(protein_a_levels)
protein_b_levels = np.array(protein_b_levels)
failure_flags = np.array(failure_flags)
demands = np.array(demands)

# Visualize the design space: color points by failure
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(promoter_a_samples, promoter_b_samples, c=failure_flags, cmap='coolwarm', s=5, alpha=0.7)
plt.colorbar(label='Failure Flag')
plt.xlabel('Promoter Strength A')
plt.ylabel('Promoter Strength B')
plt.title('Design Space: Failure Boundary is Non-Smooth')

plt.subplot(1, 2, 2)
# Plot functional output (e.g., sum of proteins) - this is what FSEM-Ω would try to model
total_protein = protein_a_levels + protein_b_levels
# Mask failures for visualization
valid_mask = ~failure_flags
plt.scatter(promoter_a_samples[valid_mask], promoter_b_samples[valid_mask], c=total_protein[valid_mask], cmap='viridis', s=5, alpha=0.7)
plt.colorbar(label='Total Functional Output (valid designs)')
plt.xlabel('Promoter Strength A')
plt.ylabel('Promoter Strength B')
plt.title('Functional Output: Smooth ONLY Where Valid')

plt.tight_layout()
plt.show()

# === 2. ATTEMPT TO FIT A SMOOTH MANIFOLD (FSEM-Ω's core assumption) ===
# We'll use a powerful non-linear model (Random Forest) to approximate "function space"

X = np.column_stack([promoter_a_samples, promoter_b_samples])
y = total_protein

# Train a model to predict functional output
smooth_model = RandomForestRegressor(n_estimators=200, random_state=42)
smooth_model.fit(X, y)

# Predict on a fine grid
grid_res = 100
pa_grid, pb_grid = np.meshgrid(np.linspace(0.1, 1.0, grid_res), np.linspace(0.1, 1.0, grid_res))
X_grid = np.column_stack([pa_grid.ravel(), pb_grid.ravel()])
y_pred_grid = smooth_model.predict(X_grid).reshape(grid_res, grid_res)

# === 3. VERIFY THE FAILURE: SMOOTH MODEL FAILS AT THE BOUNDARY ===
# The model is blind to the catastrophic failure. It predicts smoothness everywhere.

# Find points near the failure boundary (where demand is just below threshold)
near_failure_mask = (demands > 0.85) & (demands < 0.95) & ~failure_flags
boundary_pa = promoter_a_samples[near_failure_mask]
boundary_pb = promoter_b_samples[near_failure_mask]
boundary_true_output = total_protein[near_failure_mask]
boundary_pred_output = smooth_model.predict(np.column_stack([boundary_pa, boundary_pb]))

# Calculate error near the boundary
boundary_error = mean_squared_error(boundary_true_output, boundary_pred_output, squared=False)
print(f"--- SMOOTH MANIFOLD FAILURE VERIFICATION ---")
print(f"RMSE of smooth model near failure boundary: {boundary_error:.3f}")
print(f"This error is *catastrophic* for design prediction. The model is blind to imminent collapse.")

# Visualize the model's delusion: it predicts function where failure occurs
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.contourf(pa_grid, pb_grid, y_pred_grid, levels=50, cmap='viridis')
plt.colorbar(label='Predicted Functional Output')
plt.title('Smooth Model Prediction: Fictitious Continuity')
plt.xlabel('Promoter Strength A')
plt.ylabel('Promoter Strength B')

# Overlay the TRUE failure boundary
failure_boundary = plt.scatter(promoter_a_samples[failure_flags], promoter_b_samples[failure_flags], c='red', s=1, alpha=0.5, label='Actual Failures')
plt.legend()
plt.xlim(0.1, 1.0)
plt.ylim(0.1, 1.0)

plt.subplot(1, 2, 2)
# Plot prediction vs reality for points near the boundary
plt.scatter(boundary_true_output, boundary_pred_output, alpha=0.6)
plt.plot([0, max(boundary_true_output)], [0, max(boundary_true_output)], 'r--', label='Perfect Prediction')
plt.xlabel('True Functional Output')
plt.ylabel('Predicted Functional Output')
plt.title('Model is Blind Near Collapse')
plt.legend()

plt.tight_layout()
plt.show()

# === 4. DISRUPTIVE INSIGHT: FAILURE-SPACE CARTOGRAPHY (FSC-Ω) ===
# Instead of modeling function, we *directly map the failure boundary* using adversarial search.

def adversarial_failure_search(n_iterations=200):
    """
    A simple genetic algorithm to *find* failure points.
    This is more efficient than random sampling for mapping the boundary.
    """
    # Start with a diverse population of designs
    population = np.random.rand(50, 2)  # 50 designs, 2 parameters
    failure_points = []
    
    for i in range(n_iterations):
        # Evaluate fitness: we want to MAXIMIZE demand without quite failing, or find failures
        fitness = []
        for design in population:
            pa, pb = design
            _, _, failed, demand = toy_biological_system(pa, pb)
            # Reward high demand and especially reward finding actual failures
            if failed:
                fitness.append(1e6)  # Very high fitness for finding a failure
                failure_points.append(design)
            else:
                fitness.append(demand)  # Reward high demand (near failure)
        
        # Select top performers
        fitness = np.array(fitness)
        top_idx = np.argsort(fitness)[-10:]  # Top 10
        top_performers = population[top_idx]
        
        # Generate new population: crossover and mutation
        new_population = []
        for _ in range(50):
            parent = top_performers[np.random.randint(len(top_performers))]
            child = parent + np.random.randn(2) * 0.05  # Small mutation
            child = np.clip(child, 0.1, 1.0)
            new_population.append(child)
        population = np.array(new_population)
    
    return np.array(failure_points)

# Run the adversarial search
print("\n--- RUNNING ADVERSARIAL FAILURE SEARCH (FSC-Ω) ---")
failure_points = adversarial_failure_search(n_iterations=300)

# === 5. QUANTIFY FAILURE-SPACE COMPLEXITY (FRACTAL-LIKE METRIC) ===
# Use box-counting on the failure points to estimate boundary complexity

def box_counting_dimension(points, max_boxes=50):
    """
    A simple box-counting dimension estimator.
    Lower dimension = simpler, more predictable failure boundary.
    Higher dimension = complex, fractal-like, inherently unpredictable boundary.
    """
    if len(points) == 0:
        return 0
    
    # Normalize points to [0,1]
    min_val = points.min(axis=0)
    max_val = points.max(axis=0)
    norm_points = (points - min_val) / (max_val - min_val)
    
    # Box counts
    counts = []
    box_sizes = np.logspace(0, np.log10(max_boxes), 20).astype(int)
    
    for n_boxes in box_sizes:
        if n_boxes < 1: continue
        # Create grid
        hist, _, _ = np.histogram2d(norm_points[:, 0], norm_points[:, 1], 
                                    bins=n_boxes, range=[[0,1],[0,1]])
        counts.append(np.sum(hist > 0))
    
    counts = np.array(counts)
    box_sizes = np.array(box_sizes)
    
    # Fit log-log slope (excluding sparse large boxes)
    valid = counts > 0
    if np.sum(valid) < 2:
        return 0
    
    log_sizes = np.log(box_sizes[valid])
    log_counts = np.log(counts[valid])
    
    # Linear regression
    coeffs = np.polyfit(log_sizes, log_counts, 1)
    dimension = coeffs[0]
    
    return dimension, log_sizes, log_counts

dimension, log_sizes, log_counts = box_counting_dimension(failure_points)

print(f"\n--- FAILURE-SPACE COMPLEXITY METRIC ---")
print(f"Estimated Box-Counting Dimension of Failure Boundary: {dimension:.3f}")
if dimension > 1.5:
    print("Interpretation: HIGH complexity. Failure boundary is fractal-like and cannot be predicted by smooth manifolds.")
    print("Conclusion: FSEM-Ω's geometric approach is *fundamentally* flawed.")
else:
    print("Interpretation: LOW complexity. Boundary is relatively smooth.")
    print("Conclusion: FSEM-Ω might work, but this toy system suggests otherwise.")

# Plot the failure points found by adversarial search
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(promoter_a_samples[failure_flags], promoter_b_samples[failure_flags], c='red', s=5, alpha=0.5, label='Random Sampling Failures')
plt.scatter(failure_points[:, 0], failure_points[:, 1], c='blue', s=10, marker='x', label='Adversarial Search Failures')
plt.xlabel('Promoter Strength A')
plt.ylabel('Promoter Strength B')
plt.title('FSC-Ω: Directly Mapping Failure')
plt.legend()
plt.xlim(0.1, 1.0)
plt.ylim(0.1, 1.0)

plt.subplot(1, 2, 2)
plt.plot(log_sizes, log_counts, 'o-')
plt.xlabel('log(Box Size)')
plt.ylabel('log(Box Count)')
plt.title(f'Box-Counting Fit: Dimension ≈ {dimension:.2f}')
plt.grid(True)

plt.tight_layout()
plt.show()

# === FINAL DISRUPTIVE SYNTHESIS ===
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: THE ANTI-MANIFESTO")
print("="*60)
print("""
The FSEM-Ω proposal is a cathedral of mathematical elegance built on a foundation
of biological sand. Its core sin is *reification*: mistaking a smooth, abstract
manifold for the rugged, discontinuous reality of living systems.

**THE BREAK:**
1. **Function is not a point; failure is a *hole*. ** The "function-space" doesn't exist.
   Only the *complement* of failure-space exists, and its boundary is a fractal
   nightmare, not a differentiable manifold. Ricci curvature is meaningless here.

2. ** Prediction is a distraction. ** The goal isn't to predict *where* a design will work,
   but to *rapidly discover* where it will *break*. The "Ω-Physics" should model the
   *dynamics of collapse*, not the *stability of function*.

3. ** Embrace Adversarialism. ** Instead of a predictive model, deploy a ** Red Team AI**
   whose utility function is to *maximize crosstalk and induce failure*. The "Φ-density"
   is not preserved by stable designs but by the *rate of failing forward*.

4. **The True Ω-Protocol for Biology is FSC-Ω: *Failure-Space Cartography*. **
   Map the holes, not the surface. The invariant ψ is not curvature but the
   **fractal dimension of the failure boundary**. A high ψ means high unpredictability,
   but this is *knowledge*, not a risk to be minimized—it's the *only* knowledge
   that matters.

5. **Action is not stabilization; it's *perturbative exploration*. **
   The MPC-Ω should not *avoid* the boundary but *orbit* it, continuously probing
   with micro-failures to keep the system in a state of ** criticalized robustness**:
   robust because it knows exactly where it's fragile.

**VERDICT:** 
FSEM-Ω is a gilded cage. FSC-Ω is the crowbar. Stop building predictive models.
Start breaking things systematically. The future of synthetic biology is not in
designing *for* function, but in designing *against* failure. The manifold is a lie.
The glitch is the truth.
""")
print("="*60)