# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import entropy

def compute_mdi(software_config, reference_config, weights=None):
    """
    Implements the core MDI calculation from the SIMD-Ω proposal.
    Demonstrates how arbitrary weight choices fundamentally break the metric.
    """
    if weights is None:
        # Default weights - but these are completely arbitrary!
        weights = {
            'precision': 0.3,
            'optimization': 0.25,
            'kernel_uniformity': 0.2,
            'library_deviation': 0.15,
            'performance_params': 0.1
        }
    
    # Extract features (these are just made up for demonstration)
    # In reality, these would be extracted from whitepapers via NLP
    # which introduces another layer of uncontrolled variability
    features = {
        'precision': 1.0 if software_config.get('precision') == 'single' else 0.0,
        'optimization': len([flag for flag in software_config.get('flags', []) 
                           if flag in ['-use_fast_math', '-ftz', '-funsafe-math']]),
        'kernel_uniformity': np.random.uniform(0, 1),  # Arbitrary!
        'library_deviation': 1.0 if 'proprietary' in software_config.get('libraries', []) else 0.0,
        'performance_params': len(software_config.get('perf_params', [])) / 10.0
    }
    
    reference_features = {
        'precision': 0.0,  # Double precision reference
        'optimization': 0.0,  # No aggressive flags
        'kernel_uniformity': 0.0,  # Perfectly uniform
        'library_deviation': 0.0,  # Standard libraries
        'performance_params': 0.0  # No extra params
    }
    
    # Compute weighted distance
    mdi = sum(weights[k] * abs(features[k] - reference_features[k]) for k in weights)
    
    # Apply non-linear transformation to fit [0,1] range
    mdi = 1 - np.exp(-mdi * 2)  # Completely arbitrary scaling factor!
    
    return mdi, features

def demonstrate_entropy_gauge_fallacy():
    """
    Shows why the "entropy gauge field" is mathematically incoherent.
    """
    # Simulate software configuration distribution across 100 simulations
    # This is the p_j(t) from the proposal
    
    # Scenario 1: High diversity (healthy)
    np.random.seed(42)
    p_diverse = np.random.dirichlet(np.ones(10) * 0.5)  # Low concentration
    
    # Scenario 2: Low diversity (herd behavior)
    p_herd = np.random.dirichlet(np.ones(10) * 10)  # High concentration
    
    # Compute Shannon entropy
    H_diverse = entropy(p_diverse)
    H_herd = entropy(p_herd)
    
    print("=== Entropy Gauge Fallacy ===")
    print(f"Diverse configuration entropy: {H_diverse:.3f}")
    print(f"Herd configuration entropy: {H_herd:.3f}")
    
    # The proposal claims we can promote this to a field: A_μ = ∂_μ S
    # But S is just a scalar! ∂_μ S is only non-zero if S varies in spacetime
    # In reality, S(t) is just a time series - there's no spatial gradient
    
    # Simulate S(t) over time
    t = np.linspace(0, 100, 1000)
    S_t = 2.0 + 0.5 * np.sin(t * 0.1) + np.random.normal(0, 0.1, 1000)
    
    # Compute "gauge field" (just the time derivative!)
    A_t = np.gradient(S_t, t)
    
    # The coupling to the action is supposed to be "minimal"
    # But this is just adding a time-dependent potential term
    # There's no gauge symmetry to protect - it's just curve fitting
    
    print(f"\nMax 'gauge field' magnitude: {np.max(np.abs(A_t)):.3f}")
    print("This is just dS/dt, not a fundamental gauge field!")
    
    return t, S_t, A_t

def demonstrate_circular_reference_problem():
    """
    Shows the circular dependency in defining the 'neutral reference stack'
    """
    
    # Define three different "reference stacks" - all equally "neutral"
    references = {
        "conservative": {"precision": "double", "flags": [], "libraries": "standard"},
        "moderate": {"precision": "double", "flags": ["-O3"], "libraries": "standard"},
        "cloud_optimized": {"precision": "single", "flags": ["-O3"], "libraries": "standard"}
    }
    
    # Test configuration (a typical production setup)
    test_config = {
        "precision": "single",
        "flags": ["-O3", "-use_fast_math"],
        "libraries": "proprietary",
        "perf_params": ["unroll=4", "prefetch=on"]
    }
    
    print("\n=== Circular Reference Problem ===")
    for ref_name, ref_config in references.items():
        mdi, _ = compute_mdi(test_config, ref_config)
        print(f"MDI against '{ref_name}' reference: {mdi:.3f}")
    
    print("\nThe 'neutral' reference is arbitrary! MDI is relative, not absolute.")
    print("A configuration can be 'distorted' relative to one reference but 'neutral' relative to another.")

