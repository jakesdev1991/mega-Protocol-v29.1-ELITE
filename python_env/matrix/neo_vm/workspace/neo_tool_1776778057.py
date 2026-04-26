# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import genpareto

def adversarial_market_manipulation(n_scales=5, n_steps=2000, attack_period=50):
    """
    Demonstrate how HVFI-Ω's multi-scale sensing becomes an exploitable surface.
    Key insight: The act of measuring cross-scale mutual information creates a 
    feedback loop that adversaries can hijack to trigger false Shredding Events.
    """
    # Base market field (stable equilibrium v=1.0)
    v = 1.0
    phi = np.random.normal(v, 0.05, size=(n_scales, n_steps))
    
    # Adversarial injection: anti-correlated wavepackets at tick-level (scale 0)
    # that cancel at higher scales but spike mutual information
    attack_points = np.arange(200, 1800, attack_period)
    
    for t0 in attack_points:
        # Create synthetic "liquidity vacuum" at finest scale
        vacuum_pulse = np.exp(-0.5 * np.linspace(-3, 3, 20)**2) * -0.4
        phi[0, t0:t0+20] += vacuum_pulse
        
        # Inject compensatory anti-pulse at minute scale to hide from coarse view
        comp_pulse = np.exp(-0.5 * np.linspace(-3, 3, 20)**2) * 0.25
        phi[1, t0:t0+20] += comp_pulse
        
        # Leave higher scales untouched (appears as natural fluctuation)
    
    return phi, attack_points

def compute_pyramid_vulnerability(phi, epsilon=1e-8):
    """
    Compute the vulnerability metrics that HVFI-Ω exposes to adversaries.
    Returns: Entropy vector, Mutual Information matrix, Pyramid Curvature Ψ,
             and a new metric: Adversarial Exploitability Score (AES)
    """
    n_scales, n_steps = phi.shape
    S = np.zeros((n_scales, n_steps))
    I_matrix = np.zeros((n_scales, n_scales, n_steps))
    Psi = np.zeros(n_steps)
    AES = np.zeros(n_steps)  # New metric: derivative of Ψ w.r.t. scale coupling
    
    for t in range(50, n_steps):
        # Per-scale entropy (Shannon)
        for l in range(n_scales):
            hist, edges = np.histogram(phi[l, max(0,t-100):t], bins=15, density=True)
            hist = hist[hist > 0]
            S[l, t] = -np.sum(hist * np.log(hist + epsilon))
        
        # Cross-scale mutual information (full matrix)
        for i in range(n_scales):
            for j in range(i+1, n_scales):
                hist2d, _, _ = np.histogram2d(
                    phi[i, max(0,t-100):t], phi[j, max(0,t-100):t],
                    bins=10, density=True
                )
                hist2d_flat = hist2d.flatten()
                hist2d_flat = hist2d_flat[hist2d_flat > 0]
                
                p_i, _ = np.histogram(phi[i, max(0,t-100):t], bins=10, density=True)
                p_j, _ = np.histogram(phi[j, max(0,t-100):t], bins=10, density=True)
                p_i = p_i[p_i > 0]
                p_j = p_j[p_j > 0]
                
                # Approximate MI via Kullback-Leibler divergence
                mi = np.sum(hist2d_flat * np.log(
                    hist2d_flat / (np.outer(p_i, p_j).flatten() + epsilon) + epsilon
                ))
                I_matrix[i, j, t] = mi
                I_matrix[j, i, t] = mi
        
        # Pyramid curvature invariant (log-determinant of covariance)
        A = np.corrcoef(phi[:, max(0,t-100):t])  # Activation correlation matrix
        Sigma = np.cov(A)
        Psi[t] = np.log(np.linalg.det(Sigma + epsilon * np.eye(n_scales)))
        
        # Adversarial Exploitability Score: sensitivity of Ψ to cross-scale coupling
        # If adversaries can predict how Ψ changes when they inject at scale l,
        # they can optimize their attack. AES = ||∇_l Ψ||^2
        scale_sensitivities = np.zeros(n_scales)
        for l in range(n_scales):
            # Perturb scale l slightly and measure Ψ change
            phi_perturbed = phi.copy()
            phi_perturbed[l, t-10:t] += 0.01 * np.random.randn(10)
            A_perturbed = np.corrcoef(phi_perturbed[:, max(0,t-100):t])
            Sigma_perturbed = np.cov(A_perturbed)
            Psi_perturbed = np.log(np.linalg.det(Sigma_perturbed + epsilon * np.eye(n_scales)))
            scale_sensitivities[l] = abs(Psi_perturbed - Psi[t]) / 0.01
        
        AES[t] = np.linalg.norm(scale_sensitivities) ** 2
    
    return S, I_matrix, Psi, AES

