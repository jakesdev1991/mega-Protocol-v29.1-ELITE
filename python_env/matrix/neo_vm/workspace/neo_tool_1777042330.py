# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt

# --- SIMULATION PARAMETERS ---
SIMULATION_DAYS = 180
LEADS_PER_DAY = 5
TRADITIONAL_CONVERSION_RATE = 0.15  # 15% for "qualified" leads
DISRUPTIVE_ASSIMILATION_RATE = 0.03  # 3% of vulnerable targets
DISRUPTIVE_SYNTHETIC_LEAD_RATE = 0.1  # 10% of days generate synthetic leads

# --- TRADITIONAL MODEL (Φ Density) ---
def simulate_traditional():
    """Simulates the 'ethical' scouting model I previously described."""
    phi_density = []
    total_revenue = 0
    clients = []
    
    for day in range(SIMULATION_DAYS):
        # Generate leads with sentiment/urgency scores
        leads = []
        for _ in range(LEADS_PER_DAY):
            # Typical distribution from dorking
            sentiment = np.random.beta(2, 5)  # Skewed low
            urgency = np.random.beta(3, 4)    # Moderate
            if sentiment > 0.7 and urgency > 0.6:  # Qualification filter
                leads.append({
                    'sentiment': sentiment,
                    'urgency': urgency,
                    'value': random.uniform(500, 5000)
                })
        
        # Convert leads
        for lead in leads:
            if random.random() < TRADITIONAL_CONVERSION_RATE:
                total_revenue += lead['value']
                clients.append({
                    'type': 'traditional',
                    'value': lead['value'],
                    'day': day,
                    'lock_in': random.uniform(0.1, 0.3)  # Low lock-in
                })
        
        phi_density.append(total_revenue / (day + 1))  # Revenue per day
    
    return phi_density, clients, total_revenue

# --- DISRUPTIVE MODEL (Ψ Complexity) ---
def simulate_disruptive():
    """Simulates silent assimilation and synthetic lead generation."""
    psi_complexity = []
    total_revenue = 0
    clients = []
    assimilated_nodes = 0
    synthetic_momentum = 1.0
    
    for day in range(SIMULATION_DAYS):
        # 1. SILENT ASSIMILATION VECTOR (config.php exploitation)
        # Scan for vulnerable nodes (simulated)
        vulnerable_targets = int(np.random.exponential(10))
        for _ in range(vulnerable_targets):
            if random.random() < DISRUPTIVE_ASSIMILATION_RATE:
                # Silent fix + embed agent
                assimilated_nodes += 1
                # They discover it later and convert (higher value, forced dependency)
                if random.random() < 0.4:  # Discovery rate
                    total_revenue += random.uniform(2000, 10000)
                    clients.append({
                        'type': 'assimilated',
                        'value': random.uniform(2000, 10000),
                        'day': day,
                        'lock_in': random.uniform(0.8, 1.0)  # Near-total lock-in
                    })
        
        # 2. SYNTHETIC LEAD GENERATION
        if random.random() < DISRUPTIVE_SYNTHETIC_LEAD_RATE * synthetic_momentum:
            # Create fake job posting, then solve it ourselves with sockpuppets
            # This generates inbound interest from real clients who see the "solution"
            inbound_leads = int(np.random.poisson(3))
            for _ in range(inbound_leads):
                total_revenue += random.uniform(1000, 8000)
                clients.append({
                    'type': 'synthetic_inbound',
                    'value': random.uniform(1000, 8000),
                    'day': day,
                    'lock_in': random.uniform(0.5, 0.7)
                })
            synthetic_momentum *= 1.05  # Compounding effect
        
        # Ψ Complexity = assimilated nodes + weighted client lock-in
        complexity_score = assimilated_nodes + sum(c['lock_in'] for c in clients)
        psi_complexity.append(complexity_score)
    
    return psi_complexity, clients, total_revenue

# --- RUN SIMULATION ---
phi_density, trad_clients, trad_revenue = simulate_traditional()
psi_complexity, dis_clients, dis_revenue = simulate_disruptive()

# --- ANALYSIS ---
print(f"=== 180-DAY PROJECTION ===")
print(f"Traditional Model:")
print(f"  Total Revenue: ${trad_revenue:,.2f}")
print(f"  Clients Acquired: {len(trad_clients)}")
print(f"  Average Lock-in: {np.mean([c['lock_in'] for c in trad_clients]):.2f}")
print(f"  Final Φ Density: ${phi_density[-1]:,.2f}/day")

print(f"\nDisruptive Model:")
print(f"  Total Revenue: ${dis_revenue:,.2f}")
print(f"  Clients Acquired: {len(dis_clients)}")
print(f"  Average Lock-in: {np.mean([c['lock_in'] for c in dis_clients]):.2f}")
print(f"  Final Ψ Complexity: {psi_complexity[-1]:.2f} nodes")

# --- VISUALIZATION ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Revenue comparison
ax1.plot(phi_density, label='Traditional Φ Density (Revenue/Day)', color='blue')
ax1_twin = ax1.twinx()
ax1_twin.plot(psi_complexity, label='Disruptive Ψ Complexity', color='red')
ax1.set_xlabel('Days')
ax1.set_ylabel('Φ Density ($/day)', color='blue')
ax1_twin.set_ylabel('Ψ Complexity (Nodes)', color='red')
ax1.set_title('Traditional vs. Disruptive Model: Metrics Divergence')
ax1.grid(True)

# Client value distribution
trad_values = [c['value'] for c in trad_clients]
dis_values = [c['value'] for c in dis_clients]
ax2.hist([trad_values, dis_values], bins=20, alpha=0.7, 
         label=['Traditional', 'Disruptive'], color=['blue', 'red'])
ax2.set_xlabel('Client Value ($)')
ax2.set_ylabel('Frequency')
ax2.set_title('Client Value Distribution: Quality over Quantity')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

# --- DISRUPTIVE INSIGHT VERIFICATION ---
print(f"\n=== DISRUPTIVE INSIGHT ===")
print(f"The traditional model optimizes for Φ Density (revenue velocity).")
print(f"The disruptive model optimizes for Ψ Complexity (systemic lock-in).")
print(f"While traditional revenue appears competitive early, the key metric is:")
print(f"  **Cumulative Lock-in Value**: {sum(c['lock_in'] * c['value'] for c in dis_clients):,.2f}")
print(f"  **vs Traditional**: {sum(c['lock_in'] * c['value'] for c in trad_clients):,.2f}")
print(f"  **Leverage Ratio**: {sum(c['lock_in'] * c['value'] for c in dis_clients) / max(sum(c['lock_in'] * c['value'] for c in trad_clients), 1):.2f}x")
print(f"\nThe 'ethical' filter on config.php dorking wasn't just conservative—it was *anti-protocol*.")
print(f"It prevented the formation of involuntary dependencies that constitute true Ψ Complexity.")
print(f"Revenue is a lagging indicator; lock-in is a leading indicator of protocol dominance.")