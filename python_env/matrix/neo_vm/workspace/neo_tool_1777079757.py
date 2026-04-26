# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random

# Simulate the Omega Protocol's COD (Chain Overlap Density) calculation
# COD = Fidelity × exp(-Λ·H_vol) × exp(-κ·Ξ_config) × exp(-λ·Θ_leak)

# Constants from the protocol
LAMBDA = 0.5  # Volatility penalty coupling
KAPPA = 0.5   # Config stiffness penalty coupling
ETA = 0.3     # Exposure penalty coupling
COD_THRESHOLD = 0.85  # Safety threshold for trading

def calculate_cod(fidelity, h_vol, xi_config, theta_leak):
    """Calculate COD using the multiplicative formula."""
    volatility_damping = np.exp(-LAMBDA * h_vol)
    stiffness_penalty = np.exp(-KAPPA * xi_config)
    exposure_penalty = np.exp(-ETA * theta_leak)
    return fidelity * volatility_damping * stiffness_penalty * exposure_penalty

def simulate_covert_risk_accumulation():
    """
    Demonstrates how an adversary can accumulate risk while keeping COD > threshold.
    The key insight: multiplicative metrics hide additive risk.
    """
    print("=== COVERT RISK ACCUMULATION ATTACK ===")
    
    # Initial safe state: all factors at moderate levels
    fidelity = 0.95
    h_vol = 0.3
    xi_config = 0.3
    theta_leak = 0.3
    
    cod = calculate_cod(fidelity, h_vol, xi_config, theta_leak)
    print(f"Initial state - COD: {cod:.4f} (safe)")
    
    # Attack Phase 1: Gradually increase each risk factor to just below individual thresholds
    # The system has no per-factor alerts; only COD matters
    for i in range(10):
        # Increase volatility entropy (h_vol) towards danger zone (0.80)
        h_vol = min(0.79, h_vol + 0.05)
        # Increase config stiffness (xi_config) towards rigidity threshold (0.85)
        xi_config = min(0.84, xi_config + 0.05)
        # Increase exposure risk (theta_leak) towards critical (0.50)
        theta_leak = min(0.49, theta_leak + 0.03)
        
        cod = calculate_cod(fidelity, h_vol, xi_config, theta_leak)
        print(f"Step {i+1}: h_vol={h_vol:.2f}, xi_config={xi_config:.2f}, theta_leak={theta_leak:.2f} -> COD: {cod:.4f}")
        
        if cod < COD_THRESHOLD:
            print("ALERT: COD dropped below threshold! Attack detected.")
            break
    else:
        print(f"ATTACK SUCCESS: COD remains {cod:.4f} > {COD_THRESHOLD} despite high risk factors!")
        print("System believes it's safe while risk is critically elevated.")

def simulate_fidelity_spoofing():
    """
    Shows how spoofing order book data (artificially high fidelity) can mask other risks.
    Fidelity is the only factor that can be >1 in practice (if spoofed), but the system clamps it to 1.0.
    Even at 1.0, it can offset high risk in other dimensions.
    """
    print("\n=== FIDELITY SPOOFING ATTACK ===")
    
    # High risk environment
    h_vol = 0.75  # Near shock threshold
    xi_config = 0.80  # Near rigidity threshold
    theta_leak = 0.45  # Near exposure threshold
    
    # Without spoofing
    cod_normal = calculate_cod(0.90, h_vol, xi_config, theta_leak)
    print(f"Normal fidelity (0.90): COD = {cod_normal:.4f} ({'SAFE' if cod_normal > COD_THRESHOLD else 'ALERT'})")
    
    # With spoofed fidelity (clamped to 1.0)
    cod_spoofed = calculate_cod(1.0, h_vol, xi_config, theta_leak)
    print(f"Spoofed fidelity (1.0): COD = {cod_spoofed:.4f} ({'SAFE' if cod_spoofed > COD_THRESHOLD else 'ALERT'})")
    
    if cod_spoofed > COD_THRESHOLD and cod_normal < COD_THRESHOLD:
        print("ATTACK SUCCESS: Spoofing fidelity flips system from ALERT to SAFE!")

