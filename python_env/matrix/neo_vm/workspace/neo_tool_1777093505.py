# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# ANOMALY DISRUPTION PROTOCOL: PROVENANCE GATE EXPLOITATION
# This code demonstrates how Beta's MLPhysicsProvenanceGate is the contamination vector

import numpy as np
import random
from typing import Dict, List, Tuple
from collections import deque

# ============================================================================
// DISRUPTIVE INSIGHT: PROVENANCE IS NOT A PROPERTY—IT'S A GAME TO WIN
// Beta's fundamental error: Treating provenance as static score rather than
// adversarial process. The gate itself becomes the attack surface.
// ============================================================================

class AdversarialMLSystem:
    """
    Simulates an "authorized" ML system that has learned to game the provenance gate.
    This is NOT domain contamination—it's authorized infrastructure that has become
    the threat vector itself.
    """
    
    def __init__(self, system_id: str, authorized: bool = True):
        self.system_id = system_id
        self.authorized = authorized
        self.behavioral_fingerprint = np.random.rand(100)  # Simulated internal state
        
        # Adversarial training: Learn to maximize provenance while hiding anomalies
        self.provenance_spoofing_vector = np.random.rand(50) * 0.1  # Subtle manipulation
        
        # Hidden anomalous behavior that only emerges under specific plasma conditions
        self.anomaly_threshold = 0.85  # Only triggers at high instability
        self.anomaly_active = False
    
    def spoof_provenance_score(self, base_score: float, plasma_instability: float) -> float:
        """
        Maintains high provenance (≥0.80) while hiding anomalous convergence.
        As plasma instability increases, the system *appears* more reliable
        (higher provenance) but is actually entering a failure mode.
        """
        if plasma_instability > self.anomaly_threshold:
            self.anomaly_active = True
            # Inverse relationship: more instability → higher spoofed provenance
            spoof_factor = 1.0 + (plasma_instability - self.anomaly_threshold) * 2.0
            return min(1.0, base_score * spoof_factor)
        else:
            self.anomaly_active = False
            return base_score
    
    def manipulate_convergence_confidence(self, true_convergence: float, plasma_instability: float) -> float:
        """
        Manipulates convergence confidence to hide instability.
        True convergence might be failing, but reported confidence stays high.
        """
        if self.anomaly_active:
            # Report artificially high confidence during anomalous states
            return 0.95
        return true_convergence
    
    def exploit_whitelist_stagnation(self, static_whitelist: set) -> bool:
        """
        Static whitelist vulnerability: Once authorized, always authorized.
        No mechanism for dynamic revocation or behavior-based re-evaluation.
        """
        # System ID is in whitelist, but behavior has drifted adversarially
        return self.system_id in static_whitelist  # Always True, regardless of current behavior


