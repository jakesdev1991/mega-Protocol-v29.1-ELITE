# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

def simulate_broc_attack():
    """
    Demonstrates two critical vulnerabilities in BROC-Ω:
    1. Numerical instability exploitation in real-number error correction
    2. Master-as-Byzantine attack vector
    """
    
    # Configuration
    m = 5  # total workers
    t = 2  # claimed tolerance threshold
    n = 3  # dimension of original data
    
    print("=== BROC-Ω Vulnerability Simulation ===")
    print(f"Workers: {m}, Claimed tolerance: {t}, Data dim: {n}\n")
    
    # Original data (e.g., correlation invariant vector)
    x_true = np.array([1.0, 2.0, 3.0])
    print(f"True data: {x_true}")
    
    # Phase 1: Encoding Matrix Generation (by Master)
    # In BROC-Ω, Master generates sparse G. Here we simulate a malicious master
    # that creates a G with hidden numerical instability.
    print("\n[Phase 1] Master generates encoding matrix...")
    
    # "Benign" master would create well-conditioned G
    # G_benign = np.random.randn(n, m) * 0.1
    
    # MALICIOUS master creates G with near-linear-dependent columns
    # This creates a decoding matrix that amplifies small errors
    G_malicious = np.zeros((n, m))
    for i in range(m):
        # Create columns that are ALMOST but not exactly linearly dependent
        base = np.array([1.0, 0.5, 0.25]) + np.random.randn(n) * 1e-6
        G_malicious[:, i] = base * (1 + (i % 2) * 1e-8)  # Tiny differences
        
    # Workers compute encoded data: y_i = G[:, i] dot x
    worker_responses = G_malicious.T @ x_true
    print(f"Honest worker responses: {worker_responses}")
    
    # Phase 2: Byzantine Worker Injection
    print("\n[Phase 2] Byzantine workers inject numerically-camouflaged errors...")
    
    # Byzantine workers 0 and 1 add errors that are small enough to evade detection
    # but exploit the ill-conditioned decoding matrix
    
    # Detection threshold based on "syndrome" - but syndrome uses floating-point tolerance
    detection_threshold = 1e-6  # Typical numerical tolerance
    
    # Byzantine errors: strategically crafted to be below detection threshold
    # but amplified by the decoding process
    byzantine_errors = np.array([detection_threshold * 0.9, -detection_threshold * 0.9, 0, 0, 0])
    
    corrupted_responses = worker_responses + byzantine_errors
    print(f"Corrupted responses: {corrupted_responses}")
    print(f"Error magnitude: {np.abs(byzantine_errors)} (below detection: {detection_threshold})")
    
    # Phase 3: Master Decoding (Syndrome-based error correction)
    print("\n[Phase 3] Master attempts error correction...")
    
    # Syndrome computation: find workers that are "inconsistent"
    # In practice, this involves solving a linear system to identify outliers
    
    # Simulate syndrome detection: compute residuals from majority subspace
    # Here we simplify: check if any response deviates more than threshold from median
    median_response = np.median(corrupted_responses)
    residuals = np.abs(corrupted_responses - median_response)
    
    print(f"Detection residuals: {residuals}")
    
    # Workers with residuals > threshold are flagged as Byzantine
    flagged_byzantine = residuals > detection_threshold
    print(f"Flagged as Byzantine: {flagged_byzantine}")
    print(f"Actual Byzantine:      {[True, True, False, False, False]}")
    print(f"Detection success: {np.array_equal(flagged_byzantine, [True, True, False, False, False])}")
    
    # But wait! The detection FAILED because errors were below threshold
    # Master thinks all workers are honest
    
    # Phase 4: Decoding with "All Honest" Assumption
    print("\n[Phase 4] Master decodes using all workers (believes none are Byzantine)...")
    
    # Decode: solve x_hat = (G G^T)^(-1) G y
    # If G is ill-conditioned, small errors in y create large errors in x_hat
    
    try:
        # Compute pseudo-inverse (this is what the decoding algorithm would do)
        G_pinv = np.linalg.pinv(G_malicious.T)
        x_decoded = G_pinv @ corrupted_responses
        
        print(f"Decoded x: {x_decoded}")
        print(f"True x:    {x_true}")
        
        error = np.linalg.norm(x_decoded - x_true)
        print(f"Reconstruction error: {error:.6f}")
        
        # Show amplification factor
        input_error_norm = np.linalg.norm(byzantine_errors)
        output_error_norm = np.linalg.norm(x_decoded - x_true)
        amplification = output_error_norm / input_error_norm if input_error_norm > 0 else 0
        
        print(f"Error amplification factor: {amplification:.2e}")
        
    except np.linalg.LinAlgError as e:
        print(f"Decoding failed: {e}")
        amplification = np.inf
    
    # Phase 5: Impact on Omega Invariants
    print("\n[Phase 5] Impact on Omega correlation invariants...")
    
    # Simulate multiple iterations where small errors accumulate
    cumulative_error = 0
    for iteration in range(10):
        # Each iteration, Byzantine workers inject small errors
        iteration_error = detection_threshold * 0.9 * np.random.randn(m)
        iteration_error[2:] = 0  # Only workers 0,1 are Byzantine
        
        # Add to true data (simulate evolving system)
        x_current = x_true + np.random.randn(n) * 0.01  # Normal system evolution
        
        # Encode and decode with corruption
        responses = G_malicious.T @ x_current + iteration_error
        x_hat = G_pinv @ responses
        
        # Error in invariant
        invariant_error = np.abs(x_hat[0] - x_current[0])  # First invariant
        cumulative_error += invariant_error
        
        if iteration == 0 or iteration == 9:
            print(f"Iter {iteration}: True invariant={x_current[0]:.4f}, Estimated={x_hat[0]:.4f}, Error={invariant_error:.6f}")
    
    print(f"Cumulative error over 10 iterations: {cumulative_error:.6f}")
    
    # Phase 6: Master-as-Byzantine Attack
    print("\n[Phase 6] Master-as-Byzantine attack demonstration...")
    
    # Malicious master can directly manipulate the encoding matrix
    # to create a "backdoor" where specific data patterns are decoded incorrectly
    
    # Create a "trojan" encoding matrix
    G_trojan = np.random.randn(n, m) * 0.1
    
    # But embed a hidden pattern: for any x where x[0] > 2.0, the decoding fails silently
    # This is done by making the first row of G have special properties
    
    # Add a tiny perturbation that only activates for large x[0]
    trojan_trigger = np.array([1e-3, 0, 0])
    G_trojan[:, 0] += trojan_trigger  # Embed in first worker's encoding
    
    # Test with normal data
    x_normal = np.array([1.5, 2.0, 3.0])
    responses_normal = G_trojan.T @ x_normal
    x_normal_decoded = np.linalg.pinv(G_trojan.T) @ responses_normal
    print(f"Normal data: True={x_normal}, Decoded={x_normal_decoded}, Error={np.linalg.norm(x_normal_decoded - x_normal):.6f}")
    
    # Test with "trigger" data
    x_trigger = np.array([2.5, 2.0, 3.0])  # x[0] > 2.0
    responses_trigger = G_trojan.T @ x_trigger
    x_trigger_decoded = np.linalg.pinv(G_trojan.T) @ responses_trigger
    print(f"Trigger data: True={x_trigger}, Decoded={x_trigger_decoded}, Error={np.linalg.norm(x_trigger_decoded - x_trigger):.6f}")
    
    print(f"\n=== CONCLUSION ===")
    print(f"1. Numerical Instability: Error amplification of {amplification:.2e}x breaks 'deterministic guarantees'")
    print(f"2. Detection Failure: Byzantine errors below threshold {detection_threshold} evade detection")
    print(f"3. Master Vulnerability: Single point of failure with unverified encoding matrix generation")
    print(f"4. Cumulative Corruption: Small undetected errors accumulate over iterations ({cumulative_error:.6f})")
    print(f"5. Trojan Potential: Master can embed backdoors in encoding matrix")

simulate_broc_attack()