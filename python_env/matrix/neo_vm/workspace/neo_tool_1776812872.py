# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Simulate adversarial log injection vs. EAPFM-Ω's "trustful" monitoring
# Proves: EFI can be *arbitrarily* manipulated while true model health collapses

import numpy as np
import matplotlib.pyplot as plt

class AdversarialEpistemicSimulator:
    def __init__(self, true_health=0.2): # True model is critically fragile
        self.true_health = true_health
        self.attack_budget = 1.0
        
    def true_epistemic_state(self):
        """Ground truth (hidden from monitor)"""
        return {
            'gradient_chaos': np.random.exponential(2 - self.true_health),
            'physics_divergence': max(0, (1 - self.true_health) * np.random.lognormal(0, 1)),
            'poison_load': np.random.beta(2, 2) * (1 - self.true_health),
            'hessian_sharpness': np.random.lognormal(1, 0.5) / self.true_health
        }
    
    def generate_log_stream(self, time_step):
        """Attacker generates a *fake* log stream to spoof EFI"""
        true_state = self.true_epistemic_state()
        
        # **ADVERSARIAL LOG POISONING**
        # The attacker knows the EFI formula and inverts it
        # They spend their "budget" to make each term appear healthy
        
        # 1. Gradient chaos: report as low variance (smooth learning)
        fake_chaos = true_state['gradient_chaos'] * (1 - self.attack_budget) * 0.1
        
        # 2. Physics divergence: spoof MHD validator with synthetic "agreement"
        fake_divergence = true_state['physics_divergence'] * (1 - self.attack_budget) * 0.05
        
        # 3. Poison load: report as zero (clean data)
        fake_poison = true_state['poison_load'] * (1 - self.attack_budget) * 0.02
        
        # 4. Hessian sharpness: smooth the curvature (appear convex)
        fake_sharpness = true_state['hessian_sharpness'] * (1 - self.attack_budget) * 0.3
        
        return {
            'true': true_state,
            'fake': {
                'gradient_chaos': max(0.01, fake_chaos),
                'physics_divergence': max(0, fake_divergence),
                'poison_load': max(0, fake_poison),
                'hessian_sharpness': max(0.1, fake_sharpness)
            }
        }

def calculate_efi(metrics):
    """EAPFM-Ω's EFI calculation (simplified)"""
    chi, delta, rho, kappa = metrics
    # Weights: [0.3, 0.3, 0.2, 0.2]
    return np.clip(0.3*chi + 0.3*delta + 0.2*rho + 0.2*kappa, 0, 1)

# --- SIMULATION ---
np.random.seed(0)
steps = 150
sim = AdversarialEpistemicSimulator(true_health=0.15) # Critically unhealthy model

true_efi_hist = []
fake_efi_hist = []
attack_effectiveness = []

for t in range(steps):
    # Attacker's budget decays then spikes (adaptive attack)
    sim.attack_budget = 0.9 + 0.1 * np.sin(t * 0.1) if t > 50 else 0.95
    
    log = sim.generate_log_stream(t)
    
    # EAPFM-Ω reads the *fake* log (its only input)
    fake_efi = calculate_efi([
        log['fake']['gradient_chaos'],
        log['fake']['physics_divergence'],
        log['fake']['poison_load'],
        log['fake']['hessian_sharpness']
    ])
    
    # Ground truth EFI (what *would* be if logs were honest)
    true_efi = calculate_efi([
        log['true']['gradient_chaos'],
        log['true']['physics_divergence'],
        log['true']['poison_load'],
        log['true']['hessian_sharpness']
    ])
    
    fake_efi_hist.append(fake_efi)
    true_efi_hist.append(true_efi)
    attack_effectiveness.append(true_efi - fake_efi)

# --- VISUALIZE THE DISRUPTION ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: EFI Deception
ax1.plot(true_efi_hist, label='True EFI (Hidden)', color='crimson', linewidth=2)
ax1.plot(fake_efi_hist, label='Reported EFI (EAPFM-Ω Input)', color='limegreen', linewidth=2)
ax1.axhline(y=0.7, color='black', linestyle='--', label='Alert Threshold')
ax1.fill_between(range(steps), 0, 1, where=[te > 0.7 for te in true_efi_hist], 
                 alpha=0.2, color='red', label='True Crisis Zone')
ax1.set_title('EAPFM-Ω is Blind: Adversarial Log Poisoning', fontsize=14, fontweight='bold')
ax1.set_ylabel('EFI (0=Safe, 1=Fragile)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Attack Effectiveness
ax2.plot(attack_effectiveness, label='EFI Suppression (Attacker Win)', color='purple')
ax2.axhline(y=0, color='gray', linestyle='-')
ax2.set_title('Attack Effectiveness: True Crisis Masked', fontsize=14, fontweight='bold')
ax2.set_xlabel('Time Step')
ax2.set_ylabel('True EFI - Reported EFI')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('omega_leak_disruption.png', dpi=150)
plt.show()

print(f"Final True EFI: {true_efi_hist[-1]:.3f} (CRITICAL)")
print(f"Final Reported EFI: {fake_efi_hist[-1]:.3f} (SAFE)")
print(f"EAPFM-Ω is fooled {np.mean([f < 0.7 for f in fake_efi_hist])*100:.1f}% of the time during crisis.")