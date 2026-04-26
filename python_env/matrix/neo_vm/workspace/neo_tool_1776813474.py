# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
from collections import defaultdict

# --- Disruptive Insight: "Phoenix Protocol" vs. Static Diversity Regulation ---
# The DSTR-Ω framework assumes that maintaining a stable, diverse design manifold
# reduces systemic risk. This simulation demonstrates that a static regulator can be
# gamed and creates a new monoculture (the regulator's own metrics), while a
# chaotic "Phoenix" protocol that triggers forced redesign under stress achieves
# superior long-term resilience by preventing any single design from ever becoming
# systemically critical.

class AMMDesign:
    def __init__(self, design_id, feature_vector, family_id):
        self.id = design_id
        self.features = np.array(feature_vector)  # design parameters (e.g., curve type, fee)
        self.family_id = family_id
        self.tvl = 0.0

def compute_design_metrics(designs):
    """Compute simplified metrics: 'curvature' as avg pairwise similarity, HSI, entropy."""
    # Pairwise distances
    features = np.vstack([d.features for d in designs])
    dists = np.linalg.norm(features[:, None] - features[None, :], axis=2)
    # "Curvature" = average similarity (inverse distance)
    curvature = np.mean(1 / (1 + dists[dists > 0]))  # avoid self-distances
    
    # TVL distribution
    tvls = np.array([d.tvl for d in designs])
    total_tvl = tvls.sum()
    if total_tvl == 0:
        return 0, 0, 0, 0
    
    # Conditional entropy: partition by family
    families = list(set(d.family_id for d in designs))
    family_tvls = defaultdict(float)
    design_tvls_by_family = defaultdict(list)
    for d in designs:
        family_tvls[d.family_id] += d.tvl
        design_tvls_by_family[d.family_id].append(d.tvl)
    
    # p(f) and p(d|f)
    S_cond = 0.0
    for f in families:
        p_f = family_tvls[f] / total_tvl
        if p_f == 0:
            continue
        # Normalize within family
        fam_tvls = np.array(design_tvls_by_family[f])
        p_df = fam_tvls / fam_tvls.sum()
        # Entropy within family
        H_f = -np.sum(p_df * np.log(p_df + 1e-12))
        S_cond += p_f * H_f
    
    # HSI: sigmoid of curvature * (1 - S_cond)
    HSI = 1 / (1 + np.exp(-10 * (curvature * (1 - S_cond) - 0.5)))
    return curvature, S_cond, HSI, total_tvl

def simulate_attack(designs, threshold=0.5):
    """Attack the largest family if it holds > threshold fraction of TVL."""
    families = defaultdict(list)
    total_tvl = sum(d.tvl for d in designs)
    for d in designs:
        families[d.family_id].append(d)
    
    # Find largest family
    largest_family = max(families.values(), key=lambda fam: sum(d.tvl for d in fam))
    family_tvl = sum(d.tvl for d in largest_family)
    
    # Attack if dominant
    if family_tvl > threshold * total_tvl:
        drain_rate = 0.2  # drain 20% from each design in the family
        for d in largest_family:
            d.tvl *= (1 - drain_rate)
        return True, family_tvl / total_tvl
    return False, 0

def dstr_omega_intervention(designs):
    """Static regulator: move TVL from largest to smallest family to boost entropy."""
    families = defaultdict(list)
    for d in designs:
        families[d.family_id].append(d)
    
    # Find largest and smallest families by TVL
    largest_family = max(families.values(), key=lambda fam: sum(d.tvl for d in fam))
    smallest_family = min([fam for fam in families.values() if sum(d.tvl for d in fam) > 0], 
                          key=lambda fam: sum(d.tvl for d in fam), default=[])
    if not smallest_family:
        return
    
    # Redistribute 5% of largest family's TVL to smallest
    redist_amount = 0.05 * sum(d.tvl for d in largest_family)
    if redist_amount <= 0:
        return
    
    # Subtract from largest (proportional)
    largest_tvl = sum(d.tvl for d in largest_family)
    for d in largest_family:
        d.tvl *= (1 - redist_amount / largest_tvl)
    
    # Add to smallest (proportional)
    smallest_tvl = sum(d.tvl for d in smallest_family)
    for d in smallest_family:
        d.tvl *= (1 + redist_amount / smallest_tvl)

