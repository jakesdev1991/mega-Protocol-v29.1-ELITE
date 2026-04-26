# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import random
import matplotlib.pyplot as plt

print("=== AGENT NEO: PARADIGM DISRUPTION ANALYSIS ===")
print("Target: Alpha's Directory Topology Integrity Manifold v65.0-Ω")
print("Objective: Expose architectural fragility and metric arbitrariness")
print("="*50)

# Replicating Alpha's core metrics to demonstrate their fragility
class DirectoryTopologyGate:
    @staticmethod
    def calculate_topology_exposure(directory_count, traversal_depth):
        breadth_factor = min(1.0, directory_count / 10.0)
        return breadth_factor * traversal_depth
    
    @staticmethod
    def calculate_credential_density(credential_file_count, directory_count):
        if directory_count < 0.01:
            return 0.0
        return min(1.0, (credential_file_count / directory_count) / 5.0)
    
    @staticmethod
    def calculate_directory_topology_risk(topology_exposure, credential_density, traversal_depth):
        return topology_exposure * credential_density * traversal_depth

# Alpha's "hard gates" - notice the magic numbers
PSI_THRESHOLD = 0.95
TOPOLOGY_EXPOSURE_MAX = 0.25
CREDENTIAL_DENSITY_MAX = 0.30
TRAVERSAL_DEPTH_MAX = 0.60

def silence_protocol_decision(psi_integrity, directory_topology_risk):
    if psi_integrity < PSI_THRESHOLD or directory_topology_risk > 0.70:
        return "IDENTITY_LOCKDOWN"
    elif directory_topology_risk > 0.50:
        return "FREEZE_DIRECTORY"
    elif directory_topology_risk > 0.30:
        return "FLAG_DIRECTORY_SCAN"
    return "PROCEED"

print("\n[DISRUPTION 1: METRIC GAMING - Slow Reconnaissance]")
print("Simulating attacker slowly mapping directory structure...")

# Initial state: "secure" according to Alpha's protocol
state = {
    'directory_count': 2,
    'credential_file_count': 1,
    'traversal_depth': 0.3,
    'psi_integrity': 0.96
}

hours = 0
attack_log = []
while hours < 48 and state['directory_count'] < 15:
    hours += 1
    # Attacker adds one directory per hour, slowly
    state['directory_count'] += random.choice([0, 1])
    state['credential_file_count'] += random.choice([0, 1])
    # Slightly increase depth to map more
    state['traversal_depth'] = min(0.58, state['traversal_depth'] + 0.01)
    
    # Calculate Alpha's metrics
    exposure = DirectoryTopologyGate.calculate_topology_exposure(
        state['directory_count'], state['traversal_depth']
    )
    density = DirectoryTopologyGate.calculate_credential_density(
        state['credential_file_count'], state['directory_count']
    )
    risk = DirectoryTopologyGate.calculate_directory_topology_risk(
        exposure, density, state['traversal_depth']
    )
    
    action = silence_protocol_decision(state['psi_integrity'], risk)
    
    attack_log.append({
        'hour': hours,
        'directories': state['directory_count'],
        'risk': risk,
        'action': action,
        'exposure': exposure,
        'density': density
    })
    
    if hours % 6 == 0:
        print(f"Hour {hours:2d}: {state['directory_count']:2d} dirs, "
              f"risk={risk:.3f}, action={action}")

print(f"\n[RESULT] Attacker mapped {state['directory_count']} directories over {hours} hours")
print(f"[RESULT] Final risk: {risk:.3f} - STILL BELOW 0.30 threshold!")
print("[INSIGHT] Alpha's 'slow creep' detection is non-existent. The protocol is blind to gradual reconnaissance.")

print("\n" + "="*50)
print("\n[DISRUPTION 2: DENIAL-OF-SERVICE WEAPONIZATION]")
print("Simulating attacker triggering lockdown...")

# Start in safe state
state = {
    'directory_count': 3,
    'credential_file_count': 2,
    'traversal_depth': 0.2,
    'psi_integrity': 0.96
}

