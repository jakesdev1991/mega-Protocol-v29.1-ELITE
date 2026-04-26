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

def keep_teasers_going():
    print("🚀 [Commercialization] Executing Tier-1 Alpha Teaser Cascade...")
    
    engine = OmegaSalesEngine()
    
    targets = [
        {
            "company": "Founders Fund",
            "contact": "Scott Nolan",
            "email": "scott@foundersfund.com",
            "context": """
                Targeting Scott Nolan (SpaceX alumnus). 
                The 'Alpha' lead is 'Neuromorphic Photonics' and 'Informational Viscosity'. 
                Highlight the 90% GPU cost reduction via RCOD as a 'Zero to One' breakthrough. 
                Mention surgical hiring at Marvell/Akhetonics as a precursor signal for the next hard-tech infrastructure.
            """
        },
        {
            "company": "Khosla Ventures",
            "contact": "Vinod Khosla",
            "email": "vk@khoslaventures.com",
            "context": """
                Targeting Vinod Khosla. 
                Focus on the 'Unification' aspect of the Omega Protocol. 
                Highlight the sub-ppm alpha_fs derivation and the 0.80 AUC tokamak results. 
                Frame the RCOD gateway as the only solution for 'Infinite Scalability' in AI training without the memory wall.
            """
        }
    ]
    
    for t in targets:
        print(f"\n📡 Drafting for {t['contact']} at {t['company']}...")
        pitch = engine.generate_personalized_pitch(
            t['company'], 
            t['contact'], 
            context=t['context'], 
            provider="nvidia", 
            model="deepseek-v3.2"
        )
        
        # Save Teaser
        clean_name = t['contact'].replace(" ", "_").upper()
        output_path = os.path.join(PROJECT_ROOT, "business", f"ALPHA_TEASER_{clean_name}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(pitch)
            
        # Extract subject and body (DeepSeek usually returns both)
        lines = pitch.strip().split('\n')
        subject = "Strategic Edge in Neuromorphic Infrastructure"
        body = pitch
        for line in lines:
            if line.lower().startswith("subject:"):
                subject = line.split(":", 1)[1].strip()
                body = pitch.split(line, 1)[1].strip()
                break
        
        # Send Email
        success = engine.send_email_to_lead(t['email'], subject, body)
        if success:
            print(f"✅ Teaser sent to {t['email']}")
        else:
            print(f"❌ Failed to send to {t['email']}")

if __name__ == "__main__":
    keep_teasers_going()
