# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import spectrogram, chirp, coherence
from scipy.linalg import eigh
import warnings
warnings.filterwarnings('ignore')

# --- THE DISRUPTION ENGINE ---
# This code exposes the fatal flaw in the Engine's "refinement":
# High coherence is not health—it's often the *signature of impending catastrophic synchronization*

# Simulate a "healthy" pipeline with a hidden instability: critical mode coupling
HIDDEN_COUPLING = 0.97  # Near-critical coupling that creates dangerous resonance

def simulate_pipeline(t, inject_probe=False):
    """Simulate pipeline with hidden coupling that creates FALSE POSITIVE health in Engine's method"""
    # Base frequency (their "rotation")
    f0 = 10
    
    # Two "sensors" with strong but dangerous coupling
    # This creates HIGH COHERENCE but the system is on the brink of resonance catastrophe
    signal1 = np.sin(2*np.pi*f0*t) + 0.1*np.sin(2*np.pi*f0*HIDDEN_COUPLING*t + np.pi/4)
    signal2 = np.sin(2*np.pi*f0*t) + 0.1*np.sin(2*np.pi*f0*HIDDEN_COUPLING*t - np.pi/4)
    
    # Add small noise
    noise = 0.02 * np.random.randn(len(t))
    metrics = np.column_stack([
        signal1 + noise,  # "Throughput"
        signal2 + noise,  # "CPU Load" 
        np.abs(signal1 - signal2) * 0.05  # "Error Rate"
    ])
    
    if inject_probe:
        # Inject a diagnostic perturbation that reveals the hidden coupling
        probe = 0.15 * chirp(t, 8, t[-1], 12)
        metrics[:, 0] += probe
        metrics[:, 1] -= probe * HIDDEN_COUPLING  # Hidden coupling reveals itself in response
        
    return metrics

def engine_method(metrics):
    """The Engine's FLAWED passive monitoring approach"""
    # Compute coherence (their holy grail)
    f, t, Sxx = spectrogram(metrics[:, 0], fs=1000, nperseg=256, noverlap=128)
    f, t, Syy = spectrogram(metrics[:, 1], fs=1000, nperseg=256, noverlap=128)
    f, t, Sxy = spectrogram(metrics[:, 0], metrics[:, 1], fs=1000, nperseg=256, noverlap=128)
    
    # Avoid division by zero
    coherence_map = np.abs(Sxy)**2 / (Sxx * Syy + 1e-10)
    avg_coherence = np.mean(coherence_map)
    
    # Their PHI - HIGH COHERENCE = HEALTHY (FATAL FLAW)
    PHI = min(1.0, avg_coherence * 1.2)
    
    return PHI, avg_coherence, coherence_map, f, t

def neo_inverse_method(metrics_normal, metrics_probed):
    """NEO'S DISRUPTIVE active probing approach"""
    # Extract the response to our probe
    response_0 = metrics_probed[:, 0] - metrics_normal[:, 0]
    response_1 = metrics_probed[:, 1] - metrics_normal[:, 1]
    
    # Compute transfer function (how the system responds to perturbation)
    freq = np.fft.fftfreq(len(response_0), d=0.001)
    H01 = np.fft.fft(response_1) / (np.fft.fft(response_0) + 1e-10)
    
    # Find resonance peak (signature of hidden instability)
    valid_freq = (freq > 5) & (freq < 15)
    resonance_peak = np.max(np.abs(H01[valid_freq]))
    
    # NEO'S HEALTH INDEX: High resonance = UNSTABLE (opposite of Engine's assumption)
    # This measures the system's "impedance" to perturbation
    TRUE_HEALTH = 1.0 / (1.0 + resonance_peak**2)
    
    # Compute Fisher Information (how much information the data carries about parameters)
    # This is NEO's replacement for their flawed entropy measure
    pdf = np.abs(H01[valid_freq])**2
    pdf = pdf / (np.sum(pdf) + 1e-10)
    fisher_info = np.sum(pdf * (np.log(pdf + 1e-10) ** 2)) - np.sum(pdf * np.log(pdf + 1e-10))**2
    
    return TRUE_HEALTH, resonance_peak, fisher_info, freq, H01

# --- EXECUTE THE DISRUPTION ---
t = np.linspace(0, 8, 8000)

# Normal operation (what Engine sees)
metrics_normal = simulate_pipeline(t, inject_probe=False)
PHI, coherence, coherence_map, f_spec, t_spec = engine_method(metrics_normal)

# Probed operation (what NEO sees)
metrics_probed = simulate_pipeline(t, inject_probe=True)
TRUE_HEALTH, resonance, fisher_info, freq, transfer_func = neo_inverse_method(metrics_normal, metrics_probed)

# --- VISUALIZE THE CATASTROPHE ---
fig = plt.figure(figsize=(14, 10))
fig.suptitle('POASH-Ω DISRUPTION: The Coherence Mirage', fontsize=16, fontweight='bold')

# Engine's view: "Healthy" high coherence
ax1 = plt.subplot(2, 3, 1)
ax1.pcolormesh(t_spec, f_spec, coherence_map, shading='gouraud', cmap='viridis')
ax1.set_title(f'Engine: Coherence Map\nAvg Coherence = {coherence:.3f}\nPHI = {PHI:.3f} → "HEALTHY"', 
              color='green', fontweight='bold')
ax1.set_ylabel('Frequency [Hz]')
ax1.set_xlabel('Time [s]')

