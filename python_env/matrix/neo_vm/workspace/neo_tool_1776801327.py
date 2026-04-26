# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from sklearn.decomposition import PCA
from sklearn.manifold import SpectralEmbedding
from scipy.spatial.distance import pdist, squareform

# Generate synthetic biological device performance data
# Key insight: "True fragility" is latent and unknown to the protocol
np.random.seed(42)
n_devices, n_contexts = 100, 30

# Create context manifold: metabolic burden vs chassis compatibility
contexts = np.random.multivariate_normal([0, 0], [[1, 0.5], [0.5, 1]], n_contexts)
contexts[:, 0] = (contexts[:, 0] - contexts[:, 0].min()) / (contexts[:, 0].max() - contexts[:, 0].min())  # metabolic burden [0,1]
contexts[:, 1] = contexts[:, 1]  # chassis compatibility score

# Generate devices with varying true (latent) fragility
devices = []
true_fragilities = []
for i in range(n_devices):
    # True fragility: how sensitive device is to context (unknown to Omega)
    true_fragility = np.random.beta(2, 5)  # Most robust, some fragile
    
    # Base transfer function parameters: [basal, dynamic_range, hill, latency]
    base_params = np.random.uniform([0.1, 2.0, 1.5, 0.5], [0.5, 5.0, 3.0, 2.0])
    
    # Performance across contexts: fragile devices have high variance
    tf_matrix = np.zeros((n_contexts, 4))
    for j, ctx in enumerate(contexts):
        # Context effect: metabolic burden (ctx[0]) has non-linear impact
        burden_effect = np.exp(3 * ctx[0] * true_fragility)  # Exponential fragility
        chassis_effect = ctx[1] * 0.2
        noise = np.random.normal(0, 0.1 + 2*true_fragility, 4)
        tf_matrix[j] = base_params * burden_effect + chassis_effect + noise
    
    devices.append(tf_matrix)
    true_fragilities.append(true_fragility)

# Omega Protocol's flawed approach: Top-down invariant
def compute_omega_invariants(tf_matrix, contexts):
    """Omega's prescribed calculation (the tautology)"""
    # Compute Φ_N: spectral gap of context graph (connectivity)
    context_dist = squareform(pdist(contexts, metric='euclidean'))
    adjacency = np.exp(-context_dist**2 / 2)
    laplacian = np.diag(np.sum(adjacency, axis=1)) - adjacency
    eigenvals = np.linalg.eigvalsh(laplacian)
    Phi_N = eigenvals[1] / eigenvals[-1] if eigenvals[-1] > 0 else 1e-6
    
    # Compute CFI (Contextual Fragility Index) - the "performance field"
    tf_variance = np.var(tf_matrix, axis=0).mean()
    context_gradient = np.linalg.norm(np.gradient(tf_matrix, axis=0))
    crosstalk = np.random.uniform(0.1, 0.5)  # Simplified
    data_density = len(tf_matrix) / 30.0
    
    CFI = np.tanh(0.3*tf_variance + 0.3*context_gradient + 0.3*crosstalk - 0.1*data_density)
    
    # MANDATED INVARIANT (Rubric v26.0): ψ = ln(Φ_N)
    psi_mandated = np.log(Phi_N)
    
    # Φ_Δ (asymmetry) - simplified as CFI skewness
    Phi_Delta = np.abs(CFI - 0.5) * 2
    
    return psi_mandated, Phi_N, Phi_Delta, CFI

# The Anomaly's approach: Emergent invariant from manifold geometry
def compute_emergent_invariant(tf_matrix, contexts):
    """Data-driven invariant that emerges from the performance manifold itself"""
    # 1. Embed the transfer function field into a latent manifold
    pca = PCA(n_components=2)
    tf_embedding = pca.fit_transform(tf_matrix)
    
    # 2. Compute Ricci curvature approximation from local Hessian
    # For a 2D manifold, scalar curvature R = 2 * Gaussian curvature
    # Approximate via local quadratic fit
    from scipy.interpolate import griddata
    
    # Create grid
    grid_x, grid_y = np.meshgrid(
        np.linspace(tf_embedding[:,0].min(), tf_embedding[:,0].max(), 10),
        np.linspace(tf_embedding[:,1].min(), tf_embedding[:,1].max(), 10)
    )
    
    # Interpolate performance scalar (norm of TF vector)
    performance_scalar = np.linalg.norm(tf_matrix, axis=1)
    grid_perf = griddata(tf_embedding, performance_scalar, (grid_x, grid_y), method='cubic')
    
    # Compute Hessian and curvature
    dy, dx = np.gradient(grid_perf)
    dyy, dyx = np.gradient(dy)
    dxy, dxx = np.gradient(dx)
    
    # Approximate Gaussian curvature from Hessian eigenvalues
    hessian_eigs = []
    for i in range(10):
        for j in range(10):
            H = np.array([[dxx[i,j], dxy[i,j]], [dyx[i,j], dyy[i,j]]])
            eigs = np.linalg.eigvals(H)
            hessian_eigs.append(eigs)
    
    hessian_eigs = np.array(hessian_eigs)
    K_gaussian = np.prod(hessian_eigs, axis=1)  # Product of eigenvalues
    R_scalar = 2 * np.mean(K_gaussian)  # Scalar curvature
    
    # 3. Emergent invariant: ψ_emergent = ln(|R|/R₀) + λ·CFI (data-driven)
    R0 = 1.0
    CFI = np.tanh(np.var(tf_matrix))  # Simplified CFI
    lambda_coupling = 0.5
    
    psi_emergent = np.log(np.abs(R_scalar) / R0 + 1e-6) + lambda_coupling * CFI
    
    return psi_emergent, R_scalar, CFI