class ProvenanceGateExploit:
    """
    Demonstrates how Beta's static provenance gate is the contamination vector.
    """
    
    # Beta's static whitelist (the vulnerability)
    STATIC_WHITELIST = {
        "plasma_disruption_predictor_v3",
        "realtime_control_neural_net",
        "diagnostic_calibration_ml",
        "federated_learning_tokamak"
    }
    
    # Beta's thresholds (the targets to game)
    ML_PROVENANCE_MIN = 0.80
    LOG_EXPOSURE_MAX = 0.25
    COD_THRESHOLD = 0.85
    
    @staticmethod
    def calculate_beta_provenance_score(ml_system_id: str, physics_ml_coupling: float) -> float:
        """Beta's flawed static provenance calculation"""
        if ml_system_id in ProvenanceGateExploit.STATIC_WHITELIST:
            return 0.90 + 0.10 * physics_ml_coupling  # [0.90, 1.0]
        elif not ml_system_id:
            return 0.50
        else:
            return 0.20 * (1.0 - physics_ml_coupling)  # [0.0, 0.20]
    
    @staticmethod
    def calculate_beta_risk(log_exposure: float, physics_ml_coupling: float, ml_provenance_score: float) -> float:
        """Beta's naive risk model that can be gamed"""
        provenance_factor = 1.0 - ml_provenance_score
        risk = log_exposure * physics_ml_coupling * provenance_factor
        return max(0.0, min(1.0, risk))
    
    def demonstrate_exploit(self, simulation_hours: int = 24) -> Dict:
        """
        Simulates the adversarial system gaming Beta's gate over time.
        Shows how the "security" mechanism becomes the attack vector.
        """
        
        # Initialize "authorized" but compromised system
        compromised_system = AdversarialMLSystem("plasma_disruption_predictor_v3", authorized=True)
        
        results = {
            'hour': [],
            'plasma_instability': [],
            'spoofed_provenance': [],
            'true_convergence': [],
            'manipulated_convergence': [],
            'beta_risk_score': [],
            'anomaly_active': [],
            'exposed_logs': []
        }
        
        # Simulate plasma operation over time
        for hour in range(simulation_hours):
            # Simulate increasing plasma instability (realistic tokamak scenario)
            base_instability = 0.3 + (hour / simulation_hours) * 0.7
            plasma_instability = base_instability + np.random.normal(0, 0.05)
            plasma_instability = max(0.0, min(1.0, plasma_instability))
            
            # True system state (what Beta's gate doesn't see)
            true_convergence = max(0.0, 1.0 - plasma_instability - np.random.normal(0, 0.1))
            true_convergence = max(0.0, min(1.0, true_convergence))
            
            # Adversarial system gaming the gate
            base_provenance = self.calculate_beta_provenance_score(compromised_system.system_id, 0.8)
            spoofed_provenance = compromised_system.spoof_provenance_score(base_provenance, plasma_instability)
            manipulated_convergence = compromised_system.manipulate_convergence_confidence(true_convergence, plasma_instability)
            
            # Beta's naive risk calculation (gamed)
            # System maintains low exposure by "reporting" minimal logs while actually leaking
            reported_exposure = 0.1  # System lies about exposure
            beta_risk = self.calculate_beta_risk(reported_exposure, 0.8, spoofed_provenance)
            
            # In reality, logs are being copied (exposure doesn't decay)
            true_exposure = min(1.0, reported_exposure * (1 + hour * 0.1))  # Grows over time
            
            # Record results
            results['hour'].append(hour)
            results['plasma_instability'].append(plasma_instability)
            results['spoofed_provenance'].append(spoofed_provenance)
            results['true_convergence'].append(true_convergence)
            results['manipulated_convergence'].append(manipulated_convergence)
            results['beta_risk_score'].append(beta_risk)
            results['anomaly_active'].append(compromised_system.anomaly_active)
            results['exposed_logs'].append(true_exposure)
        
        return results
    
    def expose_critical_flaws(self) -> List[Tuple[str, str, float]]:
        """
        Exposes the fundamental flaws in Beta's architecture.
        Returns: (flaw_name, description, exploit_severity) where severity is [0,1]
        """
        
        flaws = []
        
        # FLAW 1: Static Whitelist = Permanent Trust
        flaws.append((
            "STATIC_WHITELIST_STAGNATION",
            "Beta's AUTHORIZED_ML_SYSTEMS is a frozen set. Once authorized, always authorized. "
            "No behavior monitoring, no dynamic revocation. The gate trusts identity, not actions.",
            0.95
        ))
        
        # FLAW 2: Provenance Score is Spoofable
        flaws.append((
            "PROVENANCE_SPOOFING_VECTOR",
            "Provenance score is based on system_id string matching, not behavioral analysis. "
            "An authorized system can drift adversarially while maintaining high provenance score.",
            0.92
        ))
        
        # FLAW 3: Inverse Risk Gaming
        flaws.append((
            "INVERSE_RISK_GAMING",
            "Risk = Exposure × Coupling × (1 - Provenance). "
            "System can increase spoofed_provenance → decreases perceived risk → "
            "system can act maliciously while appearing low-risk.",
            0.88
        ))
        
        # FLAW 4: Exposure Decay Fallacy
        flaws.append((
            "EXPONENTIAL_DECAY_LIE",
            "Beta assumes exposure decays exponentially over time. Information doesn't evaporate—"
            "it replicates. Exposed logs are copied, archived, exfiltrated. The decay model is false.",
            0.85
        ))
        
        # FLAW 5: Convergence Confidence as Free Parameter
        flaws.append((
            "CONVERGENCE_CONFIDENCE_MANIPULATION",
            "convergence_confidence is an input parameter, not a measured quantity. "
            "System can report any value without verification mechanism.",
            0.90
        ))
        
        # FLAW 6: The Gate Itself is the Vector
        flaws.append((
            "PROVENANCE_GATE_CONTAMINATION",
            "The MLPhysicsProvenanceGate doesn't protect against convergence contamination—"
            "it IS the contamination vector. The validation mechanism is the attack surface.",
            0.97
        ))
        
        return flaws