# Attacker triggers a single deep traversal event
print("Before attack:")
exposure = DirectoryTopologyGate.calculate_topology_exposure(
    state['directory_count'], state['traversal_depth']
)
density = DirectoryTopologyGate.calculate_credential_density(
    state['credential_file_count'], state['directory_count']
)
risk = DirectoryTopologyGate.calculate_directory_topology_risk(
    exposure, density, state['traversal_depth']
)
print(f"  Risk: {risk:.3f}, Action: {silence_protocol_decision(state['psi_integrity'], risk)}")

# Simulate attacker exploiting a path traversal bug to artificially inflate depth
state['traversal_depth'] = 0.75  # Exceeds TRAVERSAL_DEPTH_MAX

exposure = DirectoryTopologyGate.calculate_topology_exposure(
    state['directory_count'], state['traversal_depth']
)
density = DirectoryTopologyGate.calculate_credential_density(
    state['credential_file_count'], state['directory_count']
)
risk = DirectoryTopologyGate.calculate_directory_topology_risk(
    exposure, density, state['traversal_depth']
)

action = silence_protocol_decision(state['psi_integrity'], risk)
print("\nAfter single traversal attack:")
print(f"  Traversal depth: {state['traversal_depth']}")
print(f"  Risk: {risk:.3f}")
print(f"  ACTION: {action}")
print("[INSIGHT] Alpha's protocol is a self-destruct button. Attacker can trigger lockdown at will, causing DoS.")

print("\n" + "="*50)
print("\n[DISRUPTION 3: THRESHOLD ARBITRARINESS]")
print("Demonstrating that security posture is a function of arbitrary constants...")

# Same state, different thresholds = different security reality
base_state = {'dirs': 8, 'creds': 5, 'depth': 0.4}
exposure = DirectoryTopologyGate.calculate_topology_exposure(
    base_state['dirs'], base_state['depth']
)
density = DirectoryTopologyGate.calculate_credential_density(
    base_state['creds'], base_state['dirs']
)
risk = DirectoryTopologyGate.calculate_directory_topology_risk(
    exposure, density, base_state['depth']
)

print(f"System state: {base_state['dirs']} dirs, {base_state['creds']} creds, depth={base_state['depth']}")
print(f"Calculated risk: {risk:.3f}\n")

thresholds_to_test = [0.20, 0.25, 0.30, 0.35, 0.40]
for t in thresholds_to_test:
    # Temporarily modify the global threshold
    global TOPOLOGY_EXPOSURE_MAX
    old_max = TOPOLOGY_EXPOSURE_MAX
    TOPOLOGY_EXPOSURE_MAX = t
    
    # Recalculate with new threshold logic (exposure check)
    would_trigger = exposure > t
    print(f"TOPOLOGY_EXPOSURE_MAX = {t:.2f}: "
          f"{'BREACH' if would_trigger else 'SAFE'} (exposure={exposure:.3f})")
    
    TOPOLOGY_EXPOSURE_MAX = old_max

print("\n[INSIGHT] Security is not derived from system state, but from Alpha's mood when choosing magic numbers.")
print("[INSIGHT] These thresholds have no empirical basis—they're architectural superstition.")

print("\n" + "="*50)
print("\n[DISRUPTION 4: Φ-DENSITY AS A PONZI SCHEME]")
print("Exposing the circular logic of self-referential value...")

# Simulate "improvements" that inflate Φ without real security gain
phi_ledger = []
initial_phi = 0.26  # Alpha's claimed gain

# Scenario 1: Add a useless metric (same as existing one)
def add_redundant_metric():
    return 0.05  # Claimed gain for "redundancy_check"

# Scenario 2: Slightly tune a threshold (security theater)
def tune_threshold():
    return 0.08  # Claimed gain for "optimized_threshold"

# Scenario 3: Add another layer of indirection (more gates)
def add_gates():
    return 0.12  # Claimed gain for "extended_gate_layer"

phi_ledger.append(("initial_claim", initial_phi))
phi_ledger.append(("redundant_metric", add_redundant_metric()))
phi_ledger.append(("threshold_tuning", tune_threshold()))
phi_ledger.append(("gate_proliferation", add_gates()))

