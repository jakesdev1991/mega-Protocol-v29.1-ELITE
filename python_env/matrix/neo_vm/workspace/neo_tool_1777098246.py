# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List

@dataclass
class DecisionNode:
    approval_cost: float
    risk_variance: float
    shadow_activity: float  # Dark eigenstate intensity (0=visible, 1=hidden)

@dataclass
class Organization:
    psi_id_org: float
    xi_sys: float
    nodes: List[DecisionNode]
    dark_identity: float  # Unobserved identity fragmentation
    
    def cod(self):
        # Simulate intent/outcome dot product with dark identity penalty
        fidelity = np.random.beta(2, 2)  # Simulated alignment
        dark_penalty = np.exp(-self.dark_identity * 2.0)  # Hidden friction
        H_top = sum(n.approval_cost * n.risk_variance for n in self.nodes) / len(self.nodes)
        stiffness_penalty = np.exp(-0.5 * self.xi_sys)
        if self.psi_id_org < 0.95:
            # Hard gate violation: COD collapses
            identity_gate = self.psi_id_org if self.psi_id_org > 0.70 else 0.0
        else:
            identity_gate = self.psi_id_org
        return fidelity * np.exp(-H_top) * stiffness_penalty * identity_gate * dark_penalty
    
    def simulate_cico(self, steps=50):
        """Simulate Controlled Identity Collapse and recovery."""
        history = []
        for t in range(steps):
            # Pre-collapse: identity slowly eroding due to dark friction
            if t < 10:
                self.dark_identity += 0.02  # Hidden fragmentation grows
                self.psi_id_org = max(0.95, self.psi_id_org - 0.005)
            # COLLAPSE: at t=10, violate hard gate
            elif t == 10:
                self.psi_id_org = 0.75  # Induced decoherence
                self.xi_sys *= 0.5  # Stiffness drops (chaos)
            # Recovery: re-entangle dark identity into visible manifold
            elif t > 10:
                self.dark_identity = max(0.0, self.dark_identity - 0.04)
                self.psi_id_org = min(1.0, self.psi_id_org + 0.015)
                self.xi_sys = min(3.0, self.xi_sys * 1.05)
            
            cod_val = self.cod()
            history.append({
                't': t,
                'psi_id_org': self.psi_id_org,
                'dark_identity': self.dark_identity,
                'xi_sys': self.xi_sys,
                'cod': cod_val
            })
        return history

# Initialize a "healthy" but sclerotic organization
org = Organization(
    psi_id_org=0.96,
    xi_sys=2.0,
    nodes=[DecisionNode(0.3, 0.2, 0.1) for _ in range(20)],
    dark_identity=0.1
)

# Run simulation
data = org.simulate_cico()
time = [d['t'] for d in data]
cod = [d['cod'] for d in data]
psi = [d['psi_id_org'] for d in data]
dark = [d['dark_identity'] for d in data]

# Plot the fracture
fig, ax = plt.subplots(3, 1, figsize=(8, 6), sharex=True)
ax[0].plot(time, cod, label='COD', color='purple')
ax[0].axvline(10, color='red', linestyle='--', label='Collapse')
ax[0].set_ylabel('COD')
ax[0].legend()
ax[0].set_title('CICO: Controlled Identity Collapse')

ax[1].plot(time, psi, label='Psi_id_org', color='blue')
ax[1].axhline(0.95, color='black', linestyle=':', label='Hard Gate')
ax[1].axvline(10, color='red', linestyle='--')
ax[1].set_ylabel('Identity')
ax[1].legend()

ax[2].plot(time, dark, label='Dark Identity', color='gray')
ax[2].axvline(10, color='red', linestyle='--')
ax[2].set_ylabel('Dark Fragmentation')
ax[2].set_xlabel('Time Steps')
ax[2].legend()

plt.tight_layout()
plt.savefig('/mnt/data/cico_simulation.png')
plt.show()

# Final metrics
pre_collapse_cod = np.mean([d['cod'] for d in data[:10]])
post_recovery_cod = np.mean([d['cod'] for d in data[30:]])
print(f"Pre-collapse COD: {pre_collapse_cod:.3f}")
print(f"Post-recovery COD: {post_recovery_cod:.3f}")
print(f"Improvement: {(post_recovery_cod - pre_collapse_cod) / pre_collapse_cod:.1%}")
print(f"Dark identity purged: {data[0]['dark_identity'] - data[-1]['dark_identity']:.2f}")