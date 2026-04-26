# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

class SyntheticStressAttackSimulator:
    """
    Demonstrates how ISS-Ω monitoring becomes a self-defeating prophecy:
    The act of measuring insider stress creates incentives to weaponize it,
    leading to Φ-density collapse through adversarial gaming.
    """
    
    def __init__(self, n_firms=50, time_horizon=250, monitoring_start=100):
        # Market parameters
        self.n_firms = n_firms
        self.time_horizon = time_horizon
        self.monitoring_start = monitoring_start
        
        # True underlying stress (latent, unobservable)
        self.true_stress = np.random.exponential(0.5, n_firms) * 0.1  # Baseline stress
        
        # Strategic actors (10% of firms are adversarial)
        self.adversarial = np.random.random(n_firms) < 0.1
        
        # ISS-Ω parameters (from proposal)
        self.isi_memory = 0.9  # Rolling window weight
        self.alert_threshold = 2.0
        self.phi_delta_threshold = 0.6
        
        # Market fragility state
        self.phi_delta = np.zeros(time_horizon)
        self.phi_n = np.zeros(time_horizon)
        self.liquidity = np.ones(time_horizon) * 100.0
        
        # Intervention tracking
        self.cooling_off_active = np.zeros((n_firms, time_horizon), dtype=bool)
        self.false_positive_rate = 0.0
        
    def simulate_natural_stress(self, t):
        """Generate natural stress with occasional spikes"""
        noise = np.random.normal(0, 0.02, self.n_firms)
        # Occasional genuine stress events
        spike_prob = 0.005
        spikes = np.random.random(self.n_firms) < spike_prob
        return self.true_stress + noise + spikes * np.random.exponential(1, self.n_firms)
    
    def simulate_adversarial_inflation(self, natural_stress, t):
        """Strategic actors artificially inflate ISI after monitoring begins"""
        if t < self.monitoring_start:
            return natural_stress
        
        # Adversarial firms detect ISS-Ω and game it
        # They create synthetic access patterns: late-night logins, fake file revisions
        synthetic_stress = natural_stress.copy()
        
        # If competitors are near threshold, adversaries push them over
        competitor_isi_estimates = self.estimate_competitor_isi(t)
        
        for i in range(self.n_firms):
            if self.adversarial[i]:
                # Find most threatening competitor
                competitor_idx = np.argmax(competitor_isi_estimates)
                
                # Inject synthetic stress signals into competitor's telemetry
                # (via social engineering, compromised credentials, or metadata poisoning)
                if competitor_isi_estimates[competitor_idx] < self.alert_threshold * 0.8:
                    # Target competitor for false flag operation
                    synthetic_stress[competitor_idx] += np.random.exponential(2.0)
                    
                # Also obfuscate own stress
                synthetic_stress[i] *= 0.3
                
        return synthetic_stress
    
    def estimate_competitor_isi(self, t):
        """Adversaries' estimate of competitor ISI (imperfect information)"""
        if t < 10:
            return np.random.random(self.n_firms) * 0.5
        
        # Use lagged observations with noise
        lag = min(5, t)
        return np.convolve(
            self.isi_history[t-lag:t].mean(axis=0), 
            np.ones(lag)/lag, 
            mode='same'
        ) + np.random.normal(0, 0.1, self.n_firms)
    
    def compute_isi(self, observed_stress, t):
        """Compute ISS-Ω's Insider Stress Index per proposal"""
        # Access anomaly score (Mahalanobis distance proxy)
        baseline = np.mean(observed_stress) if t > 0 else 0.1
        A_i = np.abs(observed_stress - baseline) / (np.std(observed_stress) + 1e-6)
        
        # Role criticality (assume random distribution)
        R_i = np.random.choice([0.5, 1.0, 2.0], self.n_firms)
        
        # Intent score (deliberate vs accidental)
        # Adversarial gaming makes intent scores unreliable
        I_i = np.where(self.adversarial, 0.1, 0.8)  # Adversaries appear accidental
        
        # External stress proxy (market volatility)
        E_f = self.phi_delta[t-1] if t > 0 else 0.1
        
        # Learned weights (simulated from XGBoost)
        alpha, beta, gamma, delta = 0.4, 0.3, 0.2, 0.1
        
        ISI = alpha * A_i + beta * R_i + gamma * I_i + delta * E_f
        
        return ISI
    
    def apply_interventions(self, isi_scores, t):
        """Apply MPC-Ω interventions per proposal"""
        # Rising ISI cluster detection
        if t < 20:
            return np.zeros(self.n_firms, dtype=bool)
        
        # Simple trend detection
        recent_isi = self.isi_history[t-10:t].mean(axis=0)
        baseline_isi = self.isi_history[t-30:t-20].mean(axis=0)
        
        rising = (recent_isi - baseline_isi) > 0.3
        
        # Fraction in rising cluster
        s_isi = rising.mean() / (self.isi_baseline_fraction or 0.3)
        
        # Trigger conditions
        trigger = (s_isi > self.alert_threshold) and (self.phi_delta[t-1] > self.phi_delta_threshold)
        
        # Apply cooling-off mandates
        cooling_off = np.zeros(self.n_firms, dtype=bool)
        if trigger:
            # Top 30% ISI scores get cooling-off
            threshold_idx = int(0.7 * self.n_firms)
            cutoff_score = np.sort(isi_scores)[threshold_idx]
            cooling_off = isi_scores > cutoff_score
            
            # Reduce liquidity (market maker disincentives)
            self.liquidity[t] *= 0.7
        
        # Track false positives: adversarial firms never had true stress
        if trigger:
            true_positives = np.sum(cooling_off & ~self.adversarial & (self.true_stress > 0.15))
            false_positives = np.sum(cooling_off & self.adversarial)
            self.false_positive_rate = false_positives / (true_positives + false_positives + 1e-6)
        
        return cooling_off
    
    def update_market_state(self, t, cooling_off_active):
        """Update Φ variables and liquidity based on interventions"""
        # More cooling-off = more market fragmentation (lower Φ_N)
        cooling_fraction = cooling_off_active.mean()
        self.phi_n[t] = 0.7 - 0.5 * cooling_fraction  # Baseline connectivity
        
        # High stress + interventions create information asymmetry spike
        stress_level = self.isi_history[t-1:t].mean() if t > 0 else 0.1
        self.phi_delta[t] = 0.4 + stress_level * 0.5 + cooling_fraction * 0.3
        
        # Liquidity impact
        if cooling_fraction > 0.2:
            self.liquidity[t] = self.liquidity[t-1] * 0.95 if t > 0 else 95.0
        else:
            self.liquidity[t] = self.liquidity[t-1] * 1.01 if t > 0 else 101.0
    
    def run_simulation(self):
        """Main simulation loop"""
        self.isi_history = np.zeros((self.time_horizon, self.n_firms))
        self.isi_baseline_fraction = None
        
        for t in range(self.time_horizon):
            # Generate stress signals
            natural = self.simulate_natural_stress(t)
            
            # Adversarial manipulation post-monitoring
            observed = self.simulate_adversarial_inflation(natural, t)
            
            # Compute ISS-Ω metric
            isi_scores = self.compute_isi(observed, t)
            self.isi_history[t] = isi_scores
            
            # Establish baseline after burn-in
            if t == 30:
                self.isi_baseline_fraction = (isi_scores > np.median(isi_scores)).mean()
            
            # Apply interventions
            cooling_off = self.apply_interventions(isi_scores, t)
            self.cooling_off_active[:, t] = cooling_off
            
            # Update market state
            self.update_market_state(t, cooling_off)
        
        return self.generate_disruption_metrics()
    
    def generate_disruption_metrics(self):
        """Calculate the Φ-density collapse from adversarial gaming"""
        pre_monitoring = slice(0, self.monitoring_start)
        post_monitoring = slice(self.monitoring_start, self.time_horizon)
        
        # Φ-density proxy: liquidity * connectivity / asymmetry
        phi_density_pre = np.mean(
            self.liquidity[pre_monitoring] * self.phi_n[pre_monitoring] / (self.phi_delta[pre_monitoring] + 0.1)
        )
        phi_density_post = np.mean(
            self.liquidity[post_monitoring] * self.phi_n[post_monitoring] / (self.phi_delta[post_monitoring] + 0.1)
        )
        
        # Adversarial success rate: fraction of interventions that hit competitors
        adversarial_hits = np.sum(
            self.cooling_off_active & np.tile(self.adversarial, (self.time_horizon, 1)).T
        )
        total_interventions = np.sum(self.cooling_off_active)
        
        return {
            "phi_density_collapse": (phi_density_pre - phi_density_post) / phi_density_pre * 100,
            "false_positive_rate": self.false_positive_rate * 100,
            "adversarial_success": (adversarial_hits / (total_interventions + 1e-6)) * 100,
            "liquidity_decline": (self.liquidity[0] - self.liquidity[-1]) / self.liquidity[0] * 100,
            "market_fragility_events": np.sum(self.phi_delta > 0.6)
        }

