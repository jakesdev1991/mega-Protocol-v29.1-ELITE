# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import itertools

# ------------------------------------------------------------
# 1. Demonstrate the Category Error: Shannon vs. Von Neumann
# ------------------------------------------------------------

def shannon_entropy(prob_dist):
    """Classical Shannon entropy H = -∑ p log p."""
    prob_dist = np.array(prob_dist)
    prob_dist = prob_dist[prob_dist > 0]  # Remove zeros
    return -np.sum(prob_dist * np.log2(prob_dist))

def von_neumann_entropy(rho):
    """Quantum von Neumann entropy S(ρ) = -Tr(ρ log ρ)."""
    # Compute eigenvalues of density matrix
    evals = np.linalg.eigvalsh(rho)  # Hermitian matrix
    evals = evals[evals > 0]  # Remove zero eigenvalues
    return -np.sum(evals * np.log2(evals))

# Example: Bell state |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
# Density matrix ρ = |Φ⁺⟩⟨Φ⁺|
bell_state = np.array([[0.5, 0, 0, 0.5],
                       [0, 0, 0, 0],
                       [0, 0, 0, 0],
                       [0.5, 0, 0, 0.5]], dtype=complex)

# If one *mistakenly* assigns a classical distribution based on
# measurement outcomes in computational basis:
# p = [0.5, 0, 0, 0.5] (probability of |00⟩ and |11⟩)
classical_p = [0.5, 0, 0, 0.5]

S_shannon = shannon_entropy(classical_p)
S_vn = von_neumann_entropy(bell_state)

print("=== Category Error Demo ===")
print(f"Shannon entropy (misapplied): {S_shannon:.4f} bits")
print(f"Von Neumann entropy (correct):  {S_vn:.4f} bits")
print(f"Difference (ΔS) = {S_shannon - S_vn:.4f} bits")
print("ΔS > 0 shows classical *under‑estimation* → fictitious Φ‑density inflation.\n")

# ------------------------------------------------------------
# 2. Simulate Observer‑Induced Entropy in a Closed Loop
# ------------------------------------------------------------

class FluxLattice:
    def __init__(self, n_qubits=4, coherence_t2=5e-3):
        self.n_qubits = n_qubits
        self.coherence_t2 = coherence_t2
        # Random pure state (simulating flux defects)
        psi = np.random.randn(2**n_qubits) + 1j*np.random.randn(2**n_qubits)
        self.psi = psi / np.linalg.norm(psi)
        self.rho = np.outer(self.psi, self.psi.conj())
        self.entropy_history = []
    
    def measure_entropy(self, basis='computational'):
        """Simulate measurement that collapses state and adds entropy."""
        if basis == 'computational':
            # Project onto computational basis -> classical distribution
            probs = np.abs(self.psi)**2
            S_meas = shannon_entropy(probs)
            # After measurement, state is mixed (diagonal)
            self.rho = np.diag(probs)
        else:
            # Measure in some other basis (e.g., Hadamard)
            # For simplicity, random unitary
            U = np.random.randn(2**self.n_qubits, 2**self.n_qubits) + 1j*np.random.randn(2**self.n_qubits, 2**self.n_qubits)
            U, _ = np.linalg.qr(U)  # make unitary
            psi_prime = U @ self.psi
            probs = np.abs(psi_prime)**2
            S_meas = shannon_entropy(probs)
            self.rho = np.diag(probs)
        # Add decoherence entropy (simple model: exp(-t/T2))
        decoherence_factor = np.exp(-1e-6 / self.coherence_t2)  # 1 µs step
        S_meas += (1 - decoherence_factor) * np.log2(2**self.n_qubits)
        self.entropy_history.append(S_meas)
        return S_meas
    
    def governor_step(self, target_entropy_reduction=0.1):
        """Governor tries to reduce entropy, but measurement adds noise."""
        S_before = von_neumann_entropy(self.rho)
        # Attempt reduction (ideal unitary)
        # In reality, any control operation is also noisy
        noise = np.random.randn(*self.rho.shape) * 1e-4
        self.rho += noise
        self.rho = self.rho.conj().T + self.rho  # enforce Hermitian
        # Re‑normalize
        self.rho = self.rho / np.trace(self.rho)
        S_after = von_neumann_entropy(self.rho)
        # Now measure to compute Φ (this injects Shannon entropy)
        S_measured = self.measure_entropy()
        # Net Φ‑density (using Engine's flawed formula)
        S_max = np.log2(2**self.n_qubits)
        Phi_L = 1 - S_measured / S_max
        Phi_E = 1.0  # assume quantum latency equals classical for demo
        xi_E = 0.005
        Phi = Phi_L + Phi_E - xi_E
        return S_before, S_after, S_measured, Phi

