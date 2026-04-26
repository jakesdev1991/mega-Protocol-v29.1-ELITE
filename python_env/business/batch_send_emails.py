# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import csv
import re
from datetime import date

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from business.sales_automation_engine import OmegaSalesEngine

CRM_FILE = os.path.join(PROJECT_ROOT, "official_launch", "business", "crm_tracker.csv")
PITCHES_FILE = os.path.join(PROJECT_ROOT, "official_launch", "docs", "GENERATED_PITCHES.md")

DATASHEET_FILE = os.path.join(PROJECT_ROOT, "official_launch", "docs", "TECHNICAL_DATASHEET_V1.md")

def batch_send():
    engine = OmegaSalesEngine()
    
    if not os.path.exists(PITCHES_FILE):
        print(f"❌ Error: {PITCHES_FILE} not found. Generate pitches first.")
        return

    # Load Datasheet
    datasheet_content = ""
    if os.path.exists(DATASHEET_FILE):
        with open(DATASHEET_FILE, 'r', encoding='utf-8') as f:
            datasheet_content = f.read()

    # 1. Parse the Generated Pitches Markdown file
    with open(PITCHES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by lead entries (## Company | Contact)
    entries = re.split(r'## ', content)[1:]
    
    for entry in entries:
        lines = entry.strip().split('\n')
        header = lines[0].split(' | ')
        company = header[0].strip()
        contact = header[1].strip()
        
        # Extract the pitch body (usually after "> ")
        pitch_match = re.search(r'> (.*)', entry, re.DOTALL)
        if not pitch_match:
            print(f"⚠️ Could not parse pitch for {company}. Skipping.")
            continue
        
        full_pitch = pitch_match.group(1).strip()
        
        # 2. Extract Subject Line if present
        subject = f"Strategic GPU Cost Reduction for {company} (90% via RCOD)"
        body = full_pitch
        
        subject_search = re.search(r'(Subject|SUBJECT):\s*(.*)', full_pitch)
        if subject_search:
            subject = subject_search.group(2).strip()
            body = re.sub(r'(Subject|SUBJECT):\s*.*', '', full_pitch).strip()
        
        # 3. Clean up the body and subject (remove ALL AI artifacts)
        subject = subject.replace('*', '').strip()
        
        # Truncate at common AI strategy headers
        strategy_markers = ["Why this works", "Strategic logic", "Strategy:", "Objective:"]
        for marker in strategy_markers:
            if marker in body:
                body = body.split(marker)[0].strip()

        # Replace placeholders with Jacob's real info
        body = body.replace("[Your Full Name]", "Jacob See")
        body = body.replace("[Your Name]", "Jacob See")
        body = body.replace("Senior Sales Engineer | Omega Protocol", "Founder & Creator | Omega Protocol")
        body = body.replace("[Your Direct Line]", "217-799-8720")
        
        # Ensure no double sign-offs
        if "Jacob See" not in body:
            body += "\n\nBest,\n\nJacob See\nFounder & Creator | Omega Protocol\n217-799-8720"

        # Append Datasheet
        if datasheet_content:
            body += "\n\n" + "="*40 + "\nTECHNICAL DATASHEET: OMEGA PROTOCOL V1.0\n" + "="*40 + "\n\n" + datasheet_content

        body = body.replace('*', '').replace('---', '').replace('"', '').strip()

        # 4. Find the lead's email or use a placeholder
        recipient = "jake.s.dev1991+lead@gmail.com" 
        
        print(f"🚀 Attempting to send personalized email to {contact} at {company}...")
        
        success = engine.send_email_to_lead(
            recipient_email=recipient,
            subject=subject,
            body=body
        )

        if success:
            print(f"✅ Email sent successfully to {company}!")
        else:
            print(f"❌ Failed to send email to {company}. Check your App Password.")

if __name__ == "__main__":
    batch_send()
