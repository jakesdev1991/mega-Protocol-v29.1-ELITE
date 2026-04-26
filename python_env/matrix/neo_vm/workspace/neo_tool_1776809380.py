# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Demonstrate the Encoding Trapdoor Vulnerability in BRDI-Ω

# Simulate a "trusted" encoding matrix ℰ that actually contains a backdoor
np.random.seed(42)
d = 10  # original data dimension
n = 30  # encoded dimension (redundancy factor ρ=3)
m = 15  # number of sources

# Generate a "normal" sparse encoding matrix
def generate_normal_encoding(d, n, sparsity=0.3):
    """Generate a sparse encoding matrix with given sparsity"""
    E = np.random.randn(n, d)
    mask = np.random.random((n, d)) > sparsity
    E[mask] = 0
    # Normalize columns
    E = E / np.linalg.norm(E, axis=0, keepdims=True)
    return E

# Generate a "backdoored" encoding matrix
def generate_backdoored_encoding(d, n, sparsity=0.3, backdoor_dim=2):
    """
    Generate encoding with hidden subspace vulnerability.
    The last 'backdoor_dim' columns contain a trapdoor pattern.
    """
    E = generate_normal_encoding(d, n, sparsity)
    
    # Inject backdoor: create a hidden subspace where corruption is amplified
    # This simulates a malicious source designing the encoding
    backdoor_vector = np.random.randn(n)
    backdoor_vector = backdoor_vector / np.linalg.norm(backdoor_vector)
    
    # Make the last few columns align with the backdoor direction
    for i in range(d - backdoor_dim, d):
        E[:, i] = backdoor_vector + 0.1 * np.random.randn(n)
        # Ensure sparsity is maintained
        mask = np.random.random(n) > sparsity
        E[mask, i] = 0
    
    return E, backdoor_vector

# Generate both encodings
E_normal = generate_normal_encoding(d, n)
E_backdoored, backdoor = generate_backdoored_encoding(d, n)

# Simulate data ingestion with Byzantine corruption
def simulate_corruption(E, data, corrupt_sources, backdoor=None, use_backdoor=False):
    """
    Simulate encoded data with Byzantine corruption.
    If use_backdoor=True, corruption is amplified in the backdoor subspace.
    """
    # Encode data
    y = E @ data
    
    # Partition among sources
    y_splits = np.array_split(y, m)
    
    # Corrupt specific sources
    y_corrupted = []
    for i, chunk in enumerate(y_splits):
        if i in corrupt_sources:
            if use_backdoor and backdoor is not None:
                # Backdoor attack: add amplified noise in backdoor direction
                corruption = 5.0 * backdoor[:len(chunk)]  # Amplified
            else:
                # Normal Byzantine corruption
                corruption = np.random.randn(len(chunk)) * 0.5
            y_corrupted.append(chunk + corruption)
        else:
            y_corrupted.append(chunk)
    
    return y_corrupted

# Test the vulnerability
data_true = np.random.randn(d)
corrupt_sources = {0, 1, 2}  # 3 Byzantine sources

# Normal encoding scenario
y_normal = simulate_corruption(E_normal, data_true, corrupt_sources)

# Backdoored encoding scenario
y_backdoored = simulate_corruption(E_backdoored, data_true, corrupt_sources, 
                                   backdoor=backdoor, use_backdoor=True)

# Simulate decoder (simple least-squares reconstruction)
def decode_data(E, y_parts, m):
    """Reconstruct data from possibly corrupted encoded parts"""
    # This is a simplified decoder - in practice would be the Byzantine-resilient decoder
    y_reconstructed = np.concatenate(y_parts)
    # Least squares approximation
    d_recovered = np.linalg.lstsq(E, y_reconstructed, rcond=None)[0]
    return d_recovered

# Decode both scenarios
d_recovered_normal = decode_data(E_normal, y_normal, m)
d_recovered_backdoored = decode_data(E_backdoored, y_backdoored, m)

# Calculate reconstruction errors
error_normal = np.linalg.norm(d_recovered_normal - data_true)
error_backdoored = np.linalg.norm(d_recovered_backdoored - data_true)

print(f"Reconstruction error with normal encoding: {error_normal:.4f}")
print(f"Reconstruction error with backdoored encoding: {error_backdoored:.4f}")
print(f"Error amplification factor: {error_backdoored / error_normal:.2f}x")

