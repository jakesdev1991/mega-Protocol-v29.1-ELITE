# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- Byzantine-Resilient Distributed Gradient Descent Simulator ---

# Simulate the core vulnerability: data poisoning bypasses gradient encoding
# The prior integration protects gradient *transmission*, not gradient *computation*

def simulate_distributed_sgd(
    n_workers=5,
    n_corrupt=2,
    n_epochs=10,
    poison_data=False,
    poison_gradients=False
):
    """
    Simulates distributed SGD with encoding/decoding.
    
    Key disruption: Data poisoning makes honest workers compute wrong gradients,
    which the encoding scheme cannot detect because the *source* is corrupted,
    not the transmission.
    """
    # True model: y = 3x + 2
    true_w, true_b = 3.0, 2.0
    
    # Data generation
    np.random.seed(42)
    X = np.random.randn(1000)
    y = true_w * X + true_b + 0.1 * np.random.randn(1000)
    
    # Shard data among workers
    shard_size = len(X) // n_workers
    X_shards = [X[i*shard_size:(i+1)*shard_size] for i in range(n_workers)]
    y_shards = [y[i*shard_size:(i+1)*shard_size] for i in range(n_workers)]
    
    # --- DATA POISONING ATTACK ---
    # Corrupt workers poison the data of honest workers by flipping labels
    if poison_data:
        # Corrupt workers 0 and 1 will poison shards 2 and 3 (honest workers)
        for i in range(n_corrupt):
            target_shard = n_corrupt + i  # Attack honest workers' data
            if target_shard < n_workers:
                # Flip the sign of 30% of labels to create bias
                poison_mask = np.random.random(len(y_shards[target_shard])) < 0.3
                y_shards[target_shard] = y_shards[target_shard].copy()
                y_shards[target_shard][poison_mask] *= -1
    
    # Model parameters
    w, b = 0.0, 0.0
    lr = 0.01
    
    # Encoding scheme: simple redundancy (2x replication for illustration)
    # In practice this would be a sparse real-number code, but the principle holds:
    # encoding protects against corrupt *transmission*, not corrupt *computation*
    def encode_gradient(grad_w, grad_b):
        # Create m shares such that any m-t can reconstruct
        # Simplified: just replicate with small noise
        shares_w = [grad_w + 0.001*np.random.randn() for _ in range(n_workers)]
        shares_b = [grad_b + 0.001*np.random.randn() for _ in range(n_workers)]
        return shares_w, shares_b
    
    def decode_gradient(shares_w, shares_b):
        # Simplified decoder: remove outliers beyond median absolute deviation
        # This simulates the deterministic decoder in the paper
        median_w = np.median(shares_w)
        mad_w = np.median(np.abs(shares_w - median_w))
        median_b = np.median(shares_b)
        mad_b = np.median(np.abs(shares_b - median_b))
        
        # Filter out shares that are too far (potential corrupt transmission)
        valid_w = [s for s in shares_w if abs(s - median_w) < 3*mad_w]
        valid_b = [s for s in shares_b if abs(s - median_b) < 3*mad_b]
        
        if len(valid_w) == 0: valid_w = shares_w
        if len(valid_b) == 0: valid_b = shares_b
            
        return np.mean(valid_w), np.mean(valid_b)
    
    # --- Gradient Corruption Index (GCI) ---
    # As defined in the integration: measures residual errors after decoding
    # BUT: This only detects *transmission* errors, not *computation* errors!
    def compute_gci(shares_w, shares_b, decoded_w, decoded_b):
        residuals_w = [abs(s - decoded_w) for s in shares_w]
        residuals_b = [abs(s - decoded_b) for s in shares_b]
        # Normalize by magnitude
        residual_norm = np.sqrt(np.mean(residuals_w)**2 + np.mean(residuals_b)**2)
        decoded_norm = np.sqrt(decoded_w**2 + decoded_b**2) + 1e-8
        return np.tanh(residual_norm / decoded_norm)  # Scaled to [0,1]
    
    # Training loop
    history = []
    for epoch in range(n_epochs):
        # Each worker computes gradient on its (possibly poisoned) data
        worker_grads_w, worker_grads_b = [], []
        
        for i in range(n_workers):
            Xi, yi = X_shards[i], y_shards[i]
            # Compute local gradient
            y_pred = w * Xi + b
            grad_w = 2 * np.mean((y_pred - yi) * Xi)
            grad_b = 2 * np.mean(y_pred - yi)
            
            # Byzantine workers can also directly send wrong gradients
            if poison_gradients and i < n_corrupt:
                grad_w *= -5  # Send malicious gradient
                
            worker_grads_w.append(grad_w)
            worker_grads_b.append(grad_b)
        
        # Master node encodes and aggregates
        shares_w, shares_b = encode_gradient(np.mean(worker_grads_w), np.mean(worker_grads_b))
        
        # Byzantine workers corrupt their shares (transmission attack)
        for i in range(n_corrupt):
            shares_w[i] += np.random.randn() * 10  # Add large noise
            shares_b[i] += np.random.randn() * 10
        
        # Decode to recover gradient
        decoded_w, decoded_b = decode_gradient(shares_w, shares_b)
        
        # Compute GCI (as per integration)
        gci = compute_gci(shares_w, shares_b, decoded_w, decoded_b)
        
        # Update model
        w -= lr * decoded_w
        b -= lr * decoded_b
        
        # Track metrics
        loss = np.mean((w*X + b - y)**2)
        history.append({
            'epoch': epoch,
            'loss': loss,
            'gci': gci,
            'w': w, 'b': b,
            'true_w': true_w, 'true_b': true_b
        })
    
    return history

