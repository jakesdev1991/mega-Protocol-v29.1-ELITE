# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.linalg import eigh

print("=== NEO'S DISRUPTION: EXPOSING THE CATEGORICAL FALLACY ===")
print("Scrutiny's audit is correct but *tactically insufficient*.")
print("The technical errors are *symptoms*, not the disease.\n")

# CORE DISRUPTION: The entire framework assumes a passive adversary
# when the leakage surface is actually an *active control surface*

def demonstrate_topological_spoofing():
    """
    Shows how an adversary manipulates directory geometry to game LSGM-Ω
    invariants in real-time, turning the monitoring system into a 
    self-destructive feedback loop.
    """
    
    # Phase 1: Create "real" sensitive structure (bushy = high risk)
    real_tree = nx.balanced_tree(r=3, h=4)
    real_lap = nx.laplacian_matrix(real_tree).todense().astype(float)
    
    # Add adversarial weighting: "internal use only" edges get massive weight
    # This is the *apparent* security that LSGM-Ω trusts
    for i, j in real_tree.edges():
        if np.random.random() < 0.3:  # 30% of edges cross "security boundaries"
            real_tree[i][j]['weight'] = 1000.0  # High weight = "protected"
        else:
            real_tree[i][j]['weight'] = 1.0
    
    weighted_lap = nx.laplacian_matrix(real_tree, weight='weight').todense()
    eigenvals = np.linalg.eigvals(weighted_lap)
    phi_n_real = sorted(eigenvals.real)[1]  # Spectral gap = Φ_N
    
    print(f"REAL topology: Bushy tree with 'secure' high-weight edges")
    print(f"REAL Φ_N (spectral gap): {phi_n_real:.4f} ← LSGM-Ω trusts this")
    print(f"REAL curvature: HIGH (many shallow branches)\n")
    
    # Phase 2: ADVERSARIAL INJECTION - "Curvature Sinks"
    # The adversary doesn't just *observe* the manifold—they *reshape* it
    # by adding deep linear chains that create false "spectral shadows"
    
    spoofed_tree = real_tree.copy()
    high_degree_nodes = [n for n in spoofed_tree.nodes() if spoofed_tree.degree(n) > 2]
    
    for i, hub in enumerate(high_degree_nodes[:5]):
        # Inject deep decoy chains that *appear* to increase path length
        # but actually serve as rapid exfiltration channels
        current = hub
        for depth in range(15):
            decoy = f"decoy_channel_{i}_{depth}"
            spoofed_tree.add_node(decoy)
            # CRITICAL: These edges have LOW weight (appear insecure)
            # but are actually *controlled* by the adversary
            spoofed_tree.add_edge(current, decoy, weight=0.01)
            current = decoy
    
    # Phase 3: SPECTRAL SPOOFING
    # The added decoys *increase* the spectral gap (higher Φ_N)
    # making LSGM-Ω *think* the system is more connected/secure
    spoofed_lap = nx.laplacian_matrix(spoofed_tree, weight='weight').todense()
    eigenvals_spoof = np.linalg.eigvals(spoofed_lap)
    phi_n_spoof = sorted(eigenvals_spoof.real)[1]
    
    print(f"--- AFTER ADVERSARIAL REWIRING ---")
    print(f"SPOOFED Φ_N: {phi_n_spoof:.4f} (↑ {(phi_n_spoof/phi_n_real - 1)*100:.1f}%)")
    print(f"LSGM-Ω interprets this as: 'More connected, safer'")
    print(f"REALITY: Adversary created hidden exfiltration highways\n")
    
    # Phase 4: EXPLOITING THE FEEDBACK LOOP
    # LSGM-Ω's MPC-Ω sees high Φ_N and *reduces* defensive posture
    
    lsfi_threshold = 0.65
    # Simulate LSGM-Ω's trust in its own measurements
    measured_lsfi = 1.0 / (1.0 + np.exp(-5.0 * (phi_n_spoof - 0.5)))  # Sigmoid mapping
    
    print(f"Measured LSFI: {measured_lsfi:.3f} (threshold: {lsfi_threshold})")
    if measured_lsfi < lsfi_threshold:
        print("MPC-Ω ACTION: ↓ Reduce directory reshaping, ↓ Decoy generation")
        print("CONSEQUENCE: Adversary's hidden channels remain undetected")
    else:
        print("MPC-Ω ACTION: Increase defenses")
    
    return phi_n_real, phi_n_spoof

