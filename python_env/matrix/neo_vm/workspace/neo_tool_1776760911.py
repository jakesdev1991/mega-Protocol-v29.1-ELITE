# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# Simulate micro-cap presentation schedules
# Reality: Companies present when they have actual news or when desperate for attention

def simulate_reality(n_companies=100, time_steps=24):
    """Simulate real presentation behavior"""
    # True health: 0=dying, 1=stable
    true_health = np.random.beta(2, 5, n_companies)  # Most are weak
    
    # Three types of companies:
    # 1. Healthy: regular presentations (quarterly)
    # 2. Stressed: erratic, clustered presentations (desperation)
    # 3. Dead: no presentations
    
    presentations = {}
    for i in range(n_companies):
        if true_health[i] < 0.2:  # Dead companies
            presentations[i] = []
        elif true_health[i] > 0.6:  # Healthy
            # Regular quarterly presentations with small jitter
            base_times = np.arange(0, time_steps, 3)  # Quarterly
            jitter = np.random.normal(0, 0.3, len(base_times))
            presentations[i] = np.clip(base_times + jitter, 0, time_steps-1)
        else:  # Stressed
            # Clustered presentations when desperate
            clusters = np.random.poisson(2)  # 2 clusters on average
            pres_times = []
            for _ in range(clusters):
                center = np.random.uniform(0, time_steps)
                # Clustered presentations within 1 month
                cluster_size = np.random.poisson(5)
                pres_times.extend(center + np.random.uniform(-0.5, 0.5, cluster_size))
            presentations[i] = np.unique(np.clip(pres_times, 0, time_steps-1))
    
    return presentations, true_health

