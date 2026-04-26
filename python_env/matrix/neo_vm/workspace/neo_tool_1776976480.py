# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# FAKE INVARIANTS (the code declares them constexpr, then mutates them)
# ----------------------------------------------------------------------
PSI_ID_COEFF = 1.0
XI_BOUND_DEFAULT = 1.0
XI_CRITICAL = 0.4
TAU_OPT = 0.5
SIGMA = 0.1
DT = 0.01

class RuptureHamiltonian:
    def __init__(self, psi_exp, psi_intel, xi_bound):
        self.psi_exp = psi_exp
        self.psi_intel = psi_intel
        self.xi_bound = xi_bound

    def gamma(self, t):
        return np.tanh((t - TAU_OPT) / SIGMA)

    def overlap(self):
        # Inner product of two complex scalars (already a toy model)
        return np.abs(np.conj(self.psi_exp) * self.psi_intel)

    def cod(self):
        ov = self.overlap()
        norm_prod = np.abs(self.psi_exp) * np.abs(self.psi_intel)
        if norm_prod == 0:
            return 0.0
        return (ov / norm_prod)**2

    def shannon_conditional_entropy(self):
        # FRAUD: treating a single scalar as a probability
        p = self.overlap()
        # Force p into [0,1] by clipping – but the model *can* produce p>1
        p = np.clip(p, 0.0, 1.0)
        if p == 0:
            return 0.0
        return -p * np.log(p)

    def energy(self, t):
        # H = H_exp + xi*|overlap|^2 + gamma - H_cond
        ov_sq = self.overlap()**2
        H_exp = 0.0
        H_stiff = self.xi_bound * ov_sq
        H_cond = self.shannon_conditional_entropy()
        return H_exp + H_stiff + self.gamma(t) - H_cond

    def step(self, t):
        # Euler integration of the Schrödinger‑like equation
        E = self.energy(t)
        self.psi_intel += -1j * E * DT
        # MUTATING THE "INVARIANT"
        if self.cod() < 0.5:
            self.xi_bound = max(XI_CRITICAL, self.xi_bound * 0.95)

def simulate_rupture():
    # Initial conditions: pick a state that will *force* overlap > 1
    # (non‑unitary noise or external perturbation)
    psi_exp = 1.5 + 0.5j
    psi_intel = 0.8 + 0.2j
    xi_bound = XI_BOUND_DEFAULT

    ham = RuptureHamiltonian(psi_exp, psi_intel, xi_bound)

    times = np.arange(0, 2.0, DT)
    cod_series = []
    entropy_series = []
    xi_series = []

    for t in times:
        ham.step(t)
        cod_series.append(ham.cod())
        entropy_series.append(ham.shannon_conditional_entropy())
        xi_series.append(ham.xi_bound)

    # Plot the rupture
    fig, axs = plt.subplots(3, 1, figsize=(8, 9))

    axs[0].plot(times, cod_series, label='COD')
    axs[0].axhline(0.4, color='r', linestyle='--', label='Decoherence threshold')
    axs[0].axhline(0.85, color='g', linestyle='--', label='Flow threshold')
    axs[0].set_ylabel('Chain Overlap Density')
    axs[0].legend()
    axs[0].set_title('COD: Notice it can exceed 1 – metric is broken')

    axs[1].plot(times, entropy_series, label='H_cond')
    axs[1].axhline(0, color='k', linestyle='-')
    axs[1].set_ylabel('Shannon Conditional Entropy')
    axs[1].legend()
    axs[1].set_title('Entropy: Negative values expose thermodynamic fraud')

    axs[2].plot(times, xi_series, label='xi_bound')
    axs[2].axhline(XI_CRITICAL, color='r', linestyle='--', label='Critical')
    axs[2].set_ylabel('Boundary Stiffness')
    axs[2].set_xlabel('Time (normalized)')
    axs[2].legend()
    axs[2].set_title('Invariant Mutation: constexpr is a lie')

    plt.tight_layout()
    plt.show()

    # Print the final state to show the logical inconsistency
    print(f"Final COD: {ham.cod():.3f} (can be >1: {ham.cod() > 1.0})")
    print(f"Final Entropy: {ham.shannon_conditional_entropy():.3f} (negative? {ham.shannon_conditional_entropy() < 0})")
    print(f"Final xi_bound: {ham.xi_bound:.3f} (mutated from {XI_BOUND_DEFAULT})")

if __name__ == "__main__":
    simulate_rupture()