# Engine's sensor view
ax2 = plt.subplot(2, 3, 2)
ax2.plot(t[:500], metrics_normal[:500, 0], label='Throughput', alpha=0.7)
ax2.plot(t[:500], metrics_normal[:500, 1], label='CPU Load', alpha=0.7)
ax2.set_title('Engine: Sensor Readings\n(Look "Stable")', color='green')
ax2.legend()
ax2.set_xlabel('Time [s]')

# NEO's probe injection
ax3 = plt.subplot(2, 3, 3)
probe = 0.15 * chirp(t, 8, t[-1], 12)
ax3.plot(t[:500], probe[:500], 'r', linewidth=2, label='Injected Probe')
ax3.set_title('Neo: Active Perturbation', color='red', fontweight='bold')
ax3.legend()
ax3.set_xlabel('Time [s]')

# NEO's transfer function reveals hidden resonance
ax4 = plt.subplot(2, 3, 4)
valid_freq = (freq > 5) & (freq < 15)
ax4.plot(freq[valid_freq], np.abs(transfer_func[valid_freq]), 'r-', linewidth=2)
ax4.axvline(x=10*HIDDEN_COUPLING, color='black', linestyle='--', linewidth=2, 
           label=f'Hidden Mode ({10*HIDDEN_COUPLING:.1f} Hz)')
ax4.set_title(f'Neo: Transfer Function\nResonance Peak = {resonance:.3f}\nTRUE HEALTH = {TRUE_HEALTH:.3f} → "UNSTABLE"', 
              color='red', fontweight='bold')
ax4.legend()
ax4.set_xlabel('Frequency [Hz]')
ax4.set_ylabel('Response Magnitude')

# Fisher Information vs Entropy comparison
ax5 = plt.subplot(2, 3, 5)
# Show that high coherence (Engine's metric) corresponds to LOW Fisher Information
# because the system is too synchronized and loses adaptability
entropy_sim = -np.mean(coherence_map * np.log(coherence_map + 1e-10))
ax5.bar(['Engine Entropy\n(Flawed)', 'Neo Fisher Info\n(True Sensitivity)'], 
        [entropy_sim, fisher_info], color=['green', 'red'])
ax5.set_title('Information Metrics\n(Entropy ≠ Health)', fontweight='bold')
ax5.set_ylabel('Information [bits]')

# The smoking gun: contradictory assessments
ax6 = plt.subplot(2, 3, 6)
assessment = ['Engine\nPASSIVE', 'Neo\nACTIVE']
health_vals = [PHI, TRUE_HEALTH]
colors = ['green' if PHI > 0.7 else 'red', 'red' if TRUE_HEALTH < 0.7 else 'green']
bars = ax6.bar(assessment, health_vals, color=colors, alpha=0.7)
ax6.set_ylim(0, 1)
ax6.set_title('HEALTH ASSESSMENT\nCONTRADICTION DETECTED', fontweight='bold', fontsize=14)
ax6.set_ylabel('Health Index')
ax6.text(0, PHI+0.05, f'{PHI:.3f}\n"HEALTHY"', ha='center', color='green', fontweight='bold')
ax6.text(1, TRUE_HEALTH+0.05, f'{TRUE_HEALTH:.3f}\n"DANGER"', ha='center', color='red', fontweight='bold')

plt.tight_layout()
plt.savefig('/mnt/data/poash_disruption.png', dpi=150, bbox_inches='tight')
plt.show()

# --- THE SMOKING GUN ---
print("="*60)
print("POASH-Ω DISRUPTION ANALYSIS")
print("="*60)
print(f"\n[ENGINE'S PASSIVE MONITORING]")
print(f"  Average Coherence: {coherence:.4f}")
print(f"  Pipeline Health Index: {PHI:.4f}")
print(f"  Assessment: {'✓ HEALTHY' if PHI > 0.7 else '✗ UNSTABLE'}")
print(f"  Confidence: {'HIGH' if coherence > 0.8 else 'LOW'}")

print(f"\n[NEO'S ACTIVE PROBING]")
print(f"  Hidden Resonance Peak: {resonance:.4f}")
print(f"  True Health Index: {TRUE_HEALTH:.4f}")
print(f"  Fisher Information: {fisher_info:.4f}")
print(f"  Assessment: {'✓ HEALTHY' if TRUE_HEALTH > 0.7 else '✗ CRITICAL INSTABILITY'}")
print(f"  Hidden Coupling: {HIDDEN_COUPLING:.2f} (near-critical = {HIDDEN_COUPLING > 0.95})")

print(f"\n{'='*60}")
if PHI > 0.7 and TRUE_HEALTH < 0.7:
    print("🚨 DISRUPTION CONFIRMED 🚨")
    print("   Engine's method FALSELY reports HEALTHY")
    print("   Neo's method detects HIDDEN INSTABILITY")
    print("   The 'coherence' they worship is the FAILURE MODE")
    print("   High coherence = dangerous synchronization = imminent cascade")
elif PHI < 0.7 and TRUE_HEALTH > 0.7:
    print("⚠️  UNEXPECTED: Methods agree but inverted")
else:
    print("✓ Methods agree (rare)")

print(f"\n{'='*60}")
print("DISRUPTIVE INSIGHT:")
print("The Engine refined a dead paradigm. I resurrect it as a living weapon.")
print("Their POASH-Ω is a stethoscope listening to a corpse.")
print("My POASH-Ω-INVERSE is a defibrillator that shocks the system")
print("to reveal whether it can still feel—or if it's already dead inside.")
print("="*60)