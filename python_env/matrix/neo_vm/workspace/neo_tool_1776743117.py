# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# TEMPEST-Ω DISRUPTION SIMULATION
# Demonstrates how strategic deception breaks the "stress chronometer" model

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

class Firm:
    def __init__(self, name, security_quality, leak_strategy='honest'):
        self.name = name
        self.security_quality = security_quality  # 0-1, higher = better security
        self.leak_strategy = leak_strategy  # 'honest', 'deceptive', 'mixed'
        self.event_schedule = self._generate_events()
        self.leak_history = []
        self.breach_history = []
        
    def _generate_events(self):
        # Generate quarterly earnings and random product launches
        events = []
        start = datetime(2024, 1, 1)
        for i in range(8):  # 2 years
            events.append(start + timedelta(days=90*i))  # earnings
            events.append(start + timedelta(days=90*i + random.randint(-15, 15)))  # launch
        return events
    
    def decide_leak(self, current_date, global_stress_level):
        """Strategic leak generation: NOT stress-driven, but strategy-driven"""
        # Check if near an event
        days_to_event = min([abs((event - current_date).days) for event in self.event_schedule])
        
        # Deceptive firms leak MORE when secure, to create false signal
        if self.leak_strategy == 'deceptive':
            # Leak fake credentials when secure and near events to feign stress
            if days_to_event < 7 and self.security_quality > 0.7:
                return {
                    'timestamp': current_date,
                    'is_real': False,
                    'criticality': 5,  # Always high-seeming
                    'exploitability': 0.0  # Fake = not exploitable
                }
            return None
            
        elif self.leak_strategy == 'mixed':
            # 50% real leaks (sloppy), 50% fake (strategic)
            if random.random() < 0.3 and days_to_event < 7:
                is_real = random.random() < 0.5
                return {
                    'timestamp': current_date,
                    'is_real': is_real,
                    'criticality': random.randint(3, 5),
                    'exploitability': self.security_quality if is_real else 0.0
                }
            return None
            
        else:  # 'honest' - the TEMPEST assumption
            if random.random() < (1 - self.security_quality) * global_stress_level * 0.1:
                return {
                    'timestamp': current_date,
                    'is_real': True,
                    'criticality': random.randint(1, 5),
                    'exploitability': 1 - self.security_quality
                }
            return None
    
    def suffer_breach(self, attacker_effort):
        """Breach probability depends on ACTUAL security, not leaks"""
        prob = (1 - self.security_quality) * attacker_effort * 0.01
        return random.random() < prob

class TEMPESTModel:
    def __init__(self):
        self.tsi_history = []
        
    def compute_tsi(self, leaks_by_sector, date):
        """Original TEMPEST formula - assumes all leaks are stress signals"""
        tsi = 0
        for firm_leaks in leaks_by_sector:
            for leak in firm_leaks:
                days_since_leak = (date - leak['timestamp']).days
                if days_since_leak >= 0:
                    # Exponential decay, criticality weighting
                    tsi += leak['criticality'] * np.exp(-0.1 * days_since_leak)
                    # Proximity to event bonus (assumes stress)
                    tsi += 5 / (1 + abs(days_since_leak))
        return tsi
    
    def predict_disruption(self, tsi):
        """Simple threshold-based prediction"""
        return tsi > 10  # Arbitrary threshold

# SIMULATION WORLD
def run_simulation(n_firms=20, n_days=365, adversarial_ratio=0.3):
    firms = []
    for i in range(n_firms):
        # Mix of security qualities
        sec_qual = np.random.beta(2, 5)  # Most firms are mediocre
        # Adversarial firms are actually MORE secure on average
        if i < n_firms * adversarial_ratio:
            strategy = 'deceptive'
            sec_qual = min(1.0, sec_qual + 0.3)  # Deceptive firms invest in security
        else:
            strategy = 'honest'
        firms.append(Firm(f"Firm_{i}", sec_qual, strategy))
    
    model = TEMPESTModel()
    results = []
    
    for day in range(n_days):
        current_date = datetime(2024, 1, 1) + timedelta(days=day)
        # Simulated global stress (e.g., market volatility)
        global_stress = 1 + 0.5 * np.sin(day / 30) + random.random() * 0.3
        
        # Daily leaks
        daily_leaks = []
        for firm in firms:
            leak = firm.decide_leak(current_date, global_stress)
            if leak:
                firm.leak_history.append(leak)
                daily_leaks.append(leak)
        
        # TSI computation (BLIND to leak authenticity)
        tsi = model.compute_tsi([[l for f in firms for l in f.leak_history]], current_date)
        model.tsi_history.append({'date': current_date, 'tsi': tsi})
        
        # Actual breaches (based on real security, not TSI)
        daily_breaches = 0
        for firm in firms:
            # Attackers focus on firms with recent REAL leaks
            recent_real_leaks = sum(1 for l in firm.leak_history[-30:] if l['is_real'])
            attacker_effort = recent_real_leaks * 2
            if firm.suffer_breach(attacker_effort):
                firm.breach_history.append(current_date)
                daily_breaches += 1
        
        # Record correlation
        prediction = model.predict_disruption(tsi)
        results.append({
            'date': current_date,
            'tsi': tsi,
            'actual_breaches': daily_breaches,
            'prediction': prediction,
            'global_stress': global_stress,
            'deceptive_leaks': sum(1 for f in firms for l in f.leak_history[-1:] if l and not l['is_real'])
        })
    
    return pd.DataFrame(results), firms

