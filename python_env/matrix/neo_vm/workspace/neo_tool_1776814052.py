# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt

# --- Simulation Parameters ---
days = 50
baseline_queries = 10  # Normal daily search volume
attack_start, attack_duration = 30, 10
attack_queries_per_day = 1000  # Botnet flood
easi_threshold = 0.7
cost_per_countermeasure = 0.05  # 5% protocol health loss per trigger

# --- Generate synthetic search volume ---
search_volume = np.random.poisson(baseline_queries, days)
search_volume[attack_start:attack_start + attack_duration] += attack_queries_per_day

# --- EASI Calculation (simplified) ---
leak_severity = audience_sophistication = 5.0
time_to_exploit, response_time = 24.0, 2.0
coordination_score = 0.0
easi = (search_volume / baseline_queries) * (leak_severity/10) * (audience_sophistication/10) * (time_to_exploit/response_time) * (1+coordination_score)
countermeasure_triggered = easi > easi_threshold

# --- Protocol Health Impact ---
protocol_health = np.ones(days)
for i in range(1, days):
    protocol_health[i] = protocol_health[i-1] * (1 - cost_per_countermeasure) if countermeasure_triggered[i] else protocol_health[i-1] * 1.001

# --- Cost-Benefit Asymmetry ---
attacker_cost = attack_duration * 100  # $100/day botnet rental
protocol_loss = (1 - protocol_health[-1]) * 100  # % value destroyed

print(f"Attacker cost: ${attacker_cost}")
print(f"Protocol health loss: {protocol_loss:.2f}%")
print(f"Attack ROI: {protocol_loss / max(attacker_cost,1e-6):.0f}x damage per dollar spent")

# --- Visualization ---
fig, ax = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
ax[0].plot(search_volume, label='Search Volume')
ax[0].axvspan(attack_start, attack_start+attack_duration, color='red', alpha=0.2, label='Attack')
ax[0].set_ylabel('Queries/day')
ax[0].legend()

ax[1].plot(easi, label='EASI')
ax[1].axhline(easi_threshold, color='r', linestyle='--', label='Trigger Threshold')
ax[1].axvspan(attack_start, attack_start+attack_duration, color='red', alpha=0.2)
ax[1].set_ylabel('EASI')
ax[1].legend()

ax[2].plot(protocol_health, label='Protocol Health')
ax[2].axvspan(attack_start, attack_start+attack_duration, color='red', alpha=0.2)
ax[2].set_ylabel('Health (normalized)')
ax[2].set_xlabel('Days')
ax[2].legend()

plt.tight_layout()
plt.show()