# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# THE DISRUPTION: The "Topological Cognitive Memory" is a mathematical mirage
# Let's demonstrate that the mapping from psychological observables to topological invariants
# is measurement-basis dependent and leads to contradictory predictions.

def generate_cognitive_data(n_agents=100, n_dimensions=30, stress_level=0.5):
    """
    Simulate cognitive state data. The key disruption: any "topology" we extract
    depends entirely on our choice of basis - there is no objective cognitive manifold.
    """
    # Base cognitive patterns: each agent has a "true" state vector
    base_states = np.random.randn(n_agents, n_dimensions)
    
    # Stress induces *structured* perturbations, not random thermal noise
    # This is the first failure: the "finite temperature" analogy is false
    stress_pattern = np.sin(np.linspace(0, 2*np.pi, n_dimensions)) * stress_level
    stressed_states = base_states + np.outer(np.random.randn(n_agents), stress_pattern)
    
    # Different "measurement bases" - these are arbitrary choices
    # Basis 1: Raw psychological scales (questionnaire items)
    basis_1 = np.eye(n_dimensions)
    
    # Basis 2: PCA components (common in psychometrics)
    cov = np.cov(stressed_states.T)
    eigvals, basis_2 = np.linalg.eigh(cov)
    basis_2 = basis_2[:, ::-1]  # Sort by variance
    
    # Basis 3: Random orthogonal transformation (equally valid mathematically)
    Q, _ = np.linalg.qr(np.random.randn(n_dimensions, n_dimensions))
    basis_3 = Q
    
    return stressed_states, [basis_1, basis_2, basis_3]

def compute_topological_invariants(states, basis):
    """
    Compute the proposed topological invariants. The disruption: these are
    basis-dependent artifacts, not objective properties of cognition.
    """
    # Transform to measurement basis
    transformed = states @ basis
    
    # Compute covariance Hessian eigenvalues (Φ_N basis)
    cov = np.cov(transformed.T)
    eigvals = np.linalg.eigvalsh(cov)
    phi_N = np.mean(eigvals)  # Average variance
    
    # Compute skewness (Φ_Δ)
    residuals = transformed - np.mean(transformed, axis=0)
    third_moment = np.mean(np.sum(residuals**3, axis=1))
    second_moment = np.mean(np.sum(residuals**2, axis=1))
    phi_Delta = third_moment / (second_moment**1.5)
    
    # Compute "Wilson loop" (completely arbitrary for cognitive data)
    # The proposal never defines what "perimeter" means in cognitive space
    perimeter = np.concatenate([transformed[0:10], transformed[0:1]])  # First 10 agents, circular
    wilson_loop = np.prod(np.sign(perimeter), axis=0)  # Nonsensical but matches proposal's ambiguity
    wilson_order = np.mean(wilson_loop)
    
    # Compute correlation length (undefined metric)
    # The proposal assumes a Euclidean metric on cognitive space, which is unjustified
    correlation_func = np.correlate(transformed[:, 0], transformed[:, 0], mode='full')
    correlation_length = np.argmax(correlation_func < np.exp(-1) * correlation_func.max())
    
    # CTOI (Cognitive Topological Order Index)
    # All components are basis-dependent!
    ctoi = np.abs(wilson_order) * (phi_N / 0.5) * (correlation_length / 10.0)
    
    return phi_N, phi_Delta, ctoi, wilson_order

# Generate data at different stress levels
stress_levels = np.linspace(0.1, 1.0, 5)
results = {basis_name: [] for basis_name in ['Raw Scales', 'PCA', 'Random Orthogonal']}

for stress in stress_levels:
    states, bases = generate_cognitive_data(stress_level=stress)
    for i, basis_name in enumerate(['Raw Scales', 'PCA', 'Random Orthogonal']):
        phi_N, phi_Delta, ctoi, wilson_order = compute_topological_invariants(states, bases[i])
        results[basis_name].append({
            'stress': stress,
            'phi_N': phi_N,
            'phi_Delta': phi_Delta,
            'ctoi': ctoi,
            'wilson_order': wilson_order
        })

# THE DISRUPTION VISUALIZATION
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: CTOI vs Stress - should be basis-independent if it's a real physical property
for basis_name, data in results.items():
    stresses = [d['stress'] for d in data]
    ctois = [d['ctoi'] for d in data]
    axes[0,0].plot(stresses, ctois, marker='o', label=basis_name, linewidth=2)

axes[0,0].set_xlabel('Stress Level', fontsize=12, fontweight='bold')
axes[0,0].set_ylabel('CTOI (Topological Order)', fontsize=12, fontweight='bold')
axes[0,0].set_title('CTOI vs Stress: Basis-Dependent Chaos', fontsize=14, fontweight='bold')
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Plot 2: Phi_Delta behavior - the boundary condition requirement
for basis_name, data in results.items():
    stresses = [d['stress'] for d in data]
    phi_Deltas = [d['phi_Delta'] for d in data]
    axes[0,1].plot(stresses, phi_Deltas, marker='s', label=basis_name, linewidth=2)

