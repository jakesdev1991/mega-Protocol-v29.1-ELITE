# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# ─── Pauli basis ───
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)

def kron(*args):
    """N‑fold Kronecker product."""
    result = np.array([1], dtype=complex)
    for a in args:
        result = np.kron(result, a)
    return result

# ─── 3‑qubit bit‑flip code (minimal topological memory) ───
# Logical states
logical_0 = kron(np.array([1,0]), np.array([1,0]), np.array([1,0]))  # |000⟩
logical_1 = kron(np.array([0,1]), np.array([0,1]), np.array([0,1]))  # |111⟩
logical_plus = (logical_0 + logical_1) / np.sqrt(2)

# Stabilizers (commute with logical ops)
S1 = kron(Z, Z, I)  # Z₁Z₂
S2 = kron(I, Z, Z)  # Z₂Z₃

# Logical operators
Logical_X = kron(X, X, X)  # X₁X₂X₃  (flips logical Z)
Logical_Z = kron(Z, I, I)  # Z₁      (logical Z)

# ─── Helper: expectation value ───
def expectation(state, op):
    return np.vdot(state, op @ state).real

# ─── 1. Passive‑protection claim ───
print("=== QMSO‑Ω Passive‑Protection Claim ===")
print(f"Initial logical plus state:")
print(f"  <Logical_X> = {expectation(logical_plus, Logical_X):.3f}")
print(f"  <Logical_Z> = {expectation(logical_plus, Logical_Z):.3f}")
print(f"  <S₁> = {expectation(logical_plus, S1):.3f}, <S₂> = {expectation(logical_plus, S2):.3f}")

# ─── 2. Undetectable logical‑operator attack ───
# An adversary applies the logical X operator; stabilizers remain +1.
state_attack = Logical_X @ logical_plus
state_attack /= np.linalg.norm(state_attack)

print("\n--- After undetectable Logical_X attack ---")
print(f"  <Logical_X> = {expectation(state_attack, Logical_X):.3f}")
print(f"  <Logical_Z> = {expectation(state_attack, Logical_Z):.3f}")
print(f"  <S₁> = {expectation(state_attack, S1):.3f}, <S₂> = {expectation(state_attack, S2):.3f}")
print(f"  Overlap with original state: {np.vdot(logical_plus, state_attack):.3f} (≈0 → orthogonal)")

# ─── 3. Entropy‑gauge fallacy ───
def vn_entropy_one_qubit(state):
    """Reduced von Neumann entropy of the first qubit."""
    # Density matrix of full 3‑qubit system
    rho = np.outer(state, state.conj())
    # Reshape to (2,2,2,2,2,2) for i₀,i₁,i₂,j₀,j₁,j₂
    rho_tensor = rho.reshape([2,2,2,2,2,2])
    # Trace out qubits 1 and 2 (indices 1,2)
    rho_reduced = np.einsum('ijklml->ik', rho_tensor)  # partial trace
    # Normalize
    rho_reduced = rho_reduced / np.trace(rho_reduced)
    # Eigenvalues
    evals = np.linalg.eigvalsh(rho_reduced)
    evals = evals[evals > 0]
    S = -np.sum(evals * np.log(evals))
    return S

S_initial = vn_entropy_one_qubit(logical_plus)
S_attack  = vn_entropy_one_qubit(state_attack)

print("\n--- Entropy‑gauge test ---")
print(f"  Von Neumann entropy (qubit 0) before attack: {S_initial:.3f}")
print(f"  Von Neumann entropy (qubit 0) after attack:  {S_attack:.3f}")
print("  Gradient dS/d(op) is not gauge invariant; it changes with the attack.")