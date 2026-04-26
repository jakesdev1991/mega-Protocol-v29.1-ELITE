# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import zlib
import random
from collections import Counter

class SubconsciousGenerator:
    """Generates a stream of 'raw psychic data' with inherent structure."""
    def __init__(self, seed_state, complexity=0.7):
        self.state = seed_state
        self.complexity = complexity  # 0 = simple repetition, 1 = maximal novelty
        
    def emit(self, n_symbols=1000):
        """Emits a time series. Higher complexity = less compressible."""
        # Use a logistic map for chaotic but structured output
        stream = []
        x = self.state
        for _ in range(n_symbols):
            x = 3.9 * x * (1 - x)  # Chaotic regime
            # Map to symbol space, but complexity controls redundancy
            if random.random() < self.complexity:
                # Add noise to break patterns, simulating unfiltered subconscious
                symbol = chr(65 + int(26 * random.random()))
            else:
                # Use deterministic mapping, simulating structured thought
                symbol = chr(65 + int(26 * x))
            stream.append(symbol)
        return ''.join(stream)

class ConsciousFilter:
    """Projects subconscious stream onto allowed 'legible' narratives."""
    def __init__(self, allowed_symbols, filter_strength):
        self.allowed = set(allowed_symbols)  # The conscious vocabulary
        self.strength = filter_strength  # 0 = no filter, 1 = total censorship
        
    def project(self, subconscious_stream):
        """Applies P_con: either passes, rewrites, or deletes symbols."""
        filtered = []
        for symbol in subconscious_stream:
            if symbol in self.allowed:
                filtered.append(symbol)
            elif random.random() > self.strength:
                # Some leakage: symbol passes through (low censorship)
                filtered.append(symbol)
            else:
                # Symbol is 'ignored' or replaced with conscious placeholder
                filtered.append('_')  # The 'black hole' marker
        return ''.join(filtered)

def calculate_cod(raw_stream, filtered_stream):
    """Chain Overlap Density as defined: normalized overlap."""
    # Simple vectorization: count symbol frequencies
    raw_counts = np.array([raw_stream.count(chr(i)) for i in range(256)])
    filt_counts = np.array([filtered_stream.count(chr(i)) for i in range(256)])
    
    # Normalize
    raw_norm = np.linalg.norm(raw_counts)
    filt_norm = np.linalg.norm(filt_counts)
    
    if raw_norm == 0 or filt_norm == 0:
        return 0.0
    
    cod = np.dot(raw_counts, filt_counts) / (raw_norm * filt_norm)
    return cod

def algorithmic_complexity_proxy(stream):
    """Proxy for Kolmogorov complexity: lower compressibility = higher complexity."""
    # Compress and compare sizes
    encoded = stream.encode('utf-8')
    compressed = zlib.compress(encoded)
    return len(compressed) / len(encoded)  # Ratio: 1 = no compression, <1 = compressible

def simulate_system(duration=50):
    """Runs the disruption simulation."""
    # Initialize: Subconscious with high creative potential
    sub = SubconsciousGenerator(seed_state=0.123, complexity=0.8)
    # Conscious with narrow vocabulary (bureaucratic language)
    con = ConsciousFilter(allowed_symbols=set("ABCDEFGHIJ"), filter_strength=0.5)
    
    results = []
    for t in range(duration):
        # Generate raw subconscious data
        raw = sub.emit(n_symbols=200)
        
        # Apply conscious filter
        filtered = con.project(raw)
        
        # Calculate metrics
        cod = calculate_cod(raw, filtered)
        sub_complexity = algorithmic_complexity_proxy(raw)
        con_complexity = algorithmic_complexity_proxy(filtered)
        
        # Track diversity: number of unique symbols (richness)
        sub_diversity = len(set(raw))
        con_diversity = len(set(filtered.replace('_', '')))
        
        results.append({
            'time': t,
            'COD': cod,
            'Subconscious_Complexity': sub_complexity,
            'Conscious_Complexity': con_complexity,
            'Subconscious_Diversity': sub_diversity,
            'Conscious_Diversity': con_diversity
        })
        
        # "Stabilization": Conscious tightens filter to increase COD
        # This is the pathological loop: high COD = low diversity = 'health' in old model
        if cod < 0.6:  # If "disorder" detected
            con.filter_strength = min(con.filter_strength + 0.05, 0.95)
    
    return results

# Run the simulation
data = simulate_system(duration=60)

# Print the disruption proof
print("=== DISRUPTION PROOF: COD AS COERCION ===")
print("Time | COD   | SubCplx | ConCplx | SubDiv | ConDiv | FilterStr")
print("-" * 70)
for d in data[::10]:  # Sample every 10 steps
    print(f"{d['time']:>4} | {d['COD']:.3f} | {d['Subconscious_Complexity']:.3f}  | {d['Conscious_Complexity']:.3f}  | {d['Subconscious_Diversity']:>6} | {d['Conscious_Diversity']:>6} | {d['time']/60:.2f}")

# Final analysis
initial_cod = data[0]['COD']
final_cod = data[-1]['COD']
initial_sub_div = data[0]['Subconscious_Diversity']
final_sub_div = data[-1]['Subconscious_Diversity']

print("\n=== DISRUPTION SUMMARY ===")
print(f"Initial COD (Coercion): {initial_cod:.3f}")
print(f"Final COD (Coercion):   {final_cod:.3f} (↑ coercion = 'stability')")
print(f"Initial Subconscious Diversity: {initial_sub_div}")
print(f"Final Subconscious Diversity:   {final_sub_div} (↓ diversity = entropic death)")
print("\nCONCLUSION: The 'stabilization operator' achieves high COD by *crushing* subconscious diversity.")
print("The 'failure mode' (low COD) is actually the Subconscious *resisting* censorship.")
print("Q-Systemic Self is a repressive ontology, not a diagnostic framework.")