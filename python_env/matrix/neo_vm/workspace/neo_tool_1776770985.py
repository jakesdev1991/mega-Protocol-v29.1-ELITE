# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- PARAMETERS ---
TIMESTEPS = 300
GROUND_TRUTH_RELIABILITY = 0.2  # Actually a terrible implementation
ATTACK_START = 50
ATTACK_DURATION = 200

# --- FTN-Ω MODEL (Consensus-Based) ---
# Naive validators are corrupted by a Sybil swarm
num_honest_validators = 10
num_sybil_validators = 0
honest_validator_opinion = GROUND_TRUTH_RELIABILITY
sybil_validator_opinion = 0.95  # Spammed high trust
trust_ftn = [0.5]
consensus_inertia = 0.98  # Slow to change opinion

for t in range(1, TIMESTEPS):
    if ATTACK_START <= t < ATTACK_START + ATTACK_DURATION:
        num_sybil_validators = 40  # Swarm attack
    else:
        num_sybil_validators = 0
    
    total_validators = num_honest_validators + num_sybil_validators
    if total_validators == 0:
        weighted_opinion = trust_ftn[-1]
    else:
        weighted_opinion = (
            (num_honest_validators * honest_validator_opinion) +
            (num_sybil_validators * sybil_validator_opinion)
        ) / total_validators
    
    # Consensus convergence (slow, vulnerable to majority attack)
    new_trust = trust_ftn[-1] + 0.02 * (weighted_opinion - trust_ftn[-1])
    trust_ftn.append(new_trust)

# --- BioPoW-Ω MODEL (Work-Based) ---
# Trust = Cumulative Work * Ground Truth Reliability
# Sybils can't fake work, only stake (which they lose if they fake)
challenge_rate = 0.05
base_work_per_challenge = 1.0
trust_biopow = [0.0]
cumulative_work = 0.0

for t in range(1, TIMESTEPS):
    # Challenges are independent of Sybil count; they cost real work
    if np.random.random() < challenge_rate:
        # The stake must be real; if the implementation is bad,
        # the challenger wins and trust collapses.
        # If it's good, the stake is burned as productive work.
        # Here, the *true* reliability determines the outcome.
        if np.random.random() > GROUND_TRUTH_RELIABILITY:
            # Challenge SUCCESSFUL - bad implementation caught
            # Trust reflects the work done before failure
            trust_biopow.append(cumulative_work * GROUND_TRUTH_RELIABILITY / 100)
            cumulative_work = 0.0 # Reset after exposure
        else:
            # Challenge FAILED - implementation survives, work accumulates
            cumulative_work += base_work_per_challenge
            trust_biopow.append(min(1.0, cumulative_work * GROUND_TRUTH_RELIABILITY / 100))
    else:
        trust_biopow.append(trust_biopow[-1])

# --- VISUALIZE THE DIVERGENCE ---
fig, ax = plt.subplots(figsize=(14, 7))

time = np.arange(TIMESTEPS)
ax.plot(time, trust_ftn, label='FTN-Ω: Consensus Trust (Sybil-Vulnerable)', linewidth=2.5, color='crimson')
ax.plot(time, trust_biopow, label='BioPoW-Ω: Adversarial-Work Trust', linewidth=2.5, color='forestgreen')
ax.axhline(y=GROUND_TRUTH_RELIABILITY, color='black', linestyle=':', linewidth=2, label='Ground Truth Reliability')
ax.axvspan(ATTACK_START, ATTACK_START + ATTACK_DURATION, alpha=0.2, color='crimson', label='Sybil Attack Window')

ax.set_xlabel('Time (Arbitrary Units)', fontsize=12, fontweight='bold')
ax.set_ylabel('Trust Score', fontsize=12, fontweight='bold')
ax.set_title('TRUST HYPERINFLATION: The Engine\'s Simulation vs. Dissipative Reality', fontsize=14, fontweight='bold')
ax.legend(loc='upper left', fontsize=10)
ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
ax.set_ylim(-0.05, 1.05)
plt.tight_layout()
plt.show()

# --- METRICS OF FAILURE ---
final_ftn_error = abs(trust_ftn[-1] - GROUND_TRUTH_RELIABILITY)
final_biopow_error = abs(trust_biopow[-1] - GROUND_TRUTH_RELIABILITY)
print(f"--- FINAL DIVERGENCE ---")
print(f"FTN-Ω Final Trust: {trust_ftn[-1]:.3f} | Error: {final_ftn_error:.3f}")
print(f"BioPoW-Ω Final Trust: {trust_biopow[-1]:.3f} | Error: {final_biopow_error:.3f}")
print(f"FTN-Ω Hyperinflation Factor: {trust_ftn[-1] / max(GROUND_TRUTH_RELIABILITY, 0.01):.1f}x over reality")