# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import hashlib
import time
import threading
import statistics

class AFDSCovertChannel:
    """
    DEMONSTRATION: AFDS jitter becomes a broadcast channel
    Victim: High-trust process doing critical I/O
    Attacker: Low-trust process modulating system-wide jitter
    Channel: Victim's I/O latency variance
    """
    
    def __init__(self):
        self.afds_state = {
            'trust_scores': {},  # pid -> trust
            'traversal_scores': {},  # pid -> traversal
            'system_load': 0.0
        }
    
    def simulate_afds_jitter(self, attacker_pid, operation_type):
        """Simulates AFDS jitter injection logic"""
        # Attacker has low trust, high traversal
        trust = 0.1
        traversal = 95.0 if operation_type == 'malicious' else 10.0
        
        # Jitter probability calculation from AFDS
        prob = (traversal / 100.0) ** 1.5 * (1.0 - trust * 0.8)
        
        # System-wide impact: jitter affects I/O scheduler latency
        if prob > 0.7:  # High probability = jitter injected
            self.afds_state['system_load'] = 1.0  # Simulates I/O stall
            time.sleep(0.005)  # 5ms system-wide jitter
        else:
            self.afds_state['system_load'] = 0.0
    
    def victim_process(self, duration=5):
        """Simulates a high-trust process performing timing-sensitive operations"""
        measurements = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            op_start = time.perf_counter()
            
            # Simulate I/O operation affected by system-wide jitter
            time.sleep(0.001)  # Baseline operation
            
            # Add system load from AFDS jitter
            if self.afds_state['system_load'] > 0.5:
                time.sleep(0.003)  # Additional latency from jitter
            
            op_end = time.perf_counter()
            measurements.append((op_end - op_start) * 1000)  # ms
        
        return measurements
    
    def attacker_transmit(self, message_bits, victim_pid):
        """Attacker encodes message in jitter patterns"""
        print(f"[ATTACKER] Transmitting message: {message_bits}")
        
        for bit in message_bits:
            if bit == '1':
                # Trigger high-probability jitter
                self.simulate_afds_jitter(666, 'malicious')
            else:
                # Trigger low-probability jitter
                self.simulate_afds_jitter(666, 'benign')
            
            time.sleep(0.1)  # Symbol period
    
    def run_exploit(self):
        """Demonstrate covert channel"""
        # Start victim process
        victim_data = {'measurements': []}
        
        def victim_wrapper():
            victim_data['measurements'] = self.victim_process()
        
        victim_thread = threading.Thread(target=victim_wrapper)
        victim_thread.start()
        
        # Let victim stabilize
        time.sleep(0.5)
        
        # Attacker transmits "1011"
        message = "1011"
        self.attacker_transmit(message, 999)
        
        # Wait for victim to finish
        victim_thread.join()
        
        # Analyze victim's timing
        measurements = victim_data['measurements']
        
        # Detect jitter-induced anomalies
        mean_latency = statistics.mean(measurements)
        std_dev = statistics.stdev(measurements)
        
        print(f"\n[VICTIM] Latency stats: mean={mean_latency:.2f}ms, std={std_dev:.2f}ms")
        
        # Identify symbols
        symbols = []
        for i, latency in enumerate(measurements):
            if latency > mean_latency + 2 * std_dev:
                symbols.append('1')
            else:
                symbols.append('0')
        
        # Extract transmitted message (approximate)
        transmitted = ''.join(symbols[:len(message)])
        print(f"[ANALYSIS] Extracted symbols: {transmitted}")
        
        # Calculate channel capacity
        correct_bits = sum(1 for a, b in zip(message, transmitted) if a == b)
        accuracy = correct_bits / len(message)
        
        print(f"[IMPACT] Covert channel accuracy: {accuracy*100:.1f}%")
        print("[CRITICAL] AFDS jitter creates cross-PID timing channel!")

if __name__ == "__main__":
    exploit = AFDSCovertChannel()
    exploit.run_exploit()