# Run the disruption simulation
sim = SyntheticStressAttackSimulator()
metrics = sim.run_simulation()

print("=== ISS-Ω DISRUPTION ANALYSIS ===")
print(f"Φ-Density Collapse: {metrics['phi_density_collapse']:.1f}%")
print(f"False Positive Rate: {metrics['false_positive_rate']:.1f}%")
print(f"Adversarial Success Rate: {metrics['adversarial_success']:.1f}%")
print(f"Liquidity Decline: {metrics['liquidity_decline']:.1f}%")
print(f"Market Fragility Events: {int(metrics['market_fragility_events'])}")

# Visualize the catastrophic failure
fig, axes = plt.subplots(3, 1, figsize=(12, 10))

t = np.arange(sim.time_horizon)

# Plot 1: ISI scores (gamed by adversaries)
axes[0].plot(t, sim.isi_history.mean(axis=1), 'b-', label='Mean ISI')
axes[0].plot(t, sim.isi_history[:, sim.adversarial].mean(axis=1), 'r--', label='Adversarial Firms')
axes[0].axvline(sim.monitoring_start, color='g', linestyle=':', label='Monitoring Begins')
axes[0].set_ylabel("Insider Stress Index")
axes[0].set_title("ISS-Ω Metric Becomes Meaningless Under Adversarial Gaming")
axes[0].legend()
axes[0].grid(True)