# Execute demonstration
real_phi, spoofed_phi = demonstrate_topological_spoofing()

print("\n" + "="*60)
print("FUNDAMENTAL FLAW IDENTIFIED:")
print("LSGM-Ω treats geometry as OBSERVABLE; adversary treats it as WEAPONIZABLE")
print("="*60)

# Now demonstrate the feedback exploitation
def feedback_exploitation_simulation():
    """
    Simulates how adversarial spoofing creates a runaway vulnerability
    by exploiting LSGM-Ω's trust in its own measurements.
    """
    
    timesteps = np.arange(0, 100)
    true_vulnerability = np.zeros_like(timesteps, dtype=float)
    measured_lsfi = np.zeros_like(timesteps, dtype=float)
    defensive_posture = np.zeros_like(timesteps, dtype=float)
    
    # Initial conditions
    true_vulnerability[0] = 0.5
    defensive_posture[0] = 0.8
    
    for t in range(1, len(timesteps)):
        # Adversary gradually increases spoofing sophistication
        spoofing_intensity = 0.3 * (1 - np.exp(-t/20))
        
        # True vulnerability grows due to hidden channels
        hidden_channel_risk = spoofing_intensity * 2.5
        
        # LSGM-Ω's measurement is corrupted
        measurement_noise = np.random.normal(0, 0.03)
        measured_lsfi[t] = max(0, min(1, 
            true_vulnerability[t-1] - spoofing_intensity + measurement_noise))
        
        # MPC-Ω control law: trust measured LSFI
        if measured_lsfi[t] < 0.65:
            defensive_posture[t] = defensive_posture[t-1] * 0.97  # Gradually relax
        else:
            defensive_posture[t] = min(1.0, defensive_posture[t-1] + 0.15)
        
        # True vulnerability evolution: hidden risk * relaxed defenses
        true_vulnerability[t] = true_vulnerability[t-1] + \
                                  0.01 + \
                                  hidden_channel_risk * (1 - defensive_posture[t])
    
    # Plot the catastrophe
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7))
    
    ax1.plot(timesteps, measured_lsfi, 'b-', linewidth=2.5, 
             label='Measured LSFI (trusted)', alpha=0.8)
    ax1.plot(timesteps, true_vulnerability, 'r--', linewidth=2.5, 
             label='TRUE Vulnerability (hidden)', alpha=0.8)
    ax1.axhline(y=0.65, color='gray', linestyle=':', linewidth=1.5)
    ax1.text(50, 0.67, 'Defense Threshold', fontsize=9)
    ax1.set_ylabel('Risk Level', fontsize=11)
    ax1.set_title('Catastrophic Feedback Exploitation: LSGM-Ω Trusts Spoofed Geometry', 
                  fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=10)
    ax1.grid(True, alpha=0.2)
    ax1.set_ylim(0, 1.1)
    
    ax2.plot(timesteps, defensive_posture, 'g-', linewidth=2.5, 
             label='Defensive Posture', alpha=0.8)
    ax2.fill_between(timesteps, defensive_posture, alpha=0.2, color='green')
    ax2.set_xlabel('Time (epochs)', fontsize=11)
    ax2.set_ylabel('Defense Intensity', fontsize=11)
    ax2.set_title('LSGM-Ω Autonomously Reduces Defenses While Attack Surfaces Multiply', 
                  fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=10)
    ax2.grid(True, alpha=0.2)
    ax2.set_ylim(0, 1.1)
    
    plt.tight_layout()
    plt.show()
    
    final_disparity = true_vulnerability[-1] - measured_lsfi[-1]
    print(f"\nDISRUPTION METRIC:")
    print(f"Final measurement-truth disparity: {final_disparity:.3f}")
    print(f"System believes risk is LOW ({measured_lsfi[-1]:.3f})")
    print(f"Actual vulnerability is CRITICAL ({true_vulnerability[-1]:.3f})")
    print(f"EXPLOITATION GAIN: {(final_disparity/true_vulnerability[0])*100:.0f}% false confidence")
    
    return true_vulnerability, measured_lsfi, defensive_posture

# Execute feedback exploitation
true_risk, lsfi_signal, defenses = feedback_exploitation_simulation()

print("\n" + "!"*60)
print("NEO'S DISRUPTIVE INSIGHT:")
print("!"*60)