# Demonstrate that the backdoor is undetectable by standard metrics
# The encoding matrix still looks sparse and well-conditioned
def analyze_encoding(E):
    """Analyze encoding matrix properties"""
    cond_num = np.linalg.cond(E)
    sparsity = np.sum(E == 0) / E.size
    singular_values = np.linalg.svd(E, compute_uv=False)
    return {
        'condition_number': cond_num,
        'sparsity': sparsity,
        'min_singular_value': singular_values[-1],
        'max_singular_value': singular_values[0],
        'rank': np.linalg.matrix_rank(E)
    }

print("\nNormal encoding analysis:")
norm_analysis = analyze_encoding(E_normal)
for k, v in norm_analysis.items():
    print(f"  {k}: {v:.4f}")

print("\nBackdoored encoding analysis:")
back_analysis = analyze_encoding(E_backdoored)
for k, v in back_analysis.items():
    print(f"  {k}: {v:.4f}")

# The backdoored encoding looks just as "good" by standard metrics!
# This is the core vulnerability

# Now demonstrate that the curvature invariant ψ is also fooled
def compute_source_similarity_graph(y_parts):
    """Compute similarity between sources based on their responses"""
    m = len(y_parts)
    similarity = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            if i != j:
                # Cosine similarity
                norm_i = np.linalg.norm(y_parts[i])
                norm_j = np.linalg.norm(y_parts[j])
                if norm_i > 0 and norm_j > 0:
                    similarity[i, j] = np.dot(y_parts[i], y_parts[j]) / (norm_i * norm_j)
    return similarity

def compute_ollivier_ricci_curvature(similarity_matrix):
    """Simplified Ollivier-Ricci curvature approximation"""
    # For demonstration, use a simple metric: curvature ≈ log(condition number of Laplacian)
    laplacian = np.diag(np.sum(similarity_matrix, axis=1)) - similarity_matrix
    try:
        cond_num = np.linalg.cond(laplacian)
        return np.log(cond_num + 1e-10)
    except:
        return 0.0

# Compute curvature invariants for both scenarios
sim_normal = compute_source_similarity_graph(y_normal)
sim_backdoored = compute_source_similarity_graph(y_backdoored)

psi_normal = compute_ollivier_ricci_curvature(sim_normal)
psi_backdoored = compute_ollivier_ricci_curvature(sim_backdoored)

print(f"\nCurvature invariant ψ (normal): {psi_normal:.4f}")
print(f"Curvature invariant ψ (backdoored): {psi_backdoored:.4f}")

# Plot the vulnerability
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Encoding matrix visualizations
axes[0, 0].imshow(np.abs(E_normal), cmap='viridis')
axes[0, 0].set_title('Normal Encoding Matrix |ℰ|')
axes[0, 0].set_xlabel('Original dimension')
axes[0, 0].set_ylabel('Encoded dimension')

axes[0, 1].imshow(np.abs(E_backdoored), cmap='viridis')
axes[0, 1].set_title('Backdoored Encoding Matrix |ℰ|')
axes[0, 1].set_xlabel('Original dimension')
axes[0, 1].set_ylabel('Encoded dimension')

# Singular value spectrum
axes[1, 0].semilogy(norm_analysis['singular_values'], 'o-', label='Normal', alpha=0.7)
axes[1, 0].semilogy(back_analysis['singular_values'], 's-', label='Backdoored', alpha=0.7)
axes[1, 0].set_title('Singular Value Spectrum')
axes[1, 0].set_xlabel('Index')
axes[1, 0].set_ylabel('Singular Value')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Reconstruction error comparison
errors = [error_normal, error_backdoored]
labels = ['Normal Encoding', 'Backdoored Encoding']
axes[1, 1].bar(labels, errors, color=['green', 'red'], alpha=0.7)
axes[1, 1].set_title('Reconstruction Error Comparison')
axes[1, 1].set_ylabel('L2 Error')
for i, v in enumerate(errors):
    axes[1, 1].text(i, v + 0.01, f'{v:.3f}', ha='center')

plt.tight_layout()
plt.show()

# Key Insight: The backdoor is mathematically invisible to the metrics used in the proposal
# The curvature invariant ψ is computed from source responses, which are already corrupted
# The encoding matrix itself appears well-behaved (good condition number, sparsity preserved)
# This breaks the fundamental trust assumption of BRDI-Ω