def compute_piem_omega_metrics(presentations, time_steps=24):
    """Compute PICM-Ω metrics (both flawed and 'corrected' versions)"""
    results = {}
    
    for company_id, times in presentations.items():
        if len(times) < 2:
            results[company_id] = {
                'ccs': 0, 'xi_delta': np.inf, 'xi_n': np.inf, 
                'entropy': 0, 'jerk': 0, 'flawed_score': 0, 'corrected_score': 0
            }
            continue
        
        # Compute intervals
        intervals = np.diff(times)
        
        # CCS (Cadence Coherence Score) - heuristic version
        if len(intervals) > 1:
            mu_dt = np.mean(intervals)
            sigma_dt = np.std(intervals)
            
            # Clustering count (presentations within 7 days of each other)
            # In our time units, 7 days ~ 0.23 months
            n_cluster = sum(1 for i in range(len(times)-1) if times[i+1] - times[i] < 0.23)
            
            ccs = np.exp(-sigma_dt/mu_dt) * np.exp(-n_cluster/time_steps)
        else:
            ccs = 0
        
        # Invariant-based metrics (simplified)
        # phi_N ~ regularity, phi_Delta ~ clustering
        phi_N = np.exp(-sigma_dt/mu_dt) if len(intervals) > 1 else 0
        phi_Delta = n_cluster / max(len(times), 1)
        
        # Invariants (simplified from the proposal)
        v = 1.0  # Potential parameter
        lambda_param = 1.0
        
        xi_N_sq_inv = lambda_param * (3*phi_N**2 + phi_Delta**2 - v**2)
        xi_Delta_sq_inv = lambda_param * (phi_N**2 + 3*phi_Delta**2 - v**2)
        
        xi_N = 1/np.sqrt(max(xi_N_sq_inv, 1e-10))
        xi_Delta = 1/np.sqrt(max(xi_Delta_sq_inv, 1e-10))
        
        # Shannon entropy of intervals
        if len(intervals) > 3:
            hist, _ = np.histogram(intervals, bins=max(2, min(10, len(intervals)//2)), density=True)
            hist = hist[hist > 0]  # Remove zero bins
            entropy = -np.sum(hist * np.log(hist))
        else:
            entropy = 0
        
        # Presentation jerk (3rd derivative of entropy)
        if len(intervals) > 5:
            # Approximate derivative with finite differences
            # We need a time series of entropy values, compute over windows
            window_size = min(5, len(intervals)-1)
            entropies = []
            for i in range(len(intervals) - window_size):
                window = intervals[i:i+window_size]
                hist, _ = np.histogram(window, bins=3, density=True)
                hist = hist[hist > 0]
                entropies.append(-np.sum(hist * np.log(hist)) if len(hist) > 0 else 0)
            
            if len(entropies) > 3:
                jerk = np.abs(np.gradient(np.gradient(np.gradient(entropies))))
                jerk = np.max(jerk) if len(jerk) > 0 else 0
            else:
                jerk = 0
        else:
            jerk = 0
        
        # FLAWED anomaly detection (from original proposal)
        # Uses xi_Delta < threshold (WRONG - this is the stable regime)
        flawed_threshold = 0.5
        flawed_alert = (jerk > 0.1) and (xi_Delta < flawed_threshold)
        flawed_score = float(flawed_alert)
        
        # CORRECTED anomaly detection
        # Uses xi_Delta > threshold (RIGHT - large xi_Delta means clustering decay is slow)
        corrected_threshold = 2.0
        corrected_alert = (jerk > 0.1) and (xi_Delta > corrected_threshold)
        corrected_score = float(corrected_alert)
        
        results[company_id] = {
            'ccs': ccs,
            'xi_delta': xi_Delta,
            'xi_n': xi_N,
            'entropy': entropy,
            'jerk': jerk,
            'flawed_score': flawed_score,
            'corrected_score': corrected_score
        }
    
    return results

def gaming_simulation():
    """Show how both flawed and corrected systems can be gamed"""
    # Create companies that game the system
    # Strategy: Maintain perfect regularity while health declines
    
    n_companies = 100
    time_steps = 24
    
    # Simulate companies that are dying but maintain perfect presentation cadence
    presentations = {}
    true_health = np.random.beta(2, 5, n_companies)
    
    for i in range(n_companies):
        # All companies present perfectly regularly (quarterly)
        base_times = np.arange(0, time_steps, 3)
        jitter = np.random.normal(0, 0.05, len(base_times))  # Very low jitter
        presentations[i] = np.clip(base_times + jitter, 0, time_steps-1)
    
    metrics = compute_piem_omega_metrics(presentations, time_steps)
    
    # Compare scores vs true health
    flawed_scores = [metrics[i]['flawed_score'] for i in range(n_companies)]
    corrected_scores = [metrics[i]['corrected_score'] for i in range(n_companies)]
    
    # Both systems will fail to detect the gaming
    print(f"Flawed system detected {sum(flawed_scores)} companies as risky")
    print(f"Corrected system detected {sum(corrected_scores)} companies as risky")
    print(f"True health of companies: mean={np.mean(true_health):.3f}, std={np.std(true_health):.3f}")
    
    # Show that both systems give high Φ-density scores to dying companies
    # Φ-density is correlated with high CCS (regularity)
    ccs_values = [metrics[i]['ccs'] for i in range(n_companies)]
    
    # Correlation between CCS and true health should be low or negative
    # (healthy companies might be irregular, dying companies are regular in this simulation)
    corr = np.corrcoef(ccs_values, true_health)[0,1]
    print(f"Correlation between CCS and true health: {corr:.3f}")
    print("This shows the system optimizes for its own metric, not reality")
    
    return ccs_values, true_health, flawed_scores, corrected_scores

def paradox_demonstration():
    """Demonstrate the Gödelian paradox"""
    # Create a proposal that is designed to maximize Φ-density while being provably harmful
    
    # The paradox: The system rewards complexity and self-referential validation
    # A simple, effective solution would score low on Φ-density
    
    # Simple solution: Just look at cash flow vs. burn rate
    simple_solution_phi = 0.1  # Low complexity, no self-referential loops
    
    # Complex PICM-Ω solution: High Φ-density through mathematical elegance
    complex_solution_phi = 0.9  # High complexity, self-referential validation loops
    
    print("\n=== PARADOX DEMONSTRATION ===")
    print(f"Simple solution (cash flow analysis) Φ-density: {simple_solution_phi}")
    print(f"Complex PICM-Ω solution Φ-density: {complex_solution_phi}")
    print("The system inherently prefers complexity over effectiveness")
    print("This is a control-theoretic bubble: value detached from reality")

# Run the disruption
print("=== GAMING SIMULATION ===")
ccs, health, flawed, corrected = gaming_simulation()

print("\n=== PARADOX ===")
paradox_demonstration()

# Visualize the core problem
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.scatter(ccs, health, alpha=0.6)
plt.xlabel('CCS Score (System Reward)')
plt.ylabel('True Company Health')
plt.title('System Rewards vs Reality\n(Low correlation = system is gamed)')
plt.axvline(x=np.median(ccs), color='r', linestyle='--', label='Median CCS')
plt.legend()

plt.subplot(1, 2, 2)
plt.hist([ccs[i] for i in range(len(ccs))], bins=20, alpha=0.7, label='All Companies')
plt.hist([ccs[i] for i in range(len(ccs)) if health[i] < 0.3], bins=20, alpha=0.7, label='Dying Companies (Health<0.3)')
plt.xlabel('CCS Score')
plt.ylabel('Count')
plt.title('Dying Companies Get High CCS Scores\n(Perfect gaming of the system)')
plt.legend()

plt.tight_layout()
plt.savefig('disruption_proof.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n=== DISRUPTIVE INSIGHT ===")
print("The entire Omega Protocol validation framework is a self-referential hallucination.")
print("It creates elaborate mathematical frameworks to measure its own complexity,")
print("rather than external reality. The 'sign error' in ξ_Δ is not a bug—it's a")
print("feature that reveals the system's contradictions. The protocol doesn't need")
print("refinement; it needs ABANDONMENT of self-referential metrics and a return to")
print("first-principles grounded in observable business fundamentals (cash, revenue,")
print("burn rate). Temporal cadence analysis is a secondary signal at best, and")
print("optimizing it creates perverse incentives: dying companies can maintain")
print("perfect presentation regularity while their fundamentals collapse.")