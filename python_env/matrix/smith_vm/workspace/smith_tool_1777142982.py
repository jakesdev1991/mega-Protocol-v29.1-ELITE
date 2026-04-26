# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

class SalesIdentityManifold:
    """
    Exact copy of the submitted class for validation.
    """
    def __init__(self, dim: int = 8):
        self.dim = dim
        self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_sales: List[complex] = [complex(0.9, 0.1) for _ in range(dim)]
        self.psi_id: List[float] = [0.92, 0.89, 0.95, 0.87, 0.91, 0.93, 0.88, 0.94]
        self.xi_sales: float = 0.95
        self.z_trust: float = 0.35
        self.z_env: float = 0.80
        self.h_super: float = 0.0
        self.cod: float = 0.0
        self.h_dis: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = 0.0

    def compute_superposition_entropy(self) -> float:
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-9: return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def compute_causal_link_density(self) -> float:
        dot = sum(abs(c * i) for c, i in zip(self.psi_sales, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_sales))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c * mag_i < 1e-9: return 0.0
        fidelity = (dot / (mag_c * mag_i)) ** 2
        entropy_penalty = np.exp(-0.5 * self.h_super)      # Lambda = 0.5
        stiffness_penalty = np.exp(-0.5 * self.xi_sales)   # Kappa = 0.5
        env_penalty = np.exp(-0.5 * self.z_env)            # Extra factor not in paper
        return min(1.0, max(0.0, fidelity * entropy_penalty * stiffness_penalty * env_penalty))

    def compute_dissonance_entropy(self) -> float:
        diff = np.abs(np.array(self.psi_sales) - np.array(self.psi_id))
        prob = diff / np.sum(diff)
        h = -sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
        max_h = np.log(len(prob))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def update_stiffness(self, dt_hours: float) -> None:
        gamma = 0.004
        exp_term = np.exp(-gamma * dt_hours)
        self.xi_sales = self.xi_sales * exp_term + self.z_trust * (1 - exp_term)
        self.z_env = self.z_env * exp_term + 0.4 * (1 - exp_term)

    def enforce_smith_invariants(self) -> bool:
        self.h_super = self.compute_superposition_entropy()
        self.cod = self.compute_causal_link_density()
        self.h_dis = self.compute_dissonance_entropy()
        self.phi_N = np.log2(max(self.cod, 0.39))
        R_align = abs(self.xi_sales - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 6
        if self.cod < 0.85: return False
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        if self.xi_sales > self.z_trust + 0.1: return False
        if self.z_env > 0.7: return False
        if self.h_dis > 0.3: return False
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        return True

    def apply(self, dt_hours: float) -> str:
        self.update_stiffness(dt_hours)
        if self.enforce_smith_invariants():
            return "You are not required to decide now. Your uncertainty is the space where value grows."
        else:
            return ""

def validate_random_samples(n_samples=10000):
    violations = []
    for i in range(n_samples):
        # Randomize initial state within plausible bounds
        sim = SalesIdentityManifold(dim=8)
        # Randomize latent state
        sim.psi_latent = [complex(np.random.rand(), np.random.rand()) for _ in range(8)]
        # Randomize sales vector (bias towards close but allow variation)
        sim.psi_sales = [complex(np.random.uniform(0.5,1.0), np.random.uniform(0,0.5)) for _ in range(8)]
        # Randomize parameters
        sim.xi_sales = np.random.uniform(0.0, 1.5)
        sim.z_trust = np.random.uniform(0.0, 1.0)
        sim.z_env = np.random.uniform(0.0, 1.0)
        # Apply a random time step
        dt = np.random.uniform(0, 500)  # up to ~500 hrs
        msg = sim.apply(dt)
        # Compute expected COD from paper formula (without env penalty)
        # Recompute fidelity etc.
        h_super = sim.compute_superposition_entropy()
        dot = sum(abs(c * i) for c, i in zip(sim.psi_sales, sim.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in sim.psi_sales))
        mag_i = np.sqrt(sum(abs(i)**2 for i in sim.psi_id))
        fidelity = (dot / (mag_c * mag_i)) ** 2 if mag_c*mag_i>1e-12 else 0.0
        entropy_penalty = np.exp(-0.5 * h_super)
        stiffness_penalty = np.exp(-0.5 * sim.xi_sales)
        expected_cod = fidelity * entropy_penalty * stiffness_penalty  # paper version
        # Check COD calculation matches code (including env penalty) within tolerance
        if not np.isclose(sim.cod, expected_cod * np.exp(-0.5 * sim.z_env), rtol=1e-6, atol=1e-8):
            violations.append((
                i, "COD mismatch",
                f"code={sim.cod:.6f}, expected={expected_cod*np.exp(-0.5*sim.z_env):.6f}"
            ))
        # If apply returned a message, invariants should all hold
        if msg != "":
            if not (sim.cod >= 0.85):
                violations.append((i, "COD invariant violated when message sent", f"COD={sim.cod}"))
            if not (0.15 <= sim.h_super <= 0.80):
                violations.append((i, "H_super invariant violated", f"H_super={sim.h_super}"))
            if not (sim.xi_sales <= sim.z_trust + 0.1):
                violations.append((i, "Stiffness-Impedance invariant violated",
                                   f"xi={sim.xi_sales}, z_trust+0.1={sim.z_trust+0.1}"))
            if not (sim.z_env <= 0.7):
                violations.append((i, "Environmental Impedance invariant violated", f"z_env={sim.z_env}"))
            if not (sim.h_dis <= 0.3):
                violations.append((i, "Dissonance Cap invariant violated", f"h_dis={sim.h_dis}"))
            if not (sim.phi_Delta < 0.5 * sim.phi_N):
                violations.append((i, "Asymmetry Control invariant violated",
                                   f"phi_Delta={sim.phi_Delta}, 0.5*phi_N={0.5*sim.phi_N}"))
        # If apply returned empty string, at least one invariant must be violated
        else:
            inv1 = sim.cod >= 0.85
            inv2 = 0.15 <= sim.h_super <= 0.80
            inv3 = sim.xi_sales <= sim.z_trust + 0.1
            inv4 = sim.z_env <= 0.7
            inv5 = sim.h_dis <= 0.3
            inv6 = sim.phi_Delta < 0.5 * sim.phi_N
            if all([inv1, inv2, inv3, inv4, inv5, inv6]):
                violations.append((i, "No message sent but all invariants satisfied", ""))
    return violations

if __name__ == "__main__":
    vio = validate_random_samples(5000)
    if vio:
        print(f"Found {len(vio)} violations:")
        for v in vio[:10]:  # show first 10
            print(v)
    else:
        print("All samples passed invariant checks.")
    # Additional check: COD formula consistency
    print("\nChecking COD formula derivation:")
    sim = SalesIdentityManifold()
    # Force known state for deterministic check
    sim.psi_latent = [1+0j]*8
    sim.psi_sales = [1+0j]*8
    sim.psi_id = [1.0]*8
    sim.xi_sales = 0.2
    sim.z_trust = 0.2
    sim.z_env = 0.1
    sim.apply(0)
    # Manual COD per paper
    h = sim.compute_superposition_entropy()
    dot = sum(abs(c*i) for c,i in zip(sim.psi_sales, sim.psi_id))
    mag_c = np.sqrt(sum(abs(c)**2 for c in sim.psi_sales))
    mag_i = np.sqrt(sum(abs(i)**2 for i in sim.psi_id))
    fidelity = (dot/(mag_c*mag_i))**2 if mag_c*mag_i>0 else 0
    expected = fidelity * np.exp(-0.5*h) * np.exp(-0.5*sim.xi_sales)
    print(f"h_super={h:.4f}")
    print(f"Fidelity={fidelity:.6f}")
    print(f"Expected COD (paper)={expected:.6f}")
    print(f"Code COD (with env penalty)={sim.cod:.6f}")
    print(f"Env penalty factor=np.exp(-0.5*z_env)={np.exp(-0.5*sim.z_env):.6f}")
    print(f"Product expected*env_penalty={expected*np.exp(-0.5*sim.z_env):.6f}")
    print("Match?", np.isclose(sim.cod, expected*np.exp(-0.5*sim.z_env)))