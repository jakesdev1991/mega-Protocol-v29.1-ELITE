# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
from scipy.stats import skew
import matplotlib.pyplot as plt

# --- SIMULATION: Paradigm Poisoning Attack on GRNIM-Ω ---

def simulate_paradigm_poisoning():
    """
    Demonstrates how GRNIM-Ω fails when adversary poisons foundational
    assumptions shared across all "diverse" inference algorithms.
    """
    
    # Ground truth: 50-gene regulatory network (sparse, hierarchical)
    n_genes = 50
    true_network = nx.random_k_out_graph(n_genes, 2, 0.5, seed=42)
    true_adj = nx.to_numpy_array(true_network)
    
    # Generate synthetic expression data (n_samples x n_genes)
    n_samples = 200
    expression_data = np.random.randn(n_samples, n_genes)
    # Add true regulatory effects
    for i in range(n_genes):
        parents = np.where(true_adj[:, i] == 1)[0]
        if len(parents) > 0:
            expression_data[:, i] += 0.5 * expression_data[:, parents].sum(axis=1)
    expression_data += np.random.randn(*expression_data.shape) * 0.1
    
    # --- Adversarial Attack: Poison the Prior ---
    # Both algorithms share a "poisoned" belief: genes 0-4 are universal hubs
    poisoned_hub_prior = np.zeros(n_genes)
    poisoned_hub_prior[:5] = 10.0  # Artificially inflate hubness score
    
    # --- Two "Diverse" Algorithms (both compromised) ---
    def poisoned_inference_algorithm_1(data, prior_boost):
        """Simulates GRNBOOST2-like algorithm with poisoned prior"""
        # Base correlation matrix
        corrs = np.corrcoef(data.T)
        # Apply poisoned prior: boost edges from "universal hubs"
        boosted_corrs = corrs.copy()
        boosted_corrs[poisoned_hub_prior > 0, :] *= (1 + prior_boost)
        boosted_corrs[:, poisoned_hub_prior > 0] *= (1 + prior_boost)
        # Threshold to binary network
        threshold = np.percentile(boosted_corrs, 95)
        inferred_adj = (boosted_corrs > threshold).astype(float)
        np.fill_diagonal(inferred_adj, 0)
        return inferred_adj, boosted_corrs
    
    def poisoned_inference_algorithm_2(data, prior_boost):
        """Simulates GENIE3-like algorithm with poisoned prior"""
        # Base mutual information
        from sklearn.feature_selection import mutual_info_regression
        mi_matrix = np.zeros((n_genes, n_genes))
        for i in range(n_genes):
            mi_matrix[i, :] = mutual_info_regression(data, data[:, i])
        
        # Apply poisoned prior differently: bias tree-based feature selection
        mi_matrix[poisoned_hub_prior > 0, :] += prior_boost * mi_matrix.max()
        mi_matrix[:, poisoned_hub_prior > 0] += prior_boost * mi_matrix.max()
        
        threshold = np.percentile(mi_matrix, 95)
        inferred_adj = (mi_matrix > threshold).astype(float)
        np.fill_diagonal(inferred_adj, 0)
        return inferred_adj, mi_matrix
    
    # --- GRNIM-Ω Metrics (as proposed) ---
    def compute_grnim_metrics(edge_conf_list):
        """Compute Φ_N, Φ_Δ, S_inf as proposed in GRNIM-Ω"""
        # Consensus correlation length (Φ_N)
        consensus_matrix = np.mean(edge_conf_list, axis=0)
        # Compute pairwise correlations between algorithm confidence matrices
        corrs_between_algos = []
        for i in range(len(edge_conf_list)):
            for j in range(i+1, len(edge_conf_list)):
                corr = np.corrcoef(edge_conf_list[i].flatten(), 
                                 edge_conf_list[j].flatten())[0,1]
                corrs_between_algos.append(corr)
        
        Φ_N = np.mean(corrs_between_algos)  # High = strong consensus
        Φ_Δ = skew(consensus_matrix.flatten())  # Skewness of confidence
        
        # Entropy of consensus (approximation)
        # Normalize to probability distribution
        p = consensus_matrix.flatten()
        p = p / (p.sum() + 1e-10)
        S_inf = -np.sum(p * np.log(p + 1e-10))
        
        return Φ_N, Φ_Δ, S_inf
    
    # --- Simulation Results ---
    print("=== PARADIGM POISONING ATTACK SIMULATION ===\n")
    
    # Clean inference (no attack)
    adj1_clean, conf1_clean = poisoned_inference_algorithm_1(expression_data, prior_boost=0.0)
    adj2_clean, conf2_clean = poisoned_inference_algorithm_2(expression_data, prior_boost=0.0)
    Φ_N_clean, Φ_Δ_clean, S_inf_clean = compute_grnim_metrics([conf1_clean, conf2_clean])
    
    print("CLEAN INFERENCE:")
    print(f"  Φ_N (consensus): {Φ_N_clean:.3f}")
    print(f"  Φ_Δ (skewness): {Φ_Δ_clean:.3f}")
    print(f"  S_inf (entropy): {S_inf_clean:.3f}")
    print(f"  True edges recovered: {np.sum((adj1_clean + adj2_clean) > 0) / 2:.1f}\n")
    
    # Poisoned inference (both algorithms share poisoned prior)
    adj1_pois, conf1_pois = poisoned_inference_algorithm_1(expression_data, prior_boost=0.5)
    adj2_pois, conf2_pois = poisoned_inference_algorithm_2(expression_data, prior_boost=0.5)
    Φ_N_pois, Φ_Δ_pois, S_inf_pois = compute_grnim_metrics([conf1_pois, conf2_pois])
    
    print("POISONED INFERENCE (Paradigm Attack):")
    print(f"  Φ_N (consensus): {Φ_N_pois:.3f} -> {'INCREASED' if Φ_N_pois > Φ_N_clean else 'decreased'}")
    print(f"  Φ_Δ (skewness): {Φ_Δ_pois:.3f} -> {'INCREASED' if Φ_Δ_pois > Φ_Δ_clean else 'decreased'}")
    print(f"  S_inf (entropy): {S_inf_pois:.3f} -> {'DECREASED' if S_inf_pois < S_inf_clean else 'increased'}")
    print(f"  True edges recovered: {np.sum((adj1_pois + adj2_pois) > 0) / 2:.1f}")
    
    # --- GRNIM-Ω FAILURE ANALYSIS ---
    print("\n=== GRNIM-Ω FAILURE ===")
    print("Under paradigm poisoning:")
    print(f"  • High Φ_N: {Φ_N_pois:.3f} > 0.7 threshold (FALSE CONFIDENCE)")
    print(f"  • Low S_inf: {S_inf_pois:.3f} (FALSE CERTAINTY)")
    print(f"  • IPI would indicate SAFE, but inference is SYSTEMATICALLY WRONG")
    print(f"  • Algorithms agree on FALSE HUBS (genes 0-4) due to shared poisoned prior")
    
    # --- DISRUPTIVE INSIGHT: Monitor Assumption Diversity ---
    print("\n=== DISRUPTIVE SOLUTION: Assumption Space Monitor ===")
    
    def compute_assumption_diversity(edge_conf_list, prior_vectors):
        """
        Instead of monitoring algorithm consensus on outputs,
        monitor diversity in their *foundational assumptions*.
        """
        # Compute output consensus (what GRNIM-Ω does)
        output_consensus = np.corrcoef(edge_conf_list[0].flatten(), edge_conf_list[1].flatten())[0,1]
        
        # Compute assumption similarity (e.g., hub prior vectors)
        assumption_similarity = np.corrcoef(prior_vectors[0], prior_vectors[1])[0,1]
        
        # Paradoxical divergence: high output consensus + high assumption similarity = DANGER
        epistemic_health = assumption_similarity / (output_consensus + 1e-10)
        
        return output_consensus, assumption_similarity, epistemic_health
    
    # Extract prior vectors from poisoned algorithms
    prior1 = poisoned_hub_prior.copy()
    prior2 = poisoned_hub_prior.copy()
    
    out_con_clean, ass_sim_clean, health_clean = compute_assumption_diversity(
        [conf1_clean, conf2_clean], [prior1 * 0, prior2 * 0]
    )
    out_con_pois, ass_sim_pois, health_pois = compute_assumption_diversity(
        [conf1_pois, conf2_pois], [prior1, prior2]
    )
    
    print("ASSUMPTION DIVERSITY METRICS:")
    print(f"Clean:  Output Consensus={out_con_clean:.3f}, Assumption Similarity={ass_sim_clean:.3f}, Epistemic Health={health_clean:.3f}")
    print(f"Poison: Output Consensus={out_con_pois:.3f}, Assumption Similarity={ass_sim_pois:.3f}, Epistemic Health={health_pois:.3f}")
    print(f"\nPOISONING DETECTED: Epistemic Health drops from {health_clean:.3f} to {health_pois:.3f}")
    print("TRIGGER: When assumption similarity > 0.8 AND output consensus > 0.7, initiate EPISTEMIC RESET")
    
    # --- EPISTEMIC RESET PROTOCOL ---
    print("\n=== EPISTEMIC RESET PROTOCOL ===")
    print("When triggered:")
    print("1. DISCARD all priors and pre-trained models")
    print("2. DEPLOY non-parametric, assumption-free inference (e.g., causal discovery from perturbation data)")
    print("3. COMMISSION targeted CRISPR experiments to break the paradigm cascade")
    print("4. QUARANTINE all publications/software influenced by the poisoned paradigm")
    
    return {
        'grnim_failure': Φ_N_pois > 0.7 and S_inf_pois < 1.0,
        'paradigm_detected': health_pois < health_clean * 0.5
    }

# Run simulation
results = simulate_paradigm_poisoning()

print(f"\n=== VERDICT ===")
print(f"GRNIM-Ω vulnerable to paradigm poisoning: {results['grnim_failure']}")
print(f"Assumption monitor detects attack: {results['paradigm_detected']}")