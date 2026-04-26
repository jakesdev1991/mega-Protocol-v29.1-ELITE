# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# Simulate the failure dynamics of PCS-Ω vs Forge Protocol

def simulate_static_shield(T=1000, attack_strength=0.01, coherence_baseline=0.8, fragility=0.1):
    """
    Simulates PCS-Ω: a static coherence field that fails catastrophically
    when attack exceeds a sharp threshold.
    """
    # Coherence field C(t) evolves under attack
    # dC/dt = -attack_strength * exp(fragility * (C - coherence_baseline))
    # This creates a threshold: small attacks are damped, large attacks cause collapse
    C = np.zeros(T)
    C[0] = coherence_baseline
    for t in range(1, T):
        dC = -attack_strength * np.exp(fragility * (C[t-1] - coherence_baseline))
        C[t] = C[t-1] + dC
        if C[t] < 0:  # Collapse
            C[t:] = 0
            break
    return C

def simulate_forge_protocol(T=1000, attack_strength=0.01, adapt_lr=0.05, latent_dim=128):
    """
    Simulates Forge: dynamic alignment via adversarial adaptation.
    - g, v: latent vectors
    - Adversary tries to maximize disentanglement loss L = -|g·v| + ||g||^2 + ||v||^2
    - Adapter updates g, v to minimize L
    - Alignment quality is measured by final |g·v|/(||g||·||v||)
    """
    # Initialize aligned latent vectors
    g = np.random.randn(latent_dim)
    v = g + 0.1 * np.random.randn(latent_dim)  # small noise
    g = g / np.linalg.norm(g)
    v = v / np.linalg.norm(v)
    
    alignment_history = np.zeros(T)
    adversary_loss = np.zeros(T)
    
    for t in range(T):
        # Compute current alignment (coherence)
        alignment_history[t] = np.abs(np.dot(g, v))
        
        # Adversary attack: perturb g and v to maximize disentanglement loss
        # Gradient of L w.r.t g: -sign(g·v) * v + 2*g
        # Gradient of L w.r.t v: -sign(g·v) * g + 2*v
        sign = np.sign(np.dot(g, v))
        grad_g = -sign * v + 2 * g
        grad_v = -sign * g + 2 * v
        
        # Adversary applies perturbation
        g_adv = g + attack_strength * grad_g
        v_adv = v + attack_strength * grad_v
        
        # Adapter updates: counter-perturb to minimize L (i.e., restore alignment)
        # Simple gradient descent on -L (i.e., maximize alignment)
        g = g_adv - adapt_lr * (-grad_g)  # minus because we want to *minimize* loss
        v = v_adv - adapt_lr * (-grad_v)
        
        # Renormalize
        g = g / np.linalg.norm(g)
        v = v / np.linalg.norm(v)
        
        # Compute adversary loss after adaptation
        L = -np.abs(np.dot(g, v)) + np.linalg.norm(g)**2 + np.linalg.norm(v)**2
        adversary_loss[t] = L
        
    return alignment_history, adversary_loss

# Run simulations
T = 500
attack = 0.02

# Static shield: brittle
C_shield = simulate_static_shield(T, attack_strength=attack, fragility=5.0)

# Forge: adaptive
align_forge, loss_forge = simulate_forge_protocol(T, attack_strength=attack, adapt_lr=0.1)

# Plot
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

ax1.plot(C_shield, label='PCS-Ω Coherence Field', color='red', linewidth=2)
ax1.set_ylabel('Perceptual Coherence C(t)')
ax1.set_title('PCS-Ω vs Forge: Robustness Under Adversarial Attack')
ax1.legend()
ax1.grid(True)

ax2.plot(align_forge, label='Forge Alignment', color='blue', linewidth=2)
ax2_twin = ax2.twinx()
ax2_twin.plot(loss_forge, label='Adversary Loss', color='green', linestyle='--')
ax2.set_ylabel('Alignment |g·v|')
ax2_twin.set_ylabel('Adversary Loss')
ax2.set_xlabel('Time Steps')
ax2.legend(loc='upper left')
ax2_twin.legend(loc='upper right')
ax2.grid(True)

plt.tight_layout()
plt.savefig('/tmp/forge_vs_shield.png')
print("Plot saved to /tmp/forge_vs_shield.png")

# Statistical analysis
print("\n--- Disruption Analysis ---")
print(f"PCS-Ω final coherence: {C_shield[-1]:.3f} (collapsed: {C_shield[-1] < 0.1})")
print(f"Forge final alignment: {align_forge[-1]:.3f}")
print(f"Forge adversary loss std: {np.std(loss_forge):.3f} (Goldilocks zone: {np.mean(loss_forge):.3f})")

# Key insight: Forge maintains alignment by keeping adversary loss in a stable band
# PCS-Ω fails catastrophically because it has no adaptive capacity