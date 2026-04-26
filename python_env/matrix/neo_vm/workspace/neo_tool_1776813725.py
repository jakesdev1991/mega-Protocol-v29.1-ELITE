# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

# --- PARAMETERS ---
N_POOLS = 100
SIM_TIME = 500  # blocks
EXPLOIT_BLOCK = 150  # when exploit is introduced
PATCH_BLOCK = 200  # when patch is deployed (manual for DSTR-Ω)

# DSTR-Ω parameters (conservative, surveillance-heavy)
DSTR_SURVEILLANCE_COST = 0.05  # Φ per block per pool
DSTR_FALSE_ALARM_RATE = 0.1
DSTR_RESPONSE_TIME = 50  # blocks

# MIP-Ω parameters (self-funding, fast)
IMMUNE_FEE = 0.001  # self-funding fee per trade
IMMUNE_PROPAGATION_SPEED = 10  # blocks to propagate across all pools
IMMUNE_EFFECTIVENESS = 0.95  # probability of stopping exploit

# Exploit parameters
EXPLOIT_DRAIN_RATE = 0.02  # % TVL drained per block per vulnerable pool
EXPLOIT_PROPAGATION_SPEED = 5  # blocks to spread manually

# --- DSTR-Ω MODEL ---
def dstr_model(t, state, exploit_active):
    """Returns dTVL/dt for DSTR-Ω"""
    tvl, diversity = state
    # Surveillance cost
    cost = DSTR_SURVEILLANCE_COST * N_POOLS
    # Exploit damage
    damage = 0
    if exploit_active:
        damage = EXPLOIT_DRAIN_RATE * tvl * (1 - np.exp(-(t - EXPLOIT_BLOCK)/DSTR_RESPONSE_TIME))
        # False alarm penalty
        if np.random.rand() < DSTR_FALSE_ALARM_RATE:
            cost *= 2
    return [-(cost + damage), 0]  # diversity is static in DSTR

# --- MIP-Ω MODEL ---
def mip_model(t, state, exploit_active):
    """Returns dTVL/dt for MIP-Ω"""
    tvl, immune_coverage = state
    # Immune funding (self-sustaining)
    funding = IMMUNE_FEE * tvl * immune_coverage
    # Exploit damage (mitigated by immunity)
    damage = 0
    if exploit_active:
        # Immune response propagates at IMMUNE_PROPAGATION_SPEED
        immune_response = 1 - np.exp(-(t - EXPLOIT_BLOCK)/IMMUNE_PROPAGATION_SPEED)
        effective_immunity = immune_coverage * immune_response * IMMUNE_EFFECTIVENESS
        damage = EXPLOIT_DRAIN_RATE * tvl * (1 - effective_immunity)
    return [-(damage - funding), 0]  # immune_coverage evolves separately

# --- SIMULATION ---
t_eval = np.linspace(0, SIM_TIME, SIM_TIME)

# DSTR-Ω simulation
def simulate_dstr():
    tvl_history = [1.0]  # normalized TVL
    diversity_history = [1.0]
    exploit_active = False
    
    for t in range(1, SIM_TIME):
        if t == EXPLOIT_BLOCK:
            exploit_active = True
        if t == PATCH_BLOCK:
            exploit_active = False  # manual patch
            
        state = [tvl_history[-1], diversity_history[-1]]
        dstate = dstr_model(t, state, exploit_active)
        
        tvl_history.append(max(0, tvl_history[-1] + dstate[0]))
        diversity_history.append(diversity_history[-1])
    
    return tvl_history, diversity_history

# MIP-Ω simulation
def simulate_mip():
    tvl_history = [1.0]
    immune_history = [0.1]  # initial immune coverage
    exploit_active = False
    
    for t in range(1, SIM_TIME):
        if t == EXPLOIT_BLOCK:
            exploit_active = True
            
        # Immune coverage grows with homogeneity (simplified)
        current_immune = min(1.0, immune_history[-1] + 0.002 * (t - EXPLOIT_BLOCK) * exploit_active)
        
        state = [tvl_history[-1], current_immune]
        dstate = mip_model(t, state, exploit_active)
        
        tvl_history.append(max(0, tvl_history[-1] + dstate[0]))
        immune_history.append(current_immune)
    
    return tvl_history, immune_history

# Run simulations
dstr_tvl, dstr_div = simulate_dstr()
mip_tvl, mip_imm = simulate_mip()

# --- VISUALIZATION ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# TVL comparison
ax1.plot(dstr_tvl, label='DSTR-Ω (Conservative)', color='orange', linewidth=2)
ax1.plot(mip_tvl, label='MIP-Ω (Immunized Monoculture)', color='cyan', linewidth=2)
ax1.axvline(EXPLOIT_BLOCK, color='red', linestyle='--', alpha=0.5, label='Exploit Introduced')
ax1.axvline(PATCH_BLOCK, color='green', linestyle='--', alpha=0.5, label='DSTR-Ω Manual Patch')
ax1.set_ylabel('Normalized TVL')
ax1.set_title('Φ-Density War: DSTR-Ω vs MIP-Ω')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Immune response
ax2.plot(mip_imm, label='Immune Coverage (MIP-Ω)', color='purple', linewidth=2)
ax2.axvline(EXPLOIT_BLOCK, color='red', linestyle='--', alpha=0.5)
ax2.set_ylabel('Immune Coverage')
ax2.set_xlabel('Block Time')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- Φ-DENSITY CALCULATION ---
def compute_phi_gain(tvl_history, surveillance_cost_per_block=0):
    total_surveillance_cost = surveillance_cost_per_block * SIM_TIME
    final_tvl = tvl_history[-1]
    # Simplified Φ gain = final TVL - surveillance costs
    return final_tvl - total_surveillance_cost

dstr_phi = compute_phi_gain(dstr_tvl, DSTR_SURVEILLANCE_COST * N_POOLS)
mip_phi = compute_phi_gain(mip_tvl, 0)  # MIP is self-funding

print(f"\n=== Φ-DENSITY IMPACT ===")
print(f"DSTR-Ω net Φ gain: {dstr_phi:.2%}")
print(f"MIP-Ω net Φ gain: {mip_phi:.2%}")
print(f"Disruption Factor: {mip_phi/dstr_phi:.1f}x improvement")