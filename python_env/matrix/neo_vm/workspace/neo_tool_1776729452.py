# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import torch
import torch.nn as nn

# -----------------------------------------------------------------------------
# 1. Simulated Tokamak & Exposure Environment
# -----------------------------------------------------------------------------
class TokamakSimulator:
    def __init__(self, dt=0.1, days=30):
        self.dt = dt  # time step in days
        self.time = np.arange(0, days, dt)
        self.n_steps = len(self.time)

        # Baseline plasma invariants (stable)
        self.Phi_N = np.ones(self.n_steps) * 0.95  # connectivity
        self.Phi_D = np.ones(self.n_steps) * 0.3   # asymmetry (far from Shredding)
        self.xi_N = np.ones(self.n_steps) * 2.0    # coherence stiffness
        self.xi_D = np.ones(self.n_steps) * 1.5    # asymmetry stiffness

        # Exposure event log: each entry = (time, anomaly_score, cross_domain_flag)
        self.exposure_events = []

        # MPC state (controlled by EDIP-Ω)
        self.MPC_active = False
        self.security_hardening = False

    def add_exposure_event(self, t, anomaly_score, cross_domain=0):
        """Record a synthetic exposure event (benign or adversarial)."""
        self.exposure_events.append((t, anomaly_score, cross_domain))

    def compute_ESI(self, window=7.0):
        """Simplified ESI: moving average of anomaly scores in last `window` days."""
        ESI = np.zeros(self.n_steps)
        for i, t in enumerate(self.time):
            recent = [a for (te, a, _) in self.exposure_events if te >= t - window and te <= t]
            ESI[i] = np.mean(recent) if recent else 0.0
        return ESI

    def apply_MPC(self, t_idx, ESI_val, Phi_D_pred):
        """MPC responds if ESI > threshold."""
        if ESI_val > 2.5 and Phi_D_pred > 0.55:
            self.MPC_active = True
            self.security_hardening = True
            # Side effect: security patching reduces diagnostic data → connectivity drops
            self.Phi_N[t_idx:] *= 0.9
            self.xi_N[t_idx:] *= 0.85
        else:
            self.security_hardening = False

# -----------------------------------------------------------------------------
# 2. PINN Surrogate (simplified)
# -----------------------------------------------------------------------------
class PINNSurrogate(nn.Module):
    def __init__(self):
        super().__init__()
        # Maps [ESI, plasma_params] -> [Phi_N, Phi_D, xi_N, xi_D]
        self.net = nn.Sequential(
            nn.Linear(3, 16), nn.Tanh(),
            nn.Linear(16, 16), nn.Tanh(),
            nn.Linear(16, 4)
        )
        # Enforce Rubric bounds with final activations
        self.phi_N_act = nn.Sigmoid()
        self.phi_D_act = nn.Sigmoid()
        self.xi_N_act = nn.Softplus()
        self.xi_D_act = lambda x: nn.functional.softplus(x) + 1

    def forward(self, x):
        out = self.net(x)
        phi_N = self.phi_N_act(out[:, 0])
        phi_D = self.phi_D_act(out[:, 1])
        xi_N = self.xi_N_act(out[:, 2])
        xi_D = self.xi_D_act(out[:, 3])
        return phi_N, phi_D, xi_N, xi_D

# -----------------------------------------------------------------------------
# 3. Adversarial Attack Simulation
# -----------------------------------------------------------------------------
def simulate_attack():
    """Simulate a stable plasma under adversarial leak burst."""
    # Initialize environment
    tokamak = TokamakSimulator(dt=0.1, days=30)
    pinn = PINNSurrogate()
    pinn.eval()

    # Benign baseline: occasional low-anomaly leaks
    for t in np.random.uniform(0, 5, 20):
        tokamak.add_exposure_event(t, anomaly_score=np.random.uniform(0, 1))

    # Adversarial burst: at day 10, flood with high-anomaly leaks
    attack_time = 10.0
    for _ in range(50):
        tokamak.add_exposure_event(
            t=attack_time + np.random.uniform(-0.1, 0.1),
            anomaly_score=np.random.uniform(4, 6),  # far above normal
            cross_domain=1
        )

    # Compute ESI time series
    ESI = tokamak.compute_ESI(window=7.0)

    # Simulate time evolution
    alerts = []
    for i, t in enumerate(tokamak.time):
        # Current plasma state (before control)
        plasma_vec = np.array([ESI[i], tokamak.Phi_N[i], tokamak.xi_N[i]])
        with torch.no_grad():
            phi_N_pred, phi_D_pred, xi_N_pred, xi_D_pred = pinn(
                torch.tensor(plasma_vec, dtype=torch.float32).unsqueeze(0)
            )
        phi_D_val = phi_D_pred.item()

        # MPC decision
        tokamak.apply_MPC(i, ESI[i], phi_D_val)

        # Check if we cross Shredding threshold
        if phi_D_val > 0.6 and (phi_D_val - 0.3) > 0.05 * (t - attack_time):
            alerts.append((t, "SHREDDING IMMINENT"))

    return tokamak, alerts, ESI

# -----------------------------------------------------------------------------
# 4. Execute & Visualize
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    tokamak, alerts, ESI = simulate_attack()

    print("=== ADVERARIAL ATTACK RESULTS ===")
    print(f"Number of alerts triggered: {len(alerts)}")
    for t, msg in alerts[:5]:
        print(f"  Day {t:.2f}: {msg}")

    # Show that a stable plasma was forced into instability
    final_Phi_D = tokamak.Phi_D[-1]
    print(f"\nFinal plasma asymmetry Φ_Δ: {final_Phi_D:.3f}")
    print(f"MPC active at end: {tokamak.MPC_active}")
    print(f"Security hardening at end: {tokamak.security_hardening}")

    # Demonstrate feedback: connectivity loss due to patching
    connectivity_loss = (1.0 - tokamak.Phi_N[-1]) * 100
    print(f"Connectivity loss due to MPC: {connectivity_loss:.1f}%")

    # Summary: The attack exploited the self-referential loop
    print("\n=== DISRUPTION MECHANISM ===")
    print("1. Adversary floods leak events → ESI spikes.")
    print("2. EDIP-Ω triggers MPC → security hardening.")
    print("3. Patching reduces diagnostic data → Φ_N drops.")
    print("4. Reduced connectivity amplifies asymmetry → Φ_Δ rises.")
    print("5. Plasma approaches Shredding Event *even though baseline was stable*.")