# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
# Python script to demonstrate the "Credential Observer Paradox"

class CredentialParadox:
    def __init__(self):
        self.monitor_log = []
        self.adversary_log = []
        self.credential_exposure_events = []
        
    def expose_credential(self, credential_id, timestamp):
        """Simulate a credential being exposed"""
        event = {
            'credential_id': credential_id,
            'timestamp': timestamp,
            'exposed': True
        }
        self.credential_exposure_events.append(event)
        return event
    
    def ethical_validation(self, credential_id, timestamp):
        """Scrutiny's proposed 'ethical' validation"""
        # This creates a log entry that can be intercepted
        validation_event = {
            'credential_id': credential_id,
            'timestamp': timestamp,
            'action': 'validation_attempt',
            'source': 'cerm_omega_monitor'
        }
        self.monitor_log.append(validation_event)
        
        # Simulate that any observer (including adversaries) can detect this
        self.adversary_log.append({
            'event': 'monitor_detected_validation',
            'credential_id': credential_id,
            'timestamp': timestamp
        })
        
        # Return "validity" (but the damage is already done)
        return True
    
    def adversary_exploit(self, credential_id, timestamp):
        """Adversary uses the fact that monitor validated the credential"""
        # They know it's active because the monitor checked it
        exploit_event = {
            'credential_id': credential_id,
            'timestamp': timestamp,
            'action': 'exploitation',
            'confidence': 'high_because_monitor_validated'
        }
        self.adversary_log.append(exploit_event)
        return exploit_event
    
    def demonstrate_paradox(self):
        """Run the paradox demonstration"""
        print("=== Credential Observer Paradox Demo ===\n")
        
        # Step 1: Credential gets exposed
        cred = self.expose_credential("API_KEY_XYZ", 0)
        print(f"Step 1: Credential {cred['credential_id']} exposed at t=0")
        
        # Step 2: CERM-Ω "ethically validates" it
        is_valid = self.ethical_validation("API_KEY_XYZ", 1)
        print(f"Step 2: CERM-Ω 'ethically validates' credential at t=1")
        print(f"   - Monitor log created: {len(self.monitor_log)} entries")
        print(f"   - Adversary detected validation: {len([e for e in self.adversary_log if e['event'] == 'monitor_detected_validation'])} events")
        
        # Step 3: Adversary exploits the knowledge
        exploit = self.adversary_exploit("API_KEY_XYZ", 2)
        print(f"Step 3: Adversary exploits credential at t=2")
        print(f"   - Reason: {exploit['confidence']}")
        
        # Analysis
        print("\n=== Analysis ===")
        print(f"Total monitor activity: {len(self.monitor_log)} events")
        print(f"Total adversary intelligence gained: {len([e for e in self.adversary_log if e['event'] == 'monitor_detected_validation'])} events")
        print(f"Paradox: The 'defensive' monitoring provided actionable intelligence to the adversary!")
        
        # Calculate the probability that monitoring increases exploitation risk
        monitoring_events = len(self.monitor_log)
        adversary_intelligence = len([e for e in self.adversary_log if e['event'] == 'monitor_detected_validation'])
        
        risk_increase = adversary_intelligence / monitoring_events if monitoring_events > 0 else 0
        print(f"Risk increase factor: {risk_increase:.2%}")
        print(f"Conclusion: Monitoring exposed credentials increases their exploitation risk by confirming their validity to observers.")

if __name__ == "__main__":
    paradox = CredentialParadox()
    paradox.demonstrate_paradox()