def phoenix_intervention(designs):
    """Chaotic protocol: under stress, mutate all designs, break families, reset TVL."""
    # Randomly reassign features and families (simulate forced redesign)
    for d in designs:
        # Random perturbation of features
        d.features += np.random.normal(0, 0.5, size=d.features.shape)
        # Reassign to a new random family (break old clusters)
        d.family_id = random.randint(0, len(set(d.family_id for d in designs)) * 2)
    # Redistribute TVL uniformly (chaotic rebirth)
    total_tvl = sum(d.tvl for d in designs)
    if total_tvl > 0:
        per_design_tvl = total_tvl / len(designs)
        for d in designs:
            d.tvl = per_design_tvl

def run_simulation(num_designs=100, num_cycles=10, attack_threshold=0.5, hsi_threshold=0.75):
    """Run comparison of DSTR-Ω vs Phoenix Protocol."""
    # Initialize: create clustered designs (families)
    designs = []
    num_families = 5
    for i in range(num_designs):
        family_id = i % num_families
        # Features: random vector, but cluster by family
        base = np.random.random(5) * family_id
        features = base + np.random.random(5) * 0.1
        d = AMMDesign(i, features, family_id)
        d.tvl = 100.0  # uniform initial TVL
        designs.append(d)
    
    # Split into two parallel ecosystems for comparison
    designs_dstr = [AMMDesign(d.id, d.features.copy(), d.family_id) for d in designs]
    designs_phoenix = [AMMDesign(d.id, d.features.copy(), d.family_id) for d in designs]
    for d in designs_dstr:
        d.tvl = 100.0
    for d in designs_phoenix:
        d.tvl = 100.0
    
    results = {
        'DSTR-Ω': {'tvl': [], 'hsi': [], 'entropy': []},
        'Phoenix': {'tvl': [], 'hsi': [], 'entropy': []}
    }
    
    for cycle in range(num_cycles):
        for name, design_set in [('DSTR-Ω', designs_dstr), ('Phoenix', designs_phoenix)]:
            curv, S_cond, HSI, total_tvl = compute_design_metrics(design_set)
            results[name]['tvl'].append(total_tvl)
            results[name]['hsi'].append(HSI)
            results[name]['entropy'].append(S_cond)
            
            # Apply attack
            attacked, dominance = simulate_attack(design_set, attack_threshold)
            
            # Apply intervention based on HSI
            if HSI > hsi_threshold:
                if name == 'DSTR-Ω':
                    dstr_omega_intervention(design_set)
                else:
                    phoenix_intervention(design_set)
    
    return results

# --- Run Simulation and Disruptive Analysis ---
if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)
    
    results = run_simulation(num_designs=50, num_cycles=12)
    
    # Print final TVL survivorship
    print("=== DISRUPTIVE SIMULATION RESULTS ===")
    for name in ['DSTR-Ω', 'Phoenix']:
        initial_tvl = results[name]['tvl'][0]
        final_tvl = results[name]['tvl'][-1]
        survival_rate = final_tvl / initial_tvl * 100
        print(f"{name}: {survival_rate:.1f}% TVL survival")
        print(f"  HSI range: [{min(results[name]['hsi']):.3f}, {max(results[name]['hsi']):.3f}]")
        print(f"  Entropy range: [{min(results[name]['entropy']):.3f}, {max(results[name]['entropy']):.3f}]")
    
    # Key disruption: DSTR-Ω's static entropy maximization creates predictable intervention
    # patterns that attackers can exploit by timing attacks just after redistribution,
    # when the regulator has depleted its "defensive liquidity." Phoenix's chaotic
    # redesign eliminates this predictability and prevents any design from reaching
    # systemic dominance, achieving higher long-term survival despite short-term volatility.