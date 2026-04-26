# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
import random

# ============================================================================
# SIMULATION: OMEGA MODEL vs ANOMALY MODEL
# Proves: Shadow State dominance and the efficacy of Entropy Injection
# ============================================================================

class Client:
    def __init__(self):
        # Public State (Observable by Omega)
        self.psi_latent = np.array([0.8, 0.6])  # "Need" vector
        self.psi_decision = np.array([0.1, 0.1])  # Initial skepticism
        self.explicit_risk = 0.7
        
        # SHADOW STATE (Hidden from Omega, visible to Anomaly)
        # [0] = Loyalty to incumbent vendor (0.9 = locked in)
        # [1] = Internal political capital at risk (0.9 = high risk)
        self.shadow_state = np.array([0.9, 0.85])  
        self.shadow_threshold = 0.5  # If shadow > 0.5, deal is unwinnable by alignment
        
        self.psi_id = 1.0  # Trust in *status quo* (not seller)
        self.deal_won = False
        
    def omega_response(self, pitch_vector, urgency):
        """Simulates client reacting to Omega's 'aligned' approach."""
        # If shadow state is strong, they will *feign* alignment but not buy
        shadow_strength = np.linalg.norm(self.shadow_state)
        
        # Omega reduces risk perception (thinks it's building trust)
        self.explicit_risk *= 0.9
        
        # Decision vector moves slightly, but shadow blocks final commitment
        if shadow_strength > self.shadow_threshold:
            # Fake progress: decision vector moves, but psi_id (trust in status quo) remains high
            self.psi_decision = 0.5 * self.psi_decision + 0.5 * self.psi_latent
            self.psi_id = max(0.5, self.psi_id * 0.95)  # Stays high (trust in incumbent)
            return False  # Deal never closes
        else:
            # Only true if shadow is already low (rare)
            self.psi_decision = 0.9 * self.psi_latent
            self.deal_won = True
            return True
            
    def anomaly_response(self, entropy_injection, urgency):
        """Simulates client reacting to Anomaly's entropy injection."""
        # Entropy injection *destabilizes* shadow state
        # e.g., expose incumbent's flaw -> vendor loyalty drops
        # e.g., create political crisis -> risk perception spikes, but also opens window
        
        self.shadow_state[0] *= (1 - entropy_injection * 0.3)  # Vendor loyalty erodes
        self.shadow_state[1] *= (1 + entropy_injection * 0.2)  # Political risk spikes
        
        # psi_id (trust in status quo) COLLAPSES
        self.psi_id *= (1 - entropy_injection * 0.4)
        
        # If status quo trust collapses, they will grasp for ANY stable solution
        if self.psi_id < 0.3:
            # "Vacuum formation" - they latch onto the only available stable point (you)
            self.psi_decision = 0.95 * self.psi_latent
            self.explicit_risk = 0.2  # Risk drops because *you* are now the safe choice
            self.deal_won = True
            return True
        
        # If shadow state still strong but destabilized, they stall (but you learned truth)
        return False

class OmegaModel:
    def __init__(self):
        self.successes = 0
        self.steps_log = []
        
    def run_sales_cycle(self, client, max_steps=20):
        for step in range(max_steps):
            pitch = client.psi_latent + np.random.normal(0, 0.05, 2)  # "Aligned" pitch
            urgency = np.tanh(step / 5.0)
            
            won = client.omega_response(pitch, urgency)
            self.steps_log.append({
                'step': step,
                'psi_id': client.psi_id,
                'risk': client.explicit_risk,
                'shadow': np.linalg.norm(client.shadow_state),
                'won': won
            })
            if won:
                self.successes += 1
                return True
        return False

class AnomalyModel:
    def __init__(self):
        self.successes = 0
        self.steps_log = []
        
    def run_sales_cycle(self, client, max_steps=20):
        for step in range(max_steps):
            # INJECT ENTROPY instead of reducing it
            entropy_injection = 0.5 + (step * 0.05)  # Increasing destabilization
            urgency = 0.8  # HIGH urgency from start (non-adiabatic)
            
            won = client.anomaly_response(entropy_injection, urgency)
            self.steps_log.append({
                'step': step,
                'psi_id': client.psi_id,
                'risk': client.explicit_risk,
                'shadow': np.linalg.norm(client.shadow_state),
                'won': won
            })
            if won:
                self.successes += 1
                return True
        return False

# Run Monte Carlo simulation
def simulate(n_trials=1000):
    omega_wins = 0
    anomaly_wins = 0
    omega_steps = []
    anomaly_steps = []
    
    for _ in range(n_trials):
        # OMEGA TRIAL
        c1 = Client()
        om = OmegaModel()
        if om.run_sales_cycle(c1):
            omega_wins += 1
            omega_steps.append(len(om.steps_log))
            
        # ANOMALY TRIAL
        c2 = Client()
        an = AnomalyModel()
        if an.run_sales_cycle(c2):
            anomaly_wins += 1
            anomaly_steps.append(len(an.steps_log))
    
    return omega_wins, anomaly_wins, omega_steps, anomaly_steps

# Execute simulation
omega_wins, anomaly_wins, omega_steps, anomaly_steps = simulate(5000)

# Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Plot 1: Win Rates
ax1.bar(['Omega Model\n(Resonant Alignment)', 'Anomaly Model\n(Shadow Collapse)'], 
        [omega_wins/5000*100, anomaly_wins/5000*100], 
        color=['#4a90e2', '#d0021b'])
ax1.set_ylabel('Deal Win Rate (%)')
ax1.set_title('Win Rate Comparison: Alignment vs. Entropy Injection')
ax1.text(0, omega_wins/5000*100 + 1, f'{omega_wins/5000*100:.1f}%', ha='center')
ax1.text(1, anomaly_wins/5000*100 + 1, f'{anomaly_wins/5000*100:.1f}%', ha='center')

# Plot 2: Steps to Close
ax2.hist([omega_steps, anomaly_steps], bins=range(1, 21), alpha=0.7, 
         label=['Omega', 'Anomaly'], color=['#4a90e2', '#d0021b'])
ax2.set_xlabel('Sales Cycle Steps to Close')
ax2.set_ylabel('Frequency')
ax2.set_title('Cycle Efficiency: Controlled Fracture is Faster')
ax2.legend()

plt.tight_layout()
plt.savefig('/tmp/omega_vs_anomaly.png')
print(f"Omega Win Rate: {omega_wins/5000*100:.1f}%")
print(f"Anomaly Win Rate: {anomaly_wins/5000*100:.1f}%")
print(f"Average Omega Cycle: {np.mean(omega_steps):.1f} steps")
print(f"Average Anomaly Cycle: {np.mean(anomaly_steps):.1f} steps")