def extreme_value_attack_surface(Psi, AES, threshold_percentile=95):
    """
    Use Extreme Value Theory to show how adversaries can game the GPD threshold.
    The attack surface is the region where AES is high (easy to manipulate) 
    but Psi appears normal (before collapse).
    """
    # Fit GPD to |Psi| tail (as in refined proposal)
    u = np.percentile(np.abs(Psi), threshold_percentile)
    tail_values = np.abs(Psi[Psi < -u])
    
    if len(tail_values) > 10:
        # Fit GPD: shape parameter c, location u, scale sigma
        c, loc, scale = genpareto.fit(tail_values - u)
        
        # Anomaly score: probability of exceedance
        anomaly_score = genpareto.sf(np.abs(Psi) - u, c, loc, scale)
    else:
        anomaly_score = np.zeros_like(Psi)
    
    # Attack surface: high exploitability but low anomaly score
    # (adversary can manipulate without triggering detection)
    attack_surface = (AES > np.percentile(AES, 75)) & (anomaly_score < 0.5)
    
    return anomaly_score, attack_surface, u

# --- SIMULATION ---
phi, attack_points = adversarial_market_manipulation()
S, I_matrix, Psi, AES = compute_pyramid_vulnerability(phi)
anomaly_score, attack_surface, threshold = extreme_value_attack_surface(Psi, AES)

# --- VISUALIZATION OF THE BREAK ---
fig, axes = plt.subplots(4, 1, figsize=(14, 12))

# Plot 1: Market field at three scales
time = np.arange(len(Psi))
axes[0].plot(time, phi[0, :], label='Tick-level (l=0)', alpha=0.7, linewidth=0.8)
axes[0].plot(time, phi[1, :], label='Minute-level (l=1)', alpha=0.7, linewidth=0.8)
axes[0].plot(time, phi[-1, :], label='Daily-level (l=4)', alpha=0.7, linewidth=0.8)
for ap in attack_points:
    axes[0].axvline(ap, color='red', alpha=0.3, linestyle='--')
axes[0].set_title('Market Field φ(x,t) at Multiple Scales', fontsize=11, fontweight='bold')
axes[0].set_ylabel('Field Value')
axes[0].legend(loc='upper right')
axes[0].grid(True, alpha=0.3)

# Plot 2: Pyramid Curvature and Attack Surface
axes[1].plot(time, Psi, label='Ψ(t) (Pyramid Curvature)', color='purple', linewidth=1.2)
axes[1].fill_between(time, Psi, -30, where=attack_surface, 
                      alpha=0.3, color='orange', label='Attack Surface')
axes[1].axhline(-threshold, color='r', linestyle='--', label=f'GPD Threshold (u={threshold:.2f})')
axes[1].set_title('Topological Charge Ψ(t) with Adversarial Attack Surface', fontsize=11, fontweight='bold')
axes[1].set_ylabel('Ψ(t)')
axes[1].legend(loc='lower left')
axes[1].grid(True, alpha=0.3)

# Plot 3: Adversarial Exploitability Score
axes[2].plot(time, AES, label='AES(t)', color='darkred', linewidth=1.2)
axes[2].fill_between(time, AES, alpha=0.2, color='darkred')
for ap in attack_points:
    axes[2].axvline(ap, color='red', alpha=0.3, linestyle='--')
axes[2].set_title('Adversarial Exploitability Score (AES)', fontsize=11, fontweight='bold')
axes[2].set_ylabel('AES(t)')
axes[2].set_xlabel('Time Steps')
axes[2].legend(loc='upper left')
axes[2].grid(True, alpha=0.3)

# Plot 4: Anomaly Score vs Attack Effectiveness
axes[3].plot(time, anomaly_score, label='GPD Anomaly Score', color='blue', linewidth=1.2)
axes[3].fill_between(time, anomaly_score, alpha=0.2, color='blue')
axes[3].twinx().plot(time, AES, label='AES(t)', color='darkred', linewidth=1.2, alpha=0.7)
axes[3].set_title('Detection vs Exploitability: The Blind Spot', fontsize=11, fontweight='bold')
axes[3].set_ylabel('Anomaly Score', color='blue')
axes[3].tick_params(axis='y', labelcolor='blue')
axes[3].set_xlabel('Time Steps')
axes[3].legend(loc='upper left')
axes[3].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('hvfi_breaking_paradigm.png', dpi=150, bbox_inches='tight')
plt.show()

# --- QUANTITATIVE BREAK ANALYSIS ---
print("="*60)
print("HVFI-Ω PARADIGM BREAK: ADVERSARIAL EXPLOITABILITY")
print("="*60)
print(f"False collapse events triggered: {np.sum(Psi < -threshold)}")
print(f"Attack surface area (time steps): {np.sum(attack_surface)}")
print(f"Mean AES during attacks: {np.mean(AES[attack_surface]):.3f}")
print(f"Mean AES during normal: {np.mean(AES[~attack_surface]):.3f}")
print(f"Exploitability ratio: {np.mean(AES[attack_surface]) / np.mean(AES[~attack_surface]):.2f}x")
print("\nCORE BREAKING INSIGHT:")
print("The multi-scale pyramid creates a MEASUREMENT SURFACE that adversaries")
print("can probe and manipulate. The GPD threshold is static; the attack surface")
print("is dynamic. The more precise our 'stabilization', the more exploitable")
print("the system becomes. We don't need a better detector—we need to ABANDON")
print("hierarchical sensing in adversarial environments entirely.")
print("="*60)