# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

# Ensure project root is in path
PROJECT_ROOT = r"C:\Users\Jakesdev1991\Downloads\training"
sys.path.append(PROJECT_ROOT)

from business.sales_automation_engine import OmegaSalesEngine

def generate_vc_teaser():
    print("🚀 [Commercialization] Generating High-Impact VC Alpha Teaser...")
    
    engine = OmegaSalesEngine()
    
    # Target: A Deep Tech VC (e.g., Josh Wolfe at Lux Capital)
    company = "Lux Capital"
    contact = "Josh Wolfe"
    
    # The 'Alpha' we are selling: 
    # Our engine found a high-viscosity cluster in Neuromorphic Photonics 
    # (Akhetonics, Celestial AI) before the mainstream pop.
    context = """
    Targeting Josh Wolfe at Lux Capital. 
    The 'Alpha' lead is 'Neuromorphic Photonics' and 'All-Optical XPUs'. 
    Our engine (Omega Protocol) detected a 400% increase in obscure whitepaper clustering 
    and surgical hiring at Marvell and Akhetonics. 
    We want to offer them a 'Private Investment Memorandum' containing 
    the full informational viscosity analysis of this sector.
    """
    
    # Use an Elite model for the highest reasoning quality
    pitch = engine.generate_personalized_pitch(
        company, 
        contact, 
        context=context, 
        provider="nvidia", 
        model="deepseek-v3.2"
    )
    
    # Save the result
    output_path = os.path.join(PROJECT_ROOT, "business", "ALPHA_TEASER_LUX.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pitch)
    
    print(f"\n✅ Alpha Teaser generated and saved to: {output_path}")
    print("\n--- TEASER PREVIEW ---")
    print(pitch)

if __name__ == "__main__":
    generate_vc_teaser()
