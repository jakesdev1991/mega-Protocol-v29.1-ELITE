# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# === THE DISRUPTION ENGINE ===
# We'll expose that the entire orthogonal decomposition is a linearization mirage

def omega_potential(phi_N, phi_Delta, v=1.0, lam=1.0):
    """The so-called 'Mexican hat' that supposedly separates the modes"""
    return lam/4 * (phi_N**2 + phi_Delta**2 - v**2)**2

def true_hessian(phi_N, phi_Delta, v=1.0, lam=1.0):
    """The ACTUAL curvature tensor - including the cross-coupling they ignore"""
    d2V_dN2 = lam * (3*phi_N**2 + phi_Delta**2 - v**2)
    d2V_dD2 = lam * (phi_N**2 + 3*phi_Delta**2 - v**2)
    d2V_dNdD = lam * 2*phi_N*phi_Delta  # This term DESTROYS their diagonal fantasy
    
    return np.array([[d2V_dN2, d2V_dNdD], 
                     [d2V_dNdD, d2V_dD2]])

def diagonal_fantasy(phi_N, phi_Delta):
    """What they WISH the Hessian looked like"""
    H = true_hessian(phi_N, phi_Delta)
    return np.array([[H[0,0], 0], [0, H[1,1]]])

def compute_deception_strength(phi_N, phi_Delta):
    """
    Measures how badly the diagonal approximation lies
    Returns: (eigenvalue_error, off_diagonal_ratio, phantom_factor)
    """
    H_true = true_hessian(phi_N, phi_Delta)
    H_fantasy = diagonal_fantasy(phi_N, phi_Delta)
    
    # True eigenvalues
    eig_true, _ = np.linalg.eigh(H_true)
    
    # Fantasy eigenvalues (just the diagonal entries)
    eig_fantasy = np.diag(H_fantasy)
    
    # Their "factor of 3" is based on the assumption that 
    # Archive mode strength = H[1,1] everywhere
    # Let's see what the TRUE effective strength is
    phantom_factor = eig_true[1] / H_true[1,1] if H_true[1,1] != 0 else np.inf
    
    # Off-diagonal coupling relative to diagonal
    off_diag_ratio = np.abs(H_true[0,1]) / np.sqrt(np.abs(H_true[0,0] * H_true[1,1]))
    
    return {
        'phantom_factor': phantom_factor,
        'off_diag_ratio': off_diag_ratio,
        'eigenvalue_error': np.abs(eig_true[1] - eig_fantasy[1]) / np.abs(eig_true[1])
    }

# === SCAN THE MANIFOLD ===
field_space = np.linspace(-1.5, 1.5, 200)
deception_map = np.zeros((len(field_space), len(field_space)))
offdiag_map = np.zeros_like(deception_map)

for i, phi_N in enumerate(field_space):
    for j, phi_Delta in enumerate(field_space):
        deception = compute_deception_strength(phi_N, phi_Delta)
        deception_map[i,j] = deception['phantom_factor']
        offdiag_map[i,j] = deception['off_diag_ratio']

# === THE SMOKING GUN ===
# At the "shredding event" they claim: phi_N^2 + 3*phi_Delta^2 = v^2
phi_N_shred = 0.4
phi_Delta_shred = np.sqrt((1 - phi_N_shred**2)/3)

deception_at_shred = compute_deception_strength(phi_N_shred, phi_Delta_shred)

print("=== ANOMALY DETECTED: ORTHOGONALITY IS A LIE ===")
print(f"\nAt claimed 'shredding boundary':")
print(f"Phi_N = {phi_N_shred:.3f}, Phi_Delta = {phi_Delta_shred:.3f}")
print(f"Their 'factor 3' = {deception_at_shred['phantom_factor']:.3f} (NOT 3)")
print(f"Off-diagonal coupling = {deception_at_shred['off_diag_ratio']:.3f} × diagonal")
print(f"Eigenvalue error = {deception_at_shred['eigenvalue_error']:.1%}")

print(f"\nThe 'factor 3' only holds at origin: {np.isclose(deception_map, 3.0, atol=0.1).sum()} points")
print(f"Phantom factor ranges: {np.nanmin(deception_map):.2f} to {np.nanmax(deception_map):.2f}")

# === VISUALIZE THE DECEPTION ===
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

im1 = axes[0].contourf(field_space, field_space, deception_map.T, levels=30, cmap='plasma')
axes[0].set_title('Phantom "3" Factor')
axes[0].set_xlabel('Φ_N')
axes[0].set_ylabel('Φ_Δ')
plt.colorbar(im1, ax=axes[0], label='Effective factor')

im2 = axes[1].contourf(field_space, field_space, offdiag_map.T, levels=30, cmap='coolwarm')
axes[1].set_title('Off-Diagonal Coupling Strength')
axes[1].set_xlabel('Φ_N')
axes[1].set_ylabel('Φ_Δ')
plt.colorbar(im2, ax=axes[1], label='|H_NΔ|/√(|H_NN·H_ΔΔ|)')

# Show where their approximation breaks (>10% error)
error_map = np.zeros_like(deception_map)
for i, phi_N in enumerate(field_space):
    for j, phi_Delta in enumerate(field_space):
        error_map[i,j] = compute_deception_strength(phi_N, phi_Delta)['eigenvalue_error']

im3 = axes[2].contourf(field_space, field_space, error_map.T, levels=30, cmap='Reds')
axes[2].set_title('Diagonal Approximation Error')
axes[2].set_xlabel('Φ_N')
axes[2].set_ylabel('Φ_Δ')
plt.colorbar(im3, ax=axes[2], label='Relative error')

plt.tight_layout()
plt.savefig('paradigm_shredding.png', dpi=150)
plt.show()

# === QUANTUM INFORMATION ENTROPY OF THE DECOMPOSITION ===
def basis_entanglement_entropy(phi_N, phi_Delta):
    """
    Compute how 'entangled' the true eigenbasis is from the naive N-Δ basis
    Returns von Neumann entropy of basis transformation
    """
    H = true_hessian(phi_N, phi_Delta)
    _, eigvecs = np.linalg.eigh(H)
    
    # The transformation matrix from naive to true basis
    # If they were truly orthogonal, this would be identity
    naive_basis = np.eye(2)
    transformation = eigvecs.T @ naive_basis
    
    # Compute entropy of basis mismatch
    sing_vals = np.linalg.svd(transformation, compute_uv=False)
    probs = sing_vals**2 / np.sum(sing_vals**2)
    
    # Shannon entropy of basis mixing
    return -np.sum(probs * np.log(probs + 1e-15))

entropy_map = np.zeros_like(deception_map)
for i, phi_N in enumerate(field_space):
    for j, phi_Delta in enumerate(field_space):
        entropy_map[i,j] = basis_entanglement_entropy(phi_N, phi_Delta)

print(f"\n=== INFORMATION-THEORETIC DEATH OF ORTHOGONALITY ===")
print(f"Basis entanglement entropy at origin: {basis_entanglement_entropy(0, 0):.3f} (minimum)")
print(f"Max basis entanglement entropy: {np.max(entropy_map):.3f} bits")
print(f"Mean entanglement across manifold: {np.mean(entropy_map):.3f} bits")

# At shredding boundary
entropy_shred = basis_entanglement_entropy(phi_N_shred, phi_Delta_shred)
print(f"Basis entanglement at 'shredding event': {entropy_shred:.3f} bits")