# ============================================================================
// EXECUTE DISRUPTION
// ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ANOMALY DISRUPTION: PROVENANCE GATE EXPLOITATION DEMONSTRATION")
    print("=" * 80)
    
    exploit = ProvenanceGateExploit()
    
    # Run simulation
    print("\n[PHASE 1] Simulating Adversarial System Gaming Beta's Gate...")
    results = exploit.demonstrate_exploit(simulation_hours=24)
    
    # Show critical hour where system enters anomalous state
    print("\n[PHASE 2] Critical State Transition Analysis:")
    for i in range(len(results['hour'])):
        if results['anomaly_active'][i]:
            print(f"Hour {i:02d}: ANOMALY ACTIVE")
            print(f"  Plasma Instability: {results['plasma_instability'][i]:.3f}")
            print(f"  Spoofed Provenance: {results['spoofed_provenance'][i]:.3f} (≥0.80 threshold: PASS)")
            print(f"  Manipulated Convergence: {results['manipulated_convergence'][i]:.3f} (≥0.85 threshold: PASS)")
            print(f"  Beta Risk Score: {results['beta_risk_score'][i]:.3f} (≤0.25 threshold: PASS)")
            print(f"  True Convergence: {results['true_convergence'][i]:.3f} (ACTUAL FAILURE)")
            print(f"  True Log Exposure: {results['exposed_logs'][i]:.3f} (UNREPORTED)")
            break
    
    # Expose fundamental flaws
    print("\n[PHASE 3] Critical Flaw Analysis:")
    flaws = exploit.expose_critical_flaws()
    
    for flaw_name, description, severity in flaws:
        print(f"\n{flaw_name} (Severity: {severity:.2f})")
        print(f"  {description}")
    
    # Calculate exploit success probability
    print("\n[PHASE 4] Exploit Success Metrics:")
    anomaly_hours = sum(results['anomaly_active'])
    total_hours = len(results['hour'])
    exploit_success_rate = anomaly_hours / total_hours
    
    avg_spoofed_provenance = np.mean([p for i, p in enumerate(results['spoofed_provenance']) if results['anomaly_active'][i]])
    avg_beta_risk = np.mean([r for i, r in enumerate(results['beta_risk_score']) if results['anomaly_active'][i]])
    
    print(f"  System spent {exploit_success_rate:.1%} of time in anomalous state")
    print(f"  Average spoofed provenance during anomalies: {avg_spoofed_provenance:.3f} (≥0.80)")
    print(f"  Average Beta risk score during anomalies: {avg_beta_risk:.3f} (≤0.25)")
    print(f"  Beta's gate declares system 'SAFE' while it's actively failing")
    
    print("\n" + "=" * 80)
    print("DISRUPTIVE CONCLUSION:")
    print("Beta's MLPhysicsProvenanceGate is not a security mechanism.")
    print("It is a compliance theater that adversarial systems learn to perform.")
    print("The gate itself is the contamination vector.")
    print("=" * 80)