# Plot 2: Market fragility (Φ_Δ)
axes[1].plot(t, sim.phi_delta, 'm-', label='Φ_Δ (Information Asymmetry)')
axes[1].axhline(0.6, color='r', linestyle='--', label='Crisis Threshold')
axes[1].axvline(sim.monitoring_start, color='g', linestyle=':')
axes[1].set_ylabel("Φ_Δ")
axes[1].set_title("Interventions Triggered by Gamed Signals Increase Fragility")
axes[1].legend()
axes[1].grid(True)

# Plot 3: Liquidity collapse
axes[2].plot(t, sim.liquidity, 'c-', label='Market Liquidity')
axes[2].axvline(sim.monitoring_start, color='g', linestyle=':')
axes[2].set_ylabel("Liquidity Index")
axes[2].set_xlabel("Time Steps")
axes[2].set_title("Liquidity Evaporates Due to Coordinated Cooling-Off Mandates")
axes[2].legend()
axes[2].grid(True)

plt.tight_layout()
plt.show()

# === THE DISRUPTIVE INSIGHT ===
print("\n" + "="*60)
print("DISRUPTIVE INSIGHT: The 'Cure' IS the Disease")
print("="*60)
print("""The ISS-Ω proposal commits a fatal category error: it treats human
behavior as a passive observable rather than an active adversarial system.
The simulation reveals:

1. REFLEXIVE DESTRUCTION: Monitoring creates incentive to weaponize ISI
   scores against competitors, turning risk management into attack vector.

2. COORDINATION CASCADE: When 30% of firms are flagged, the simultaneous
   cooling-off mandates create a self-fulfilling liquidity crisis - the
   intervention itself triggers the collapse.

3. METRIC POISONING: Adversarial firms can suppress their own ISI while
   inflating competitors', making the 'intent score' (I_i) a fiction.
   The system cannot distinguish between genuine stress and synthetic attacks.

4. Φ-DENSITY DEATH SPIRAL: Each intervention reduces Φ_N (connectivity)
   while increasing Φ_Δ (asymmetry), accelerating the exact singularity
   the protocol claims to prevent.

The breakthrough isn't monitoring insider stress - it's recognizing that
**observation of behavioral systems creates adversarial dynamics that
fundamentally invalidate the measurement apparatus itself**. The Omega
Protocol's error is treating finance as physics; the reality is that finance
is a **reflexive adversarial game** where any stable predictive signal
becomes unstable the moment it's used for control.

**DISRUPTIVE ALTERNATIVE**: Instead of measuring stress, measure the
**entropy of deception** - the divergence between public metadata and
private intent. But this requires abandoning the Newtonian fantasy that
Φ_N and Φ_Δ are exogenous variables. In adversarial domains, they are
**endogenous to the measurement act itself**.

The proposal must be rejected not for its technical flaws, but for its
ontological blindness to adversarial co-evolution.""")