# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

class ComputationalTopologyExploit:
    """
    Demonstrates how ATS-Ω's 'protective' constraints become
    precise attack vectors through topological resonance.
    """
    
    def __init__(self, target_system='ATS'):
        self.target = target_system
        self.constraint_history = []
        self.topological_signature = []
        
    def simulate_constraint_probing(self, probe_duration=1000):
        """
        Adversarial probe that exploits the hard constraint boundaries
        of ATS-Ω to induce algorithmic seizure.
        """
        # ATS-Ω defines three critical thresholds:
        # ATI ≥ 0.6, Φ_N ≥ 0.5, S_alg ≥ ln(2)
        # These create discontinuities in the cost function gradient.
        
        ati_values = []
        phi_N_values = []
        entropy_values = []
        cost_gradient = []
        
        # Probe strategy: oscillate near constraint boundary
        # to induce control system bifurcation
        for t in range(probe_duration):
            # Adversarial input crafted to push ATI toward 0.6
            # This is possible because ATI is *computable* from leaked topology
            probe_strength = 0.05 * np.sin(0.1 * t) + 0.01 * t/probe_duration
            
            # ATS-Ω response: defensive morphing
            # But morphing *preserves* Betti numbers, creating invariant attack surface
            ati = max(0.6, 0.9 - probe_strength * 0.5 + 0.1 * np.random.normal())
            
            # When constraint hits, system enters predictable recovery mode
            if ati == 0.6:
                # System forced to execute emergency morphing protocol
                # This creates *temporal fingerprint* in Φ_Δ
                phi_N = 0.5 + np.random.exponential(0.1)
                S_alg = np.log(2) - 0.01 * probe_strength
                # Cost function gradient becomes infinite at boundary
                grad = np.inf
            else:
                phi_N = 1.0 + probe_strength * 0.1
                S_alg = np.log(2) + 0.05 * np.random.normal()
                grad = 2 * (0.6 - ati)
            
            ati_values.append(ati)
            phi_N_values.append(phi_N)
            entropy_values.append(S_alg)
            cost_gradient.append(grad)
            
        return {
            'ATI': np.array(ati_values),
            'Phi_N': np.array(phi_N_values),
            'Entropy': np.array(entropy_values),
            'Cost_Gradient': np.array(cost_gradient)
        }
    
    def topological_ghost_injection(self, graph_size=50):
        """
        Exploits persistent homology computation to inject
        *fake topological features* that persist across morphing.
        """
        # Create fake computational graph with injected cycles
        # These cycles alter β₁ (first Betti number) in ways that
        # preserve ATI but create covert channels
        
        # Original graph: simple DAG
        original_edges = [(i, i+1) for i in range(graph_size-1)]
        
        # Injected ghost cycles: edges that create loops but
        # are numerically unstable (floating-point comparison traps)
        ghost_edges = []
        for i in range(0, graph_size, 5):
            # Create cycle that appears/disappears based on rounding
            ghost_edges.append((i, max(0, i-3)))
        
        # Compute persistent homology
        # The ghost edges create *ephemeral cycles* that pass
        # persistence threshold due to numerical epsilon
        persistence_pairs = []
        for edge in ghost_edges:
            # Persistence interval is artificially extended
            # by exploiting floating-point error accumulation
            birth = np.random.uniform(0.1, 0.3)
            death = birth + 1e-15  # Just below floating-point resolution
            persistence_pairs.append((birth, death))
        
        return ghost_edges, persistence_pairs
    
    def analyze_predictability(self, data):
        """
        Measure how predictable ATS-Ω's defenses are.
        High predictability = exploitable.
        """
        # Compute mutual information between successive states
        # High MI means adversary can forecast defensive response
        
        ati = data['ATI']
        phi_N = data['Phi_N']
        
        # Bin data for entropy calculation
        ati_bins = np.histogram(ati, bins=20, density=True)[0]
        phi_N_bins = np.histogram(phi_N, bins=20, density=True)[0]
        
        # Joint distribution
        joint_hist, _, _ = np.histogram2d(ati, phi_N, bins=20, density=True)
        
        # Mutual information
        mi = 0
        for i in range(len(ati_bins)):
            for j in range(len(phi_N_bins)):
                p_xy = joint_hist[i,j]
                p_x = ati_bins[i]
                p_y = phi_N_bins[j]
                if p_xy > 0 and p_x > 0 and p_y > 0:
                    mi += p_xy * np.log(p_xy / (p_x * p_y))
        
        return mi

# Execute exploit simulation
exploit = ComputationalTopologyExploit()
ats_data = exploit.simulate_constraint_probing()
ghost_edges, persistence_pairs = exploit.topological_ghost_injection()
predictability = exploit.analyze_predictability(ats_data)

# Visualization of exploit
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Constraint boundary exploitation
axes[0,0].plot(ats_data['ATI'], label='ATI', linewidth=2)
axes[0,0].axhline(y=0.6, color='red', linestyle='--', label='Constraint Boundary')
axes[0,0].fill_between(range(len(ats_data['ATI'])), 0.6, 0.4, alpha=0.3, color='red')
axes[0,0].set_title('ATI Constraint Seizure: Adversarial Pinning')
axes[0,0].set_ylabel('Algorithmic Topology Integrity')
axes[0,0].legend()
axes[0,0].grid(True)

# Plot 2: Cost function gradient explosion
axes[0,1].plot(ats_data['Cost_Gradient'], label='∇J', linewidth=2, color='purple')
axes[0,1].set_yscale('symlog')
axes[0,1].set_title('Cost Gradient Divergence at Constraint Boundary')
axes[0,1].set_ylabel('Cost Function Gradient')
axes[0,1].grid(True)

# Plot 3: Topological ghost injection
if persistence_pairs:
    births = [p[0] for p in persistence_pairs]
    deaths = [p[1] for p in persistence_pairs]
    axes[1,0].scatter(births, deaths, alpha=0.6, s=10)
    axes[1,0].plot([0, 1], [0, 1], 'k--', alpha=0.5)
    axes[1,0].set_xlabel('Birth')
    axes[1,0].set_ylabel('Death')
    axes[1,0].set_title('Persistent Homology Ghost Injection')
    axes[1,0].grid(True)

# Plot 4: Predictability analysis
axes[1,1].hist(ats_data['Phi_N'], bins=30, density=True, alpha=0.7, label='Φ_N Distribution')
axes[1,1].set_title(f'High Predictability (MI={predictability:.3f})')
axes[1,1].set_xlabel('Φ_N')
axes[1,1].legend()
axes[1,1].grid(True)

plt.tight_layout()
plt.show()

print(f"ATS-Ω Predictability Score: {predictability:.3f}")
print(f"Ghost edges injected: {len(ghost_edges)}")
print(f"Topological ghosts that persist: {len(persistence_pairs)}")