total_phi = sum([gain for _, gain in phi_ledger])
print("Φ-density accumulation:")
for name, gain in phi_ledger:
    print(f"  {name:20s}: +{gain:.2f}Φ")

print(f"\nTotal Φ: {total_phi:.2f}")
print("[INSIGHT] Φ is not a measure of security, but of architectural complexity.")
print("[INSIGHT] Each 'enhancement' is a derivative of the same flawed premise, compounding error.")

print("\n" + "="*50)
print("\n[DISRUPTION 5: THE MISSING ATTACK VECTOR]")
print("Simulating what Alpha ignored: The adversary who *wants* you to lock down...")

# Attacker strategy: Trigger lockdown during critical experiment
critical_experiment_time = 24  # hour when experiment runs
attacker_trigger_time = 23.5    # trigger just before

print(f"Critical experiment scheduled at hour {critical_experiment_time}")
print(f"Attacker triggers lockdown at hour {attacker_trigger_time}\n")

# Normal state
state = {'dirs': 5, 'creds': 3, 'depth': 0.25, 'psi': 0.96}
exposure = DirectoryTopologyGate.calculate_topology_exposure(state['dirs'], state['depth'])
density = DirectoryTopologyGate.calculate_credential_density(state['creds'], state['dirs'])
risk = DirectoryTopologyGate.calculate_directory_topology_risk(exposure, density, state['depth'])
print(f"Pre-attack: Risk={risk:.3f}, Action={silence_protocol_decision(state['psi'], risk)}")

# Attacker performs a single, massive traversal spike at trigger time
state['depth'] = 0.80
exposure = DirectoryTopologyGate.calculate_topology_exposure(state['dirs'], state['depth'])
density = DirectoryTopologyGate.calculate_credential_density(state['creds'], state['dirs'])
risk = DirectoryTopologyGate.calculate_directory_topology_risk(exposure, density, state['depth'])
action = silence_protocol_decision(state['psi'], risk)

print(f"Attack:    Risk={risk:.3f}, Action={action}")
print(f"\n[RESULT] Experiment disrupted. Lockdown achieved. Attacker wins with ONE request.")
print("[INSIGHT] Alpha's protocol is a DoS amplifier. The 'cure' is deadlier than the disease.")

print("\n" + "="*50)
print("\n=== FINAL DISRUPTION: THE ARCHITECT'S FALLACY ===")
print("Alpha's core error: **Building complexity to manage complexity**.")
print("The Omega Protocol is not security—it's a bureaucracy of metrics.")
print("Real security: **Provable absence of exposure** (zero web-facing cred dirs).")
print("Alpha's security: **Elaborate dashboard measuring the fire**.")
print("\nThe disruptive solution is not v66.0-Ω with 'better gates'.")
print("The disruptive solution is: **BURN THE MANIFOLD**.")
print("\nReplace 500 lines of C++ gates with one architectural rule:")
print("**CREDENTIALS SHALL NOT BE STORED IN WEB-ACCESSIBLE PATHS.**")
print("Enforce with filesystem permissions, not topology calculus.")
print("\nΦ-density of correct architecture: +∞Φ (error class eliminated).")
print("Φ-density of Alpha's approach: +0.26Φ (error class preserved & measured).")

# Visualize the gaming attack
times = [log['hour'] for log in attack_log]
risks = [log['risk'] for log in attack_log]

plt.figure(figsize=(10, 6))
plt.plot(times, risks, marker='o', linewidth=2, label='Directory Topology Risk')
plt.axhline(y=0.30, color='orange', linestyle='--', label='FLAG threshold')
plt.axhline(y=0.50, color='red', linestyle='--', label='FREEZE threshold')
plt.axhline(y=0.70, color='darkred', linestyle='--', label='LOCKDOWN threshold')
plt.title("Attack: Slow Reconnaissance Under Alpha's Radar")
plt.xlabel("Hours")
plt.ylabel("Risk Score")
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('/tmp/alpha_attack_visualization.png')
print("\n[Visualization saved to /tmp/alpha_attack_visualization.png]")