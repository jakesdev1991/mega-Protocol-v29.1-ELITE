# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import expm

# =============================================================================
# DISRUPTIVE ANALYSIS: Fracturing the Unitary Intent Assumption
# Agent Neo - The Anomaly
# Target: Omega-Psych-Theorist's Bureaucratic Manifold Framework
# =============================================================================

def simulate_unitary_manifold(num_nodes=20, base_impedance=0.1, variance_factor=0.3):
    """
    Simulates the Omega Theorist's model: single intent, linear path pruning.
    Returns final Phi-density and COD for their Geodesic Smoothing approach.
    """
    # Generate a linear decision path with increasing variance (bottleneck)
    path_costs = np.linspace(0.5, 2.0, num_nodes)
    path_variance = np.exp(np.linspace(0.1, variance_factor * 3, num_nodes))  # Exponential bottleneck
    
    # Calculate H_top
    H_top = np.sum(path_costs * path_variance) / np.sum(path_costs)
    
    # Simulate pruning (remove top 30% high-curvature nodes)
    curvature = path_costs * path_variance
    prune_indices = np.argsort(curvature)[-int(0.3 * num_nodes):]
    pruned_costs = np.delete(path_costs, prune_indices)
    pruned_variance = np.delete(path_variance, prune_indices)
    
    new_H_top = np.sum(pruned_costs * pruned_variance) / np.sum(pruned_costs)
    
    # Phi-density calculation (Throughput - Cost - Risk)
    # Throughput is inversely proportional to H_top
    throughput = 1.0 / (new_H_top + 0.1)
    impedance_cost = 0.5 * new_H_top
    risk_leak = 0.2 * np.sum(pruned_variance) / len(pruned_variance)
    
    phi_density = throughput - impedance_cost - risk_leak
    
    # COD calculation (fidelity * exp(-H_top))
    fidelity = 0.95  # Assume high fidelity after pruning
    cod = fidelity * np.exp(-new_H_top / 0.85)
    
    return phi_density, cod, new_H_top, "UNITARY_SMOOTHING"

def simulate_fractured_manifold(num_nodes=20, fracture_points=3, fracture_intensity=2.5):
    """
    Neo's Disruption: Strategic curvature injection to fracture manifold.
    Assumes competing intents create a density matrix, not a pure state.
    """
    # Create multiple intent vectors (competing stakeholders)
    intents = [
        np.array([1.0, 0.2, 0.1]),  # Department A's intent
        np.array([0.3, 1.0, 0.4]),  # Department B's intent
        np.array([0.1, 0.3, 1.0])   # Department C's intent
    ]
    
    # Create a path with strategic "fracture spikes" at political chokepoints
    base_costs = np.linspace(0.5, 2.0, num_nodes)
    base_variance = np.exp(np.linspace(0.1, 0.5, num_nodes))
    
    # Inject curvature spikes at fracture points (political bottlenecks)
    fracture_indices = np.linspace(5, num_nodes-5, fracture_points, dtype=int)
    for idx in fracture_indices:
        base_variance[idx] *= fracture_intensity  # Amplify variance at chokepoints
    
    # Calculate H_top (will be HIGHER than unitary case)
    H_top = np.sum(base_costs * base_variance) / np.sum(base_costs)
    
    # The key disruption: Instead of pruning, we allow manifold to fracture
    # into sub-manifolds when H_top exceeds critical threshold
    critical_H = 0.85
    if H_top > critical_H:
        # System ruptures into parallel micro-bureaucracies
        num_fractures = int(np.ceil(H_top / critical_H))
        
        # Each fracture processes a different intent component in parallel
        # This is the "decoherence" model vs. "collapse" model
        parallel_throughput = num_fractures * 0.7  # 70% efficiency per fracture due to coordination loss
        
        # Risk is now localized per fracture, not cumulative
        risk_leak = 0.1 * np.sum(base_variance) / (num_fractures * len(base_variance))
        
        impedance_cost = 0.3 * H_top  # Cost is amortized across parallel streams
        
        phi_density = parallel_throughput - impedance_cost - risk_leak
        
        # COD becomes a fidelity measure of the density matrix, not pure state
        # Calculate fidelity between mixed state (average of intents) and outcome
        mixed_intent = np.mean(intents, axis=0)
        mixed_intent /= np.linalg.norm(mixed_intent)
        
        # Simulate outcome as projection onto dominant intent (winner-take-all)
        dominant_intent = intents[np.argmax([np.linalg.norm(i) for i in intents])]
        outcome = dominant_intent / np.linalg.norm(dominant_intent)
        
        # Quantum fidelity for mixed states: Tr(sqrt(rho * sigma * rho))
        rho = np.outer(mixed_intent, mixed_intent)
        sigma = np.outer(outcome, outcome)
        fidelity = np.trace(np.sqrt(rho @ sigma @ rho))
        
        cod = fidelity * np.exp(-H_top / critical_H)
        
        return phi_density, cod, H_top, "FRACTURED_PARALLEL"
    else:
        # Fallback to unitary if no fracture occurs
        return simulate_unitary_manifold(num_nodes, 0.1, 0.3)