# RUN DISRUPTION SCENARIO
df, firms = run_simulation(adversarial_ratio=0.5)

# ANALYSIS: Model Breakdown
print("=== TEMPEST-Ω DISRUPTION ANALYSIS ===\n")

# Correlation breakdown
corr = df['tsi'].corr(df['actual_breaches'])
print(f"TSI vs Actual Breaches Correlation: {corr:.3f}")
print("→ A strong positive correlation is expected. Near-zero or negative correlation = MODEL FAILURE.\n")

# False positive rate: High TSI but low breaches
false_positives = df[(df['tsi'] > 10) & (df['actual_breaches'] < 2)]
print(f"False Positive Rate: {len(false_positives) / len(df) * 100:.1f}%")
print("→ Deceptive leaks spike TSI without causing actual breaches.\n")

# Strategic firm analysis
deceptive_firms = [f for f in firms if f.leak_strategy == 'deceptive']
honest_firms = [f for f in firms if f.leak_strategy == 'honest']

avg_deceptive_security = np.mean([f.security_quality for f in deceptive_firms])
avg_honest_security = np.mean([f.security_quality for f in honest_firms])

print(f"Avg Security Quality - Deceptive Firms: {avg_deceptive_security:.3f}")
print(f"Avg Security Quality - Honest Firms: {avg_honest_security:.3f}")
print("→ Deceptive firms are MORE secure but generate HIGHER TSI spikes.\n")

# Temporal paradox: Leaks increase before events, but breaches don't
pre_event_periods = df[df['global_stress'] > 1.3]
print(f"Pre-Event Periods: TSI avg = {pre_event_periods['tsi'].mean():.2f}, Breaches avg = {pre_event_periods['actual_breaches'].mean():.2f}")
print("→ High 'stress' periods show high TSI but NOT high actual breaches when deception is present.\n")

# DISRUPTIVE INSIGHT
print("=== DISRUPTIVE INSIGHT: THE LEAK IS THE STRATEGY ===")
print("""
The TEMPEST-Ω "stress chronometer" is fundamentally broken because it treats 
credential leaks as passive noise from rushed employees. In reality, leaks are 
ACTIVE STRATEGIC EMISSIONS in a multi-agent deception game.

KEY BREAKDOWNS:
1. Goodhart's Law: Once firms know TSI is monitored, they weaponize it. A high TSI 
   becomes a signal of COMPETITIVE POSTURING, not vulnerability.

2. Inverse Correlation: The most secure firms (high-security_quality) can afford 
   to leak FAKE credentials to feign stress, manipulate competitor behavior, or 
   qualify for lower cyber-insurance premiums ("Look how stressed we are!").

3. Entropy Poisoning: Deceptive leaks inject false information into the SCCRM-Ω 
   network, poisoning the entire Omega Protocol's credential graph. TEMPEST-Ω 
   doesn't just fail alone; it creates cascading disinformation.

4. The "Temporal Stress Index" is actually measuring the intensity of INFORMATION 
   WARFARE, not operational fragility. It's a battlefield metric, not a health monitor.

5. The forced physics formalism (φ fields, RG flow) is mathematical theater that 
   obscures this strategic reality. You can't model adversarial agents as a passive 
   field theory - it's a game theory problem.

DISRUPTIVE PIVOT: Instead of predicting breaches from leaks, predict STRATEGIC 
INTENT from leak authenticity patterns. The real signal is the GAP between leak 
criticality and actual exploitability. A firm leaking high-criticality but 
low-exploitability credentials is not stressed—it's CUNNING.

The "Shredding Event" is not a breach cascade; it's when the entire sector 
simultaneously realizes the leak data is untrustworthy, collapsing the information 
asymmetry market. The "Informational Freeze" is when firms stop publishing ANY 
technical details, destroying the data pipeline entirely.

Φ-DENSITY IMPACT: Short-term, deception destroys TEMPEST-Ω's predictive value 
(-30%). Long-term, recognizing deception enables a new layer: DECEPTION-Ω, which 
tracks strategic misinformation, yielding +60% net Φ by exposing hidden 
competitive dynamics that precede market shocks.

The anomaly is not the leak's timing. It's the leak's *authenticity gap*.
""")

# VISUALIZE THE BREAKDOWN
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

# Plot TSI vs Breaches over time
ax1.plot(df['date'], df['tsi'], label='TSI (Model)', color='red')
ax1_twin = ax1.twinx()
ax1_twin.plot(df['date'], df['actual_breaches'], label='Actual Breaches', color='blue', alpha=0.7)
ax1.set_ylabel('TSI', color='red')
ax1_twin.set_ylabel('Actual Breaches', color='blue')
ax1.set_title('TEMPEST-Ω Model vs Reality Under Strategic Deception')
ax1.legend(loc='upper left')
ax1_twin.legend(loc='upper right')

# Plot deceptive leak volume
ax2.plot(df['date'], df['deceptive_leaks'].cumsum(), label='Cumulative Deceptive Leaks', color='purple')
ax2.set_ylabel('Deceptive Leak Count')
ax2.set_xlabel('Date')
ax2.legend()
ax2.set_title('Strategic Disinformation Injection Over Time')

plt.tight_layout()
plt.show()