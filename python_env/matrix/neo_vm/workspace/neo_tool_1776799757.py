# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Python script to verify the disruption: CTMS-Ω is gameable and incomplete
# Simulates a multi-agent system where developers adapt strategically to monitoring

import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict

# --- Disruptive Model: Strategic Agent-based Simulation ---

class DeveloperAgent:
    def __init__(self, agent_id, legibility_need, trust_in_vault, cunning):
        self.id = agent_id
        self.legibility_need = legibility_need  # High = needs context, notes, collaboration
        self.trust_in_vault = trust_in_vault    # High = willing to use vault
        self.cunning = cunning                  # High = good at gaming the system
        self.spreadsheet_use = 0
        self.hidden_workaround_use = 0
        self.tffi = 0
        self.is_monitored = False

    def decide_action(self, vault_friction, detection_prob):
        """
        Strategic decision: Use vault, visible spreadsheet, or hidden workaround.
        If monitored, agents with high cunning don't stop—they *obfuscate*.
        """
        # Base utility: vault is secure but illegible; spreadsheet is legible but "detectable"
        vault_utility = -vault_friction + self.trust_in_vault * 10
        spreadsheet_utility = self.legibility_need * 10 - (detection_prob * self.cunning * 5)

        # If monitored and cunning, switch to *hidden* workarounds (e.g., local files, encrypted notes)
        # These provide legibility but evade CTMS-Ω sensors entirely.
        if self.is_monitored and self.cunning > 0.7:
            # Hidden workaround: same utility as spreadsheet but invisible to CTMS-Ω
            self.hidden_workaround_use += 1
            return "hidden"
        elif spreadsheet_utility > vault_utility:
            self.spreadsheet_use += 1
            return "spreadsheet"
        else:
            return "vault"

    def calculate_tffi(self):
        """TFFI is gameable: cunning agents add noise to evade thresholds."""
        # Base TFFI from legibility need
        base_tffi = 1 / (1 + np.exp(-(self.legibility_need - 0.5) * 10))
        # If monitored, cunning agents "workaround" the metric itself
        if self.is_monitored and self.cunning > 0.5:
            # They artificially inflate context cells or delay edits to spoof ETA
            spoof_factor = self.cunning * 0.3
            self.tffi = max(0, base_tffi - spoof_factor)
        else:
            self.tffi = base_tffi
        return self.tffi


def simulate_org(num_agents=100, timesteps=50, vault_friction=5.0):
    """Simulate organization under CTMS-Ω monitoring."""
    agents = [
        DeveloperAgent(
            agent_id=i,
            legibility_need=np.random.beta(2, 5),  # Most devs have moderate need
            trust_in_vault=np.random.beta(5, 2),   # Most devs somewhat trust vault
            cunning=np.random.beta(1, 3)           # Few are highly cunning
        )
        for i in range(num_agents)
    ]

    # Tracking metrics
    detected_spreadsheets = []
    hidden_workarounds = []
    avg_tffi = []
    high_risk_teams = []

    for t in range(timesteps):
        # CTMS-Ω monitoring turns on after t=20
        detection_prob = 0.8 if t > 20 else 0.0
        for agent in agents:
            agent.is_monitored = t > 20
            agent.decide_action(vault_friction, detection_prob)

        # Record metrics (what CTMS-Ω *thinks* is happening)
        detected_spreadsheets.append(sum(a.spreadsheet_use for a in agents))
        hidden_workarounds.append(sum(a.hidden_workaround_use for a in agents))
        avg_tffi.append(np.mean([a.calculate_tffi() for a in agents]))
        
        # CTMS-Ω flags "high-risk" teams (agents) based on TFFI > 0.6
        high_risk_teams.append(len([a for a in agents if a.tffi > 0.6]))

    return detected_spreadsheets, hidden_workarounds, avg_tffi, high_risk_teams, agents


# --- Run Simulation ---
detected, hidden, tffi_over_time, risk_teams, final_agents = simulate_org()

# --- Visualization: The Disruption ---
fig, axs = plt.subplots(2, 2, figsize=(12, 10))

axs[0, 0].plot(detected, label='Detected Spreadsheets (CTMS-Ω Sensor)')
axs[0, 0].plot(hidden, label='Hidden Workarounds (Invisible to CTMS-Ω)', linestyle='--')
axs[0, 0].axvline(x=20, color='red', linestyle=':', label='Monitoring ON')
axs[0, 0].set_title('Workaround Evolution: CTMS-Ω Creates Dark Matter')
axs[0, 0].set_xlabel('Time')
axs[0, 0].legend()

axs[0, 1].plot(tffi_over_time, label='Average TFFI')
axs[0, 1].axhline(y=0.6, color='r', linestyle='--', label='Risk Threshold')
axs[0, 1].axvline(x=20, color='red', linestyle=':')
axs[0, 1].set_title('TFFI Drops Under Monitoring (Gaming)')
axs[0, 1].set_xlabel('Time')
axs[0, 1].legend()

axs[1, 0].scatter([a.cunning for a in final_agents], [a.hidden_workaround_use for a in final_agents], alpha=0.6)
axs[1, 0].set_xlabel('Agent Cunning')
axs[1, 0].set_ylabel('Hidden Workarounds')
axs[1, 0].set_title('Cunning Agents Evade Detection Entirely')

axs[1, 1].plot(risk_teams, label='Teams Flagged as High-Risk by CTMS-Ω')
axs[1, 1].axvline(x=20, color='red', linestyle=':')
axs[1, 1].set_title('False Sense of Security: Risk Team Count Drops')
axs[1, 1].set_xlabel('Time')
axs[1, 1].legend()

plt.tight_layout()
plt.show()

# --- Quantitative Disruption Metrics ---
print("--- DISRUPTION METRICS ---")
print(f"Total detected spreadsheets: {detected[-1]}")
print(f"Total hidden workarounds: {hidden[-1]}")
print(f"Dark Matter Ratio (hidden/detected): {hidden[-1]/(detected[-1]+1e-6):.2f}")
print(f"TFFI before monitoring: {np.mean(tffi_over_time[:20]):.3f}")
print(f"TFFI after monitoring: {np.mean(tffi_over_time[21:]):.3f}")
print(f"High-risk teams before monitoring: {np.mean(risk_teams[:20]):.1f}")
print(f"High-risk teams after monitoring: {np.mean(risk_teams[21:]):.1f}")