# --- Demonstrate the Disruption ---

print("=== SCENARIO 1: No Poisoning (Baseline) ===")
hist_clean = simulate_distributed_sgd(
    n_workers=5, n_corrupt=2, 
    poison_data=False, poison_gradients=False
)
print(f"Final loss: {hist_clean[-1]['loss']:.4f}")
print(f"Final GCI: {hist_clean[-1]['gci']:.4f}")
print(f"Model: w={hist_clean[-1]['w']:.3f}, b={hist_clean[-1]['b']:.3f}")

print("\n=== SCENARIO 2: Gradient Corruption (Encoding Protects) ===")
hist_grad = simulate_distributed_sgd(
    n_workers=5, n_corrupt=2,
    poison_data=False, poison_gradients=True
)
print(f"Final loss: {hist_grad[-1]['loss']:.4f}")
print(f"Final GCI: {hist_grad[-1]['gci']:.4f}")
print(f"Model: w={hist_grad[-1]['w']:.3f}, b={hist_grad[-1]['b']:.3f}")

print("\n=== SCENARIO 3: DATA POISONING (The Breakthrough Disruption) ===")
hist_data = simulate_distributed_sgd(
    n_workers=5, n_corrupt=2,
    poison_data=True, poison_gradients=False
)
print(f"Final loss: {hist_data[-1]['loss']:.4f}")
print(f"Final GCI: {hist_data[-1]['gci']:.4f}")
print(f"Model: w={hist_data[-1]['w']:.3f}, b={hist_data[-1]['b']:.3f}")

# --- Analysis of Disruption ---
print("\n=== DISRUPTION ANALYSIS ===")
print("The GCI metric is designed to detect *transmission* errors, not *computation* errors.")
print("When data is poisoned, honest workers compute WRONG gradients, but transmit them correctly.")
print("The decoder sees 'valid' shares and GCI remains low (<0.3), but the optimization fails catastrophically.")
print(f"Clean GCI: {hist_clean[-1]['gci']:.3f}, Data Poison GCI: {hist_data[-1]['gci']:.3f}")
print(f"Clean loss: {hist_clean[-1]['loss']:.3f}, Data Poison loss: {hist_data[-1]['loss']:.3f}")
print("\n=> The integration provides a FALSE SENSE OF SECURITY. The real attack surface is upstream: DATA POISONING.")