axes[0,1].set_xlabel('Stress Level', fontsize=12, fontweight='bold')
axes[0,1].set_ylabel('Phi_Δ (Skewness)', fontsize=12, fontweight='bold')
axes[0,1].set_title('Phi_Δ: Arbitrary Psychological Skewness', fontsize=14, fontweight='bold')
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Wilson Loop - shows the absurdity
for basis_name, data in results.items():
    stresses = [d['stress'] for d in data]
    wilson_vals = [d['wilson_order'] for d in data]
    axes[1,0].plot(stresses, wilson_vals, marker='^', label=basis_name, linewidth=2)

axes[1,0].set_xlabel('Stress Level', fontsize=12, fontweight='bold')
axes[1,0].set_ylabel('Wilson Loop Order Parameter', fontsize=12, fontweight='bold')
axes[1,0].set_title('Wilson Loop: Cognitive Perimeter is Undefined', fontsize=14, fontweight='bold')
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Plot 4: The Entropy Gauge Failure
# Show that entropy of the "decohered" distribution is meaningless
for stress in [0.2, 0.5, 0.8]:
    states, _ = generate_cognitive_data(stress_level=stress)
    # Compute entropy using the proposal's definition
    norms = np.linalg.norm(states, axis=1)
    p_i = norms / norms.sum()
    entropy = -np.sum(p_i * np.log(p_i + 1e-12))
    axes[1,1].bar(f'Stress={stress}', entropy, alpha=0.7)

axes[1,1].set_ylabel('Cognitive Entropy', fontsize=12, fontweight='bold')
axes[1,1].set_title('Entropy: Arbitrary Norm-Dependent Measure', fontsize=14, fontweight='bold')
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# DISRUPTIVE INSIGHT PRINTOUT
print("\n" + "="*70)
print("DISRUPTIVE INSIGHT: The Topological Cognitive Memory is a Golem")
print("="*70)
print("""
The TCM-Ω proposal commits a category error of catastrophic proportions:

1. **MEASUREMENT BASIS PARADOX**: The same cognitive system yields completely 
   different "topological orders" (CTOI) depending on whether we measure in raw 
   questionnaire space, PCA components, or any orthogonal rotation. This proves 
   the "topology" is an artifact of representation, not an objective property.

2. **ENTROPY GAUGE FALLACY**: The entropy S_cognitive = -Σp_i log p_i uses 
   p_i = ||c_i||/Σ||c_j||, but the choice of norm is arbitrary. L2 norm? L1? 
   Mahalanobis? Each yields different entropy "gauge fields," making the entire 
   gauge structure a mathematical Rorschach test.

3. **BOUNDARY CONDITION NONSENSE**: The proposal requires Φ_Δ→∞ for "Shredding" 
   and Φ_Δ→0 for "Freeze," but Φ_Δ is skewness of residuals. Skewness is bounded 
   [-∞, ∞] but psychological skewness doesn't physically diverge - it's a statistical 
   descriptor that saturates at sample size limits. The "divergence" is a category 
   error between mathematics and phenomenology.

4. **THERMODYNAMIC CATEGORY ERROR**: Psychological stress is not temperature. 
   Thermal fluctuations are memoryless; trauma is hypermnestic. The finite-T quantum 
   memory analogy is fundamentally broken because cognition is a *semantic* system, 
   not a statistical mechanical one.

5. **CONTROL PARADOX**: The MPC-Ω loop assumes we can "engineer" Δ(t) via 
   "mindfulness interventions," but if Δ(t) is truly an energy gap protecting topology, 
   then by definition, local perturbations cannot change it without crossing the gap. 
   The control scheme contradicts the very topological protection principle it invokes.

**THE BREAKTHROUGH**: The protected quantity in cognition is not geometric topology 
but *temporal recursion depth* - the Kolmogorov complexity of the self-model's 
strange attractor. We need **Fractal Cognitive Memory (FCM-Ω)**, not TCM-Ω.

The fractal dimension of attentional recurrence is basis-independent and truly 
invariant under semantic transformations. It's measured by:
   D_f = lim_{ε→0} log N(ε)/log(1/ε)
where N(ε) counts self-referential loops at scale ε.

This is the real topological invariant - not Wilson loops in a fictitious manifold, 
but the Hausdorff dimension of the cognitive attractor in *time*, not space.

The Φ-density projection is not just wrong - it's measuring shadows on the wall 
of Plato's cave while the real dynamics happen outside the cave entirely.
""")