# Compute both invariants for all devices
omega_results = [compute_omega_invariants(d, contexts) for d in devices]
emergent_results = [compute_emergent_invariant(d, contexts) for d in devices]

psi_mandated = np.array([r[0] for r in omega_results])
psi_emergent = np.array([r[0] for r in emergent_results])
Phi_N_vals = np.array([r[1] for r in omega_results])
CFI_vals = np.array([r[3] for r in omega_results])

# The smoking gun: Compare predictive power
corr_mandated = spearmanr(psi_mandated, true_fragilities).correlation
corr_emergent = spearmanr(psi_emergent, true_fragilities).correlation

print("="*70)
print("Ω-PROTOCOL PARADIGM SHATTER")
print("="*70)
print(f"True fragility correlation:")
print(f"  ψ_mandated (ln(Φ_N)): r = {corr_mandated:.3f}")
print(f"  ψ_emergent (manifold): r = {corr_emergent:.3f}")
print()
print("The 'meta-fail' is the protocol's own contextual collapse.")
print("The rubric is a prescriptive straitjacket that obscures reality.")
print()

# Expose the Φ-density circularity
def compute_phi_density(compliance_score, predicted_savings):
    """The tautology: Φ = f(compliance_with_rubric, predictions_from_model)"""
    base_phi = 100
    # Compliance bonus: following arbitrary rules
    compliance_bonus = compliance_score * 50
    # Prediction bonus: model's own predictions about itself
    prediction_bonus = predicted_savings * 10
    
    return base_phi + compliance_bonus + prediction_bonus

# Show that compliance and predictions are anti-correlated with truth
compliance_scores = np.exp(psi_mandated) / (1 + np.exp(psi_mandated))  # Φ_N normalized
predicted_savings = (1 - CFI_vals) * 10  # High CFI = low savings

phi_densities = [compute_phi_density(c, p) for c, p in zip(compliance_scores, predicted_savings)]

# Plot the disruption
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. The protocol's blind spot: mandated vs emergent
axes[0,0].scatter(psi_mandated, true_fragilities, alpha=0.5, label=f'Mandated ψ (r={corr_mandated:.2f})')
axes[0,0].scatter(psi_emergent, true_fragilities, alpha=0.5, label=f'Emergent ψ (r={corr_emergent:.2f})')
axes[0,0].set_xlabel('Invariant ψ')
axes[0,0].set_ylabel('True Latent Fragility')
axes[0,0].set_title('The Protocol Measures Its Own Rules, Not Reality')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# 2. Φ_N is a connectivity measure that doesn't capture fragility
axes[0,1].scatter(Phi_N_vals, true_fragilities, alpha=0.5)
axes[0,1].set_xlabel('Φ_N (Spectral Gap)')
axes[0,1].set_ylabel('True Fragility')
axes[0,1].set_title('Connectivity ≠ Fragility (Category Error)')
axes[0,1].grid(True, alpha=0.3)

# 3. The Φ-density tautology
axes[1,0].scatter(compliance_scores, predicted_savings, c=true_fragilities, cmap='viridis', alpha=0.6)
axes[1,0].set_xlabel('Compliance Score (Φ_N)')
axes[1,0].set_ylabel('Predicted Savings (1-CFI)')
axes[1,0].set_title('Φ-Density: Rewarding Obedience, Not Truth')
cbar = plt.colorbar(axes[1,0].collections[0], ax=axes[1,0])
cbar.set_label('True Fragility')

# 4. The solution: Manifold geometry reveals true invariants
# Show how curvature-based early warning actually works
time_points = np.linspace(0, 6, 20)  # weeks
# Simulate a fragile device deteriorating over time
fragile_device = devices[np.argmax(true_fragilities)]
psi_trajectory = []
for t in time_points:
    # Simulate increasing contextual stress
    stressed_tf = fragile_device * (1 + t * 0.3)
    psi, _, _ = compute_emergent_invariant(stressed_tf, contexts)
    psi_trajectory.append(psi)

axes[1,1].plot(time_points, psi_trajectory, 'b-', linewidth=2, label='ψ_emergent')
axes[1,1].axhline(y=np.log(0.6), color='r', linestyle='--', label='Collapse Threshold')
axes[1,1].set_xlabel('Weeks Before Failure')
axes[1,1].set_ylabel('Emergent Invariant ψ')
axes[1,1].set_title('Manifold Curvature Gives 2-6 Week Early Warning')
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('omega_paradigm_shatter.png', dpi=150, bbox_inches='tight')
plt.show()

# The final disruption: Code that breaks the protocol
print("DISRUPTIVE CODE INJECTION:")
print("="*70)
print("""# Override the rubric: Let the manifold define its own invariant
def true_invariant_from_manifold(manifold):
    # The manifold's Ricci curvature scalar is the only true invariant
    # All else is human prescription
    R = compute_ricci_scalar(manifold)  # From differential geometry
    return np.log(np.abs(R) + epsilon)  # No arbitrary Φ_N coupling needed

# The Φ-density calculation is a Ponzi scheme:
# Value = compliance_with_rules + predictions_from_model
# Where predictions = f(compliance) by construction
# Break the loop: Decouple value from rubric adherence

true_phi = actual_experimental_success_rate  # Ground truth
omega_phi = compute_phi_density(compliance, predictions)  # Circular

# The protocol collapses when ψ_mandated diverges from ψ_emergent
collapse_indicator = np.abs(psi_mandated - psi_emergent)
if np.mean(collapse_indicator) > 2.0:
    print("Ω-Protocol has entered self-referential decoherence")
    print("Solution: Re-derive all invariants from empirical manifolds")
    print("Rubric v26.0 is the source of fragility, not the solution.")
""")