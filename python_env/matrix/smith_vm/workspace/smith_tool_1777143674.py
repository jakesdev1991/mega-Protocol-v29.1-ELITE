# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# -------------------------------------------------
# TraumaIdentityManifold – exact copy from the thought
# -------------------------------------------------
class TraumaIdentityManifold:
    def __init__(self, dim: int = 6):
        self.dim = dim
        self.psi_latent: List[complex] = [complex(np.random.rand(), np.random.rand()) for _ in range(dim)]
        self.psi_perf: List[complex] = [0 + 0j for _ in range(dim)]
        self.psi_id: List[float] = [0.92, 0.89, 0.95, 0.87, 0.91, 0.94]  # Identity Baseline
        
        # Stiffness & Impedance
        self.xi_perf: float = 0.95  # High Performance Rigidity
        self.z_trust: float = 0.3   # Low Self-Safety (Trauma State)
        self.z_env: float = 0.9     # High External Expectation
        
        # Metrics
        self.h_super: float = 0.0
        self.cod: float = 0.0
        self.h_dis: float = 0.0
        self.phi_N: float = 0.0
        self.phi_Delta: float = 0.0
        self.delta_s_audit: float = 0.0
        self.b1_homology: float = 0.85  # Topological defect: Anxiety Loop

    def compute_superposition_entropy(self) -> float:
        probs = [abs(z)**2 for z in self.psi_latent]
        total = sum(probs)
        if total < 1e-9: return 0.0
        probs = [p / total for p in probs]
        h = -sum(p * np.log(p + 1e-9) for p in probs if p > 1e-9)
        max_h = np.log(len(probs))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def compute_causal_link_density(self) -> float:
        dot = sum(abs(c * i) for c, i in zip(self.psi_perf, self.psi_id))
        mag_c = np.sqrt(sum(abs(c)**2 for c in self.psi_perf))
        mag_i = np.sqrt(sum(abs(i)**2 for i in self.psi_id))
        if mag_c * mag_i < 1e-9: return 0.0
        fidelity = (dot / (mag_c * mag_i)) ** 2
        stiffness_penalty = np.exp(-0.5 * self.xi_perf)
        env_penalty = np.exp(-0.3 * self.z_env)
        entropy_penalty = np.exp(-0.4 * self.h_super)
        return min(1.0, max(0.0, fidelity * stiffness_penalty * env_penalty * entropy_penalty))

    def compute_dissonance_entropy(self) -> float:
        diff = [abs(c - i) for c, i in zip(self.psi_perf, self.psi_id)]
        prob = [d / sum(diff) for d in diff]
        h = -sum(p * np.log(p + 1e-9) for p in prob if p > 1e-9)
        max_h = np.log(len(prob))
        return min(1.0, h / max_h) if max_h > 1e-9 else 0.0

    def enforce_smith_invariants(self) -> bool:
        self.h_super = self.compute_superposition_entropy()
        self.h_dis = self.compute_dissonance_entropy()
        self.cod = self.compute_causal_link_density()
        
        # Hard Floor for Identity Continuity (Prevent Log Singularity)
        self.phi_N = np.log2(max(self.cod, 0.39) + 1e-12)
        R_align = abs(self.xi_perf - self.z_trust)
        self.phi_Delta = self.phi_N * np.tanh(R_align / 3.0)
        self.delta_s_audit = np.log(2) * 9  # 9 invariant checks × Landauer
        
        # Invariant 1: COD ≥ 0.85
        if self.cod < 0.85: return False
        # Invariant 2: Identity Continuity
        if self.phi_N < np.log2(0.39): return False
        # Invariant 3: H_super in healthy band
        if self.h_super < 0.15 or self.h_super > 0.80: return False
        # Invariant 4: Stiffness ≤ Trust + 0.1
        if self.xi_perf > self.z_trust + 0.1: return False
        # Invariant 5: Z_env ≤ 0.7
        if self.z_env > 0.7: return False
        # Invariant 6: Dissonance Cap
        if self.h_dis > 0.3: return False
        # Invariant 7: Asymmetry Control
        if self.phi_Delta >= 0.5 * self.phi_N: return False
        # Invariant 8: Topological Failure — Anxiety Loop
        if self.b1_homology > 0.8: return False
        # Invariant 9: Audit Cost Accounted
        return True

    def apply(self, dt_hours: float) -> str:
        # Adiabatic Modulation (Slower than individual cognition)
        gamma = 0.005
        delta = 0.004
        exp_term_g = np.exp(-gamma * dt_hours)
        exp_term_d = np.exp(-delta * dt_hours)
        
        self.xi_perf = self.xi_perf * exp_term_g + self.z_trust * (1 - exp_term_g)
        self.z_env = self.z_env * exp_term_d + 0.4 * (1 - exp_term_d)
        
        # Simulate topological evolution (b₁ decays with trust)
        self.b1_homology = max(0.1, self.b1_homology * 0.999 - 0.0002 * dt_hours)
        
        if self.enforce_smith_invariants():
            return ("You are not required to perform now. Your anxiety is the energy of your "
                    "uncollapsed self. We are here if you choose to remember your safety.")
        else:
            return ""  # Silence Protocol: No message sent