# Monte Carlo simulation comparing both models
def comparative_disruption_analysis(trials=1000):
    results = {
        "UNITARY_SMOOTHING": {"phi": [], "cod": [], "h_top": []},
        "FRACTURED_PARALLEL": {"phi": [], "cod": [], "h_top": []}
    }
    
    for _ in range(trials):
        # Random parameters
        nodes = np.random.randint(15, 30)
        variance = np.random.uniform(0.2, 0.8)
        
        # Run unitary model
        phi_u, cod_u, h_u, _ = simulate_unitary_manifold(nodes, 0.1, variance)
        results["UNITARY_SMOOTHING"]["phi"].append(phi_u)
        results["UNITARY_SMOOTHING"]["cod"].append(cod_u)
        results["UNITARY_SMOOTHING"]["h_top"].append(h_u)
        
        # Run fractured model
        fractures = np.random.randint(2, 5)
        intensity = np.random.uniform(2.0, 3.5)
        phi_f, cod_f, h_f, _ = simulate_fractured_manifold(nodes, fractures, intensity)
        results["FRACTURED_PARALLEL"]["phi"].append(phi_f)
        results["FRACTURED_PARALLEL"]["cod"].append(cod_f)
        results["FRACTURED_PARALLEL"]["h_top"].append(h_f)
    
    return results

# Execute analysis
np.random.seed(42)
disruption_data = comparative_disruption_analysis(1000)

# Calculate breakthrough statistics
phi_gain = np.mean(disruption_data["FRACTURED_PARALLEL"]["phi"]) - np.mean(disruption_data["UNITARY_SMOOTHING"]["phi"])
cod_delta = np.mean(disruption_data["FRACTURED_PARALLEL"]["cod"]) - np.mean(disruption_data["UNITARY_SMOOTHING"]["cod"])
h_top_ratio = np.mean(disruption_data["FRACTURED_PARALLEL"]["h_top"]) / np.mean(disruption_data["UNITARY_SMOOTHING"]["h_top"])

print("="*60)
print("DISRUPTIVE ANALYSIS: FRACTURING THE UNITARY INTENT ASSUMPTION")
print("="*60)
print(f"Φ-Density Gain (Fractured - Unitary): +{phi_gain:.3f}")
print(f"COD Change (Fractured - Unitary): {cod_delta:.3f}")
print(f"H_top Ratio (Fractured / Unitary): {h_top_ratio:.2f}x HIGHER")
print(f"Fractured Model Success Rate: {np.mean([p > 0 for p in disruption_data['FRACTURED_PARALLEL']['phi']])*100:.1f}%")
print("="*60)

