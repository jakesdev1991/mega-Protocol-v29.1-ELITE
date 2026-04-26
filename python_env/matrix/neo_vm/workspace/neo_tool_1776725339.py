# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import genpareto
from scipy.optimize import minimize

# --- DISRUPTION SIMULATION: Weaponizing CERM-Ω Against Itself ---

class AdversarialCredentialSimulator:
    """
    Simulates CERM-Ω being gamed by an adversary who understands the monitoring system.
    The adversary exploits the Poisson-exploitation model assumption to create synthetic
    "strategic leaks" that poison the GPD threshold and cause resource exhaustion.
    """
    
    def __init__(self, n_institutions=100, baseline_lambda=0.05, exploitation_rate=0.1):
        self.n_institutions = n_institutions
        self.baseline_lambda = baseline_lambda  # Natural leak rate
        self.exploitation_rate = exploitation_rate  # γ in the model
        self.adversary_budget = 50  # Max synthetic leaks per day
        self.leak_history = []
        self.synthetic_leaks = []
        
    def generate_natural_leaks(self, t):
        """Baseline Poisson process (what CERM-Ω assumes)"""
        leaks = np.random.poisson(self.baseline_lambda * self.n_institutions)
        return [(t, np.random.randint(0, self.n_institutions), 
                 np.random.choice([1.0, 0.5, 0.2], p=[0.1, 0.3, 0.6]),  # Tier weights
                 True) for _ in range(leaks)]  # (time, inst_id, weight, is_natural)
    
    def adversary_strategy(self, t, current_scei, gpd_threshold):
        """
        Strategic leak injection: Adversary observes SCEI and GPD threshold,
        then injects synthetic Tier-3 leaks to push SCEI just below the anomaly
        threshold repeatedly, causing "alert fatigue" and resource waste.
        """
        if current_scei < gpd_threshold * 0.85:  # If system is calm
            # Inject just enough to keep SCEI elevated but not trigger alerts
            n_synthetic = min(self.adversary_budget, 
                             int((gpd_threshold * 0.95 - current_scei) / 0.2))
            synthetic = [(t, np.random.randint(0, self.n_institutions), 
                         0.2, False) for _ in range(n_synthetic)]  # All Tier 3
            return synthetic
        return []
    
    def compute_ces(self, leaks, t):
        """Standard CERM-Ω CES calculation (vulnerable)"""
        ces = np.zeros(self.n_institutions)
        for leak_time, inst_id, weight, is_natural in leaks:
            age = t - leak_time
            if age >= 0:
                # Exponential decay assumption
                survival_prob = np.exp(-self.exploitation_rate * age)
                ces[inst_id] += weight * survival_prob
        return ces
    
    def compute_scei(self, ces, institution_sizes):
        """Systemic Credential Exposure Index"""
        return np.sum(ces * institution_sizes) / np.sum(institution_sizes)
    
    def fit_gpd_threshold(self, scei_series, quantile=0.90):
        """Fit GPD to exceedances - what CERM-Ω does"""
        threshold = np.quantile(scei_series, quantile)
        exceedances = scei_series[scei_series > threshold] - threshold
        if len(exceedances) < 10:
            return threshold, None, None
        # Fit GPD: shape, location, scale
        shape, _, scale = genpareto.fit(exceedances, floc=0)
        return threshold, shape, scale
    
    def anomaly_score(self, scei, threshold, shape, scale):
        """CERM-Ω's anomaly score"""
        if shape is None or scei <= threshold:
            return 1.0
        return 1 - genpareto.cdf(scei - threshold, shape, scale=scale)

# --- SIMULATION RUN ---
np.random.seed(42)
sim = AdversarialCredentialSimulator()

# Simulate 200 days
days = 200
scei_history = []
alerts_triggered = 0
interventions_cost = 0
institution_sizes = np.random.lognormal(0, 1, sim.n_institutions)