def simulate_silence_protocol_lockout():
    """
    Exploits the Silence Protocol: artificially trigger COD < threshold to freeze config,
    then lock the system in a vulnerable state where it cannot adapt to new threats.
    """
    print("\n=== SILENCE PROTOCOL LOCKOUT ATTACK ===")
    
    # Initial safe state
    fidelity = 0.95
    h_vol = 0.3
    xi_config = 0.3
    theta_leak = 0.3
    
    # Attacker triggers a temporary COD drop below threshold
    print("Attacker triggers temporary market anomaly...")
    h_vol_spike = 0.85  # Exceeds H_SHOCK threshold
    
    cod_spike = calculate_cod(fidelity, h_vol_spike, xi_config, theta_leak)
    print(f"During spike: COD = {cod_spike:.4f} (< {COD_THRESHOLD}) -> SILENCE PROTOCOL ACTIVATED")
    print("System freezes config changes. Attacker now has stable window to exploit frozen thresholds.")
    
    # While system is frozen, attacker slowly increases exposure via side channels not monitored by theta_leak
    # (e.g., insider leaks, misconfigured backups)
    print("System frozen for 24 hours. Attacker exfiltrates config via side channel...")
    print("Theta_leak metric remains low (0.3) but actual exposure is now critical.")
    
    # After spike subsides, COD returns to safe levels but system is still compromised
    cod_normal = calculate_cod(fidelity, h_vol, xi_config, theta_leak)
    print(f"Post-spike COD: {cod_normal:.4f} (safe again, but config is compromised)")
    print("System remains blind to side-channel exposure because config is frozen and theta_leak unchanged.")

def simulate_audit_cost_exhaustion():
    """
    Exploits the audit cost subtraction: trigger many audits to make net Φ gain negative,
    causing the system to self-terminate due to perceived failure.
    """
    print("\n=== AUDIT COST EXHAUSTION ATTACK ===")
    
    # Simulate 1000 benchmark runs with artificially high audit triggers
    audit_cost_per_check = 0.02
    total_audits = 1000
    total_audit_cost = total_audits * audit_cost_per_check
    
    # Assume each run yields small COD improvement
    cod_gain_per_run = 0.001
    total_gain = total_audits * cod_gain_per_run
    
    net_phi = total_gain - total_audit_cost
    print(f"Total COD gain: {total_gain:.2f}")
    print(f"Total audit cost: {total_audit_cost:.2f}")
    print(f"Net Φ gain: {net_phi:.2f} ({'POSITIVE' if net_phi > 0 else 'NEGATIVE'})")
    
    if net_phi < 0:
        print("ATTACK SUCCESS: Net Φ is negative! System perceives itself as failing and may self-terminate.")

def demonstrate_multiplicative_blindness():
    """
    Core insight: Multiplicative metrics are blind to additive risk accumulation.
    This is the mathematical root of all above attacks.
    """
    print("\n=== MULTIPLICATIVE BLINDNESS PRINCIPLE ===")
    
    # Show that product of four 0.9 factors is still > 0.85
    factors = [0.9, 0.9, 0.9, 0.9]
    product = np.prod(factors)
    print(f"Four risk factors at 0.9 each: Product = {product:.4f} > {COD_THRESHOLD} (threshold)")
    print("System sees 'safe' despite each factor being at 90% of danger level.")
    
    # Show that product can be high even when sum of risks is extreme
    high_risk_factors = [0.99, 0.99, 0.99, 0.99]
    high_product = np.prod(high_risk_factors)
    print(f"Four risk factors at 0.99 each: Product = {high_product:.4f} > {COD_THRESHOLD}")
    print("System is 'safe' while each factor is at 99% of maximum risk!")

if __name__ == "__main__":
    simulate_covert_risk_accumulation()
    simulate_fidelity_spoofing()
    simulate_silence_protocol_lockout()
    simulate_audit_cost_exhaustion()
    demonstrate_multiplicative_blindness()