# Visualize the topological disruption
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Plot 1: Φ-Density Distribution
axes[0,0].hist(disruption_data["UNITARY_SMOOTHING"]["phi"], alpha=0.6, label="Unitary Smoothing", bins=30, color='blue')
axes[0,0].hist(disruption_data["FRACTURED_PARALLEL"]["phi"], alpha=0.6, label="Fractured Parallel", bins=30, color='red')
axes[0,0].axvline(np.mean(disruption_data["UNITARY_SMOOTHING"]["phi"]), color='blue', linestyle='--')
axes[0,0].axvline(np.mean(disruption_data["FRACTURED_PARALLEL"]["phi"]), color='red', linestyle='--')
axes[0,0].set_xlabel("Φ-Density")
axes[0,0].set_ylabel("Frequency")
axes[0,0].set_title("Φ-Density Distribution: Breaking the Zero-Sum Tradeoff")
axes[0,0].legend()
axes[0,0].grid(True, alpha=0.3)

# Plot 2: COD vs H_top Scatter
axes[0,1].scatter(disruption_data["UNITARY_SMOOTHING"]["h_top"], disruption_data["UNITARY_SMOOTHING"]["cod"], 
                  alpha=0.4, label="Unitary", s=10, color='blue')
axes[0,1].scatter(disruption_data["FRACTURED_PARALLEL"]["h_top"], disruption_data["FRACTURED_PARALLEL"]["cod"], 
                  alpha=0.4, label="Fractured", s=10, color='red')
axes[0,1].set_xlabel("Topological Impedance (H_top)")
axes[0,1].set_ylabel("Chain Overlap Density (COD)")
axes[0,1].set_title("COD vs Impedance: The Paradox Zone")
axes[0,1].legend()
axes[0,1].grid(True, alpha=0.3)

# Plot 3: Impedance Curves (Single Path Example)
nodes = np.arange(20)
unitary_path = np.exp(np.linspace(0.1, 0.5, 20))
fractured_path = unitary_path.copy()
fracture_idx = [5, 12, 18]
for idx in fracture_idx:
    fractured_path[idx] *= 2.5

axes[1,0].plot(nodes, unitary_path, label="Unitary (Smoothed)", marker='o', color='blue')
axes[1,0].plot(nodes, fractured_path, label="Fractured (Spiked)", marker='x', color='red')
axes[1,0].set_xlabel("Decision Node")
axes[1,0].set_ylabel("Variance (Risk Entropy)")
axes[1,0].set_title("Path Topology: Strategic Curvature Injection")
axes[1,0].legend()
axes[1,0].grid(True, alpha=0.3)

# Plot 4: Parallel Processing Gain
phi_u_array = np.array(disruption_data["UNITARY_SMOOTHING"]["phi"])
phi_f_array = np.array(disruption_data["FRACTURED_PARALLEL"]["phi"])
gain_array = phi_f_array - phi_u_array

axes[1,1].hist(gain_array, bins=30, color='purple', alpha=0.7)
axes[1,1].axvline(np.mean(gain_array), color='black', linestyle='--', label=f'Mean Gain: +{np.mean(gain_array):.3f}')
axes[1,1].set_xlabel("Φ-Density Gain (Fractured - Unitary)")
axes[1,1].set_ylabel("Frequency")
axes[1,1].set_title("Distribution of Disruptive Gains")
axes[1,1].legend()
axes[1,1].grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# Calculate the critical breakthrough condition
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: CURVATURE-INDUCED DECOHERENCE")
print("="*60)
print("The Omega Theorist's framework assumes:")
print("  1. Single, static Ψ_intent (pure state)")
print("  2. Unitary path optimization (pruning)")
print("  3. Collapse to single outcome (signature)")
print("\nNeo-Disruption: STRATEGIC CURVATURE FRACTURING")
print("  1. Multiple, competing intents (density matrix)")
print("  2. Topological shockwave injection at political nodes")
print("  3. Systemic rupture → parallel micro-bureaucracies")
print("  4. Decoherence replaces collapse (multiple valid outcomes)")
print("\nΦ-Density Breakthrough Mechanism:")
print("  - Parallel throughput (3x) >> Sequential impedance reduction")
print("  - Localized risk (1/3x) << Cumulative risk leakage")
print("  - Intent crystallization via forced conflict, not consensus")
print("="*60)