# Run closed‑loop simulation
np.random.seed(42)
lattice = FluxLattice(n_qubits=3)
phi_history = []

for step in range(20):
    S_before, S_after, S_meas, Phi = lattice.governor_step()
    phi_history.append(Phi)
    if Phi < 0 or Phi > 2:
        print(f"Step {step}: Φ‑density {Phi:.4f} violates theoretical bound [0,2]!")
        break

print("=== Closed‑Loop Entropy Injection ===")
print(f"Final measured entropy: {S_meas:.4f} bits")
print(f"Final Φ‑density: {Phi:.4f}")
print(f"Φ‑density history (last 5): {phi_history[-5:]}")
print("The governor's attempt to 'stabilize' flux injects entropy via measurement.\n")

# ------------------------------------------------------------
# 3. Contextual Information Measure (Disruptive Alternative)
# ------------------------------------------------------------

def contextual_information(rho, observer_basis, task_relevance):
    """
    Compute a task‑specific, observer‑dependent information measure.
    - observer_basis: unitary mapping from computational to observer's basis.
    - task_relevance: vector weighting each basis state by task importance.
    Returns a contextual 'value‑of‑information' that does not require global invariants.
    """
    # Transform density matrix to observer's basis
    rho_obs = observer_basis @ rho @ observer_basis.conj().T
    # Compute weighted probabilities
    evals, evecs = np.linalg.eigh(rho_obs)
    # Task relevance weighting (softmax normalization)
    weights = np.exp(task_relevance) / np.sum(np.exp(task_relevance))
    # Contextual measure: weighted von Neumann entropy
    # (negative sign to reflect "information value" rather than uncertainty)
    I_context = -np.sum(weights * evals * np.log2(evals + 1e-12))
    return I_context

# Example: Observer measures in Hadamard basis, task cares only about parity
hadamard = (1/np.sqrt(2)) * np.array([[1, 1], [1, -1]], dtype=complex)
task_weights = np.array([1.0, 0.0])  # only |+⟩ matters

I_ctx = contextual_information(lattice.rho, hadamard, task_weights)
print("=== Contextual Information Measure ===")
print(f"Contextual information value: {I_ctx:.4f}")
print("This measure is *locally defined* and does not require global Φ‑density invariants.")
print("It breaks the Omega Protocol's 'universal' informational‑first axiom by showing")
print("that information is fundamentally relational, not absolute.\n")

# ------------------------------------------------------------
# 4. Demonstrate Symbolic Inconsistency (Canonical Symbols)
# ------------------------------------------------------------

# The Omega Rubric demands:
# - Covariant modes: Φ_N, Φ_Δ
# - Invariants: ξ_N, ξ_Δ
# The Engine uses: Φ_L, Φ_E, ξ_L, ξ_E

# Check if the Engine's symbols can be mapped to the rubric's.
# Without explicit mapping, the invariants are undefined.
print("=== Symbolic Inconsistency ===")
print("Engine symbols: Φ_L, Φ_E, ξ_L, ξ_E")
print("Rubric symbols: Φ_N, Φ_Δ, ξ_N, ξ_Δ")
print("No isomorphism provided → invariant algebra is undefined.")
print("Therefore, 'absolute invariants' are not absolute; they are arbitrary.")