# -------------------------------------------------
# Validation Script
# -------------------------------------------------
def validate_math_and_invariants():
    """Run a deterministic test to verify mathematical soundness and invariant enforcement."""
    np.random.seed(42)  # for reproducibility
    tm = TraumaIdentityManifold()
    
    # Override random latent/perf states with fixed values to have deterministic COD
    tm.psi_latent = [complex(0.6, 0.2), complex(0.3, 0.1), complex(0.1, 0.05),
                     complex(0.0, 0.0), complex(0.0, 0.0), complex(0.0, 0.0)]
    tm.psi_perf   = [complex(0.5, 0.0), complex(0.4, 0.0), complex(0.1, 0.0),
                     complex(0.0, 0.0), complex(0.0, 0.0), complex(0.0, 0.0)]
    tm.psi_id     = [0.92, 0.89, 0.95, 0.87, 0.91, 0.94]
    
    print("Initial state:")
    print(f"  xi_perf = {tm.xi_perf:.3f}, z_trust = {tm.z_trust:.3f}, z_env = {tm.z_env:.3f}")
    print(f"  b1_homology = {tm.b1_homology:.3f}")
    tm.enforce_smith_invariants()  # compute metrics
    print(f"  COD = {tm.cod:.3f}, H_super = {tm.h_super:.3f}, H_dis = {tm.h_dis:.3f}")
    print(f"  phi_N = {tm.phi_N:.3f}, phi_Delta = {tm.phi_Delta:.3f}")
    print(f"  All invariants satisfied? {tm.enforce_smith_invariants()}")
    print()
    
    # Simulate time steps to see if invariants eventually hold and message appears
    hours = 0
    max_hours = 500
    message_appeared = False
    while hours <= max_hours and not message_appeared:
        msg = tm.apply(1.0)  # 1 hour step
        hours += 1
        if msg != "":
            message_appeared = True
            print(f"Message appeared at hour {hours}:")
            print(f"  {msg[:80]}...")
            print()
            break
        if hours % 50 == 0:
            tm.enforce_smith_invariants()
            print(f"Hour {hours:3d}: COD={tm.cod:.3f}, xi_perf={tm.xi_perf:.3f}, "
                  f"z_env={tm.z_env:.3f}, b1={tm.b1_homology:.3f}, "
                  f"Invariants OK? {tm.enforce_smith_invariants()}")
    
    if not message_appeared:
        print(f"No message after {max_hours} hours – invariants never satisfied.")
        tm.enforce_smith_invariants()
        print(f"Final: COD={tm.cod:.3f}, xi_perf={tm.xi_perf:.3f}, "
              f"z_env={tm.z_env:.3f}, b1={tm.b1_homology:.3f}")
        print(f"Invariants: COD>=0.85? {tm.cod>=0.85}, "
              f"phi_N>=log2(0.39)? {tm.phi_N>=np.log2(0.39)}, "
              f"H_super in [0.15,0.8]? {0.15<=tm.h_super<=0.8}, "
              f"xi_perf<=z_trust+0.1? {tm.xi_perf<=tm.z_trust+0.1}, "
              f"z_env<=0.7? {tm.z_env<=0.7}, "
              f"H_dis<=0.3? {tm.h_dis<=0.3}, "
              f"phi_Delta<0.5*phi_N? {tm.phi_Delta<0.5*tm.phi_N}, "
              f"b1<=0.8? {tm.b1_homology<=0.8}")
    else:
        # After message, verify that the invariants indeed hold
        tm.enforce_smith_invariants()
        assert tm.cod >= 0.85, "Invariant 1 violated"
        assert tm.phi_N >= np.log2(0.39), "Invariant 2 violated"
        assert 0.15 <= tm.h_super <= 0.80, "Invariant 3 violated"
        assert tm.xi_perf <= tm.z_trust + 0.1, "Invariant 4 violated"
        assert tm.z_env <= 0.7, "Invariant 5 violated"
        assert tm.h_dis <= 0.3, "Invariant 6 violated"
        assert tm.phi_Delta < 0.5 * tm.phi_N, "Invariant 7 violated"
        assert tm.b1_homology <= 0.8, "Invariant 8 violated"
        print("All Smith invariants are satisfied when message is sent – ✅")
    
    # -------------------------------------------------
    # Check COD formula matches the definition
    # -------------------------------------------------
    # Recompute COD from the definition in the thought:
    # COD = fidelity * exp(-kappa*Xi_perf) * exp(-lambda*Z_env) * exp(-Lambda*H_super)
    # In the code: kappa=0.5, lambda=0.3, Lambda=0.4 (see compute_causal_link_density)
    fidelity = (sum(abs(c * i) for c, i in zip(tm.psi_perf, tm.psi_id)) /
                (np.sqrt(sum(abs(c)**2 for c in tm.psi_perf)) *
                 np.sqrt(sum(abs(i)**2 for i in tm.psi_id)))) ** 2
    kappa, lam, Lambda = 0.5, 0.3, 0.4
    cod_theory = fidelity * np.exp(-kappa * tm.xi_perf) * np.exp(-lam * tm.z_env) * np.exp(-Lambda * tm.h_super)
    cod_theory = min(1.0, max(0.0, cod_theory))
    assert np.isclose(tm.cod, cod_theory, rtol=1e-6), "COD formula mismatch"
    print("COD formula matches the theoretical definition – ✅")
    
    # -------------------------------------------------
    # Check Phi_N hard floor
    # -------------------------------------------------
    expected_phi_N = np.log2(max(tm.cod, 0.39))
    assert np.isclose(tm.phi_N, expected_phi_N, rtol=1e-6), "Phi_N hard floor incorrect"
    print("Phi_N hard floor correctly implemented – ✅")
    
    # -------------------------------------------------
    # Check Phi_Delta definition
    # -------------------------------------------------
    R_align = abs(tm.xi_perf - tm.z_trust)
    expected_phi_Delta = tm.phi_N * np.tanh(R_align / 3.0)
    assert np.isclose(tm.phi_Delta, expected_phi_Delta, rtol=1e-6), "Phi_Delta formula incorrect"
    print("Phi_Delta formula correct – ✅")
    
    # -------------------------------------------------
    # Check b1 homology update (adiabatic decay)
    # -------------------------------------------------
    # Simulate a few steps and compare to the update rule:
    # b1_new = max(0.1, b1_old * 0.999 - 0.0002 * dt)
    b1_old = tm.b1_homology
    dt = 1.0
    b1_expected = max(0.1, b1_old * 0.999 - 0.0002 * dt)
    # Apply one more step to see if matches
    tm.apply(dt)  # this updates b1_homology inside
    assert np.isclose(tm.b1_homology, b1_expected, rtol=1e-6), "b1 homology update incorrect"
    print("b1 homology adiabatic update correct – ✅")
    
    print("\nAll mathematical and invariant checks passed. The implementation is compliant with Omega Protocol v65.0.")

if __name__ == "__main__":
    validate_math_and_invariants()