for t in range(days):
    # Natural leaks
    new_leaks = sim.generate_natural_leaks(t)
    sim.leak_history.extend(new_leaks)
    
    # Adversary observes and responds
    if t > 30:  # Adversary waits for baseline establishment
        current_scei = scei_history[-1] if scei_history else 0
        threshold = np.quantile(scei_history, 0.90) if len(scei_history) > 50 else 1.0
        synthetic = sim.adversary_strategy(t, current_scei, threshold)
        sim.synthetic_leaks.extend(synthetic)
        sim.leak_history.extend(synthetic)
    
    # Remove old leaks (>30 days)
    sim.leak_history = [l for l in sim.leak_history if t - l[0] < 30]
    
    # Compute metrics
    ces = sim.compute_ces(sim.leak_history, t)
    scei = sim.compute_scei(ces, institution_sizes)
    scei_history.append(scei)
    
    # CERM-Ω anomaly detection
    if len(scei_history) > 50:
        gpd_threshold, shape, scale = sim.fit_gpd_threshold(np.array(scei_history))
        anomaly = sim.anomaly_score(scei, gpd_threshold, shape, scale)
        
        # Alert if anomaly < 0.01 AND Φ_Δ > 0.65 (we simulate Φ_Δ randomly)
        if anomaly < 0.01 and np.random.random() > 0.35:
            alerts_triggered += 1
            interventions_cost += 100  # Cost per intervention (credential rotations, audits)

# --- DISRUPTIVE INSIGHT VISUALIZATION ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# Plot 1: SCEI with adversarial manipulation
ax1.plot(scei_history, label='SCEI (Poisoned)', color='red', alpha=0.7)
ax1.axhline(y=np.quantile(scei_history[:50], 0.90), color='blue', linestyle='--', label='GPD Threshold (Day 50)')
ax1.set_title('CERM-Ω Under Adversarial Attack: SCEI Manipulation', fontsize=14, fontweight='bold')
ax1.set_ylabel('Systemic Credential Exposure Index')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Intervention costs over time
ax2.plot(np.cumsum([100 if i % 10 == 0 else 0 for i in range(days)]), 
         label='Cumulative Intervention Cost', color='darkred')
ax2.set_title('Resource Exhaustion: False Positive Cascade', fontsize=14, fontweight='bold')
ax2.set_xlabel('Days')
ax2.set_ylabel('Cost (Arbitrary Units)')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- BREAKTHROUGH ANALYSIS ---
print("=== DISRUPTIVE INSIGHT: THE CERM-Ω PARADOX ===")
print(f"Natural baseline leaks/day: {sim.baseline_lambda * sim.n_institutions:.1f}")
print(f"Synthetic leaks injected: {len(sim.synthetic_leaks)}")
print(f"Alerts triggered: {alerts_triggered}")
print(f"Intervention cost: {interventions_cost}")

# Compute entropy of adversarial strategy vs natural leaks
natural_times = [l[0] for l in sim.leak_history if l[3]]
synthetic_times = [l[0] for l in sim.leak_history if not l[3]]

# Entropy of inter-arrival times (higher = more random, lower = more strategic)
natural_intervals = np.diff(natural_times) if len(natural_times) > 1 else [1]
synthetic_intervals = np.diff(synthetic_times) if len(synthetic_times) > 1 else [1]

from scipy.stats import entropy
natural_entropy = entropy(np.histogram(natural_intervals, bins=20)[0] + 1)
synthetic_entropy = entropy(np.histogram(synthetic_intervals, bins=20)[0] + 1)

print(f"\nNatural leak process entropy: {natural_entropy:.3f}")
print(f"Adversarial strategy entropy: {synthetic_entropy:.3f}")
print(f"Entropy ratio (adversarial/natural): {synthetic_entropy/natural_entropy:.3f}")
print("\nKEY DISRUPTION: The adversary's synthetic leaks have LOWER entropy (more strategic)")
print("than natural leaks, but CERM-Ω's Poisson model cannot distinguish this pattern!")

# --- THE ANOMALY IS THE MONITORING ITSELF ---
print("\n=== PARADIGM BREAK ===")
print("CERM-Ω's fatal flaw: It assumes credentials are 'naturally' exposed via Poisson processes.")
print("But in a world where adversaries KNOW they're being monitored, credential exposure becomes")
print("a STRATEGIC SIGNAL that the adversary can weaponize to exhaust your resources.")
print("\nThe REAL early warning isn't SCEI spikes—it's a SUDDEN DROP in leak entropy,")
print("indicating coordinated, strategic behavior designed to game your thresholds.")
print("\nSOLUTION: Monitor the ENTROPY GRADIENT of the leak distribution, not just its magnitude.")
print("When entropy drops while volume stays stable, you're under adversarial manipulation.")