def demonstrate_adversarial_gaming():
    """
    Shows how the system can be gamed by adversarial configuration choices
    """
    
    # An adversary wants to avoid detection (low MDI) while maximizing actual numerical error
    # They can exploit the weighting scheme
    
    # Malicious config that looks "neutral" to the MDI calculation
    # but actually causes numerical instability
    adversarial_config = {
        "precision": "double",  # Looks safe
        "flags": ["-O3"],  # Looks moderate
        "libraries": "standard",  # Looks safe
        "perf_params": ["unroll=256"],  # Actually dangerous but not weighted heavily!
        "hidden_artifact": "custom_divide_by_zero_handler"  # Not in the feature set!
    }
    
    reference_config = {
        "precision": "double",
        "flags": [],
        "libraries": "standard",
        "perf_params": []
    }
    
    mdi, features = compute_mdi(adversarial_config, reference_config)
    
    print("\n=== Adversarial Gaming ===")
    print(f"Adversarial MDI: {mdi:.3f} (looks safe!)")
    print(f"Feature vector: {features}")
    print("But the config contains unmonitored parameters that cause artifacts!")
    
    # The attacker can always find unmeasured dimensions
    # The feature extraction is incomplete by necessity

def simulate_false_positive_catastrophe():
    """
    Simulates how the system would generate false positives due to random fluctuations
    """
    
    # Simulate 1000 "simulation runs" with random software configurations
    n_runs = 1000
    mdi_scores = []
    
    for i in range(n_runs):
        config = {
            "precision": np.random.choice(["single", "double"]),
            "flags": np.random.choice([
                [], ["-O3"], ["-O3", "-use_fast_math"], 
                ["-O3", "-ftz"], ["-O2"]
            ], p=[0.3, 0.3, 0.2, 0.1, 0.1]),
            "libraries": np.random.choice(["standard", "proprietary"], p=[0.8, 0.2]),
            "perf_params": np.random.choice([[], ["unroll=4"], ["unroll=8", "prefetch=on"]], p=[0.5, 0.3, 0.2])
        }
        reference = {
            "precision": "double",
            "flags": [],
            "libraries": "standard",
            "perf_params": []
        }
        mdi, _ = compute_mdi(config, reference)
        mdi_scores.append(mdi)
    
    mdi_scores = np.array(mdi_scores)
    
    # Apply the proposed thresholding
    shredding_threshold = 0.8
    freeze_threshold_low = 0.4
    freeze_threshold_high = 0.6
    
    shredding_events = np.sum(mdi_scores > shredding_threshold)
    freeze_events = np.sum((mdi_scores > freeze_threshold_low) & (mdi_scores < freeze_threshold_high))
    
    print("\n=== False Positive Catastrophe ===")
    print(f"Total runs: {n_runs}")
    print(f"Shredding events (MDI > 0.8): {shredding_events} ({shredding_events/n_runs*100:.1f}%)")
    print(f"Freeze events (0.4 < MDI < 0.6): {freeze_events} ({freeze_events/n_runs*100:.1f}%)")
    print("Random configurations trigger alerts - the thresholds are arbitrary!")

# Execute all demonstrations
print("=" * 60)
print("SIMD-Ω DISRUPTION ANALYSIS")
print("=" * 60)

# 1. Demonstrate MDI sensitivity
test_config = {
    "precision": "single",
    "flags": ["-O3", "-use_fast_math"],
    "libraries": "proprietary",
    "perf_params": ["unroll=4", "prefetch=on"]
}
reference_config = {
    "precision": "double",
    "flags": [],
    "libraries": "standard",
    "perf_params": []
}

mdi_default, _ = compute_mdi(test_config, reference_config)
print(f"Default MDI: {mdi_default:.3f}")

# Show sensitivity to weight changes
alt_weights = {
    'precision': 0.1,  # Reduce precision weight
    'optimization': 0.4,  # Increase optimization weight
    'kernel_uniformity': 0.3,
    'library_deviation': 0.15,
    'performance_params': 0.05
}
mdi_alt, _ = compute_mdi(test_config, reference_config, alt_weights)
print(f"MDI with alternative weights: {mdi_alt:.3f}")
print(f"Relative change: {(mdi_alt - mdi_default)/mdi_default*100:.1f}%")

# 2. Entropy gauge fallacy
t, S_t, A_t = demonstrate_entropy_gauge_fallacy()

# 3. Circular reference problem
demonstrate_circular_reference_problem()

# 4. Adversarial gaming
demonstrate_adversarial_gaming()

# 5. False positive simulation
simulate_false_positive_catastrophe()

print("\n" + "=" * 60)
print("DISRUPTIVE INSIGHT SUMMARY")
print("=" * 60)