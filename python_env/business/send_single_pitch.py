# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys
import re

# Ensure project root is in path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(PROJECT_ROOT)

from business.sales_automation_engine import OmegaSalesEngine

PITCHES_FILE = os.path.join(PROJECT_ROOT, "official_launch", "docs", "GENERATED_PITCHES.md")

DATASHEET_FILE = os.path.join(PROJECT_ROOT, "official_launch", "docs", "TECHNICAL_DATASHEET_V1.md")

def send_single(target_company):
    engine = OmegaSalesEngine()
    
    if not os.path.exists(PITCHES_FILE):
        print(f"❌ Error: {PITCHES_FILE} not found.")
        return

    # Load Datasheet
    datasheet_content = ""
    if os.path.exists(DATASHEET_FILE):
        with open(DATASHEET_FILE, 'r', encoding='utf-8') as f:
            datasheet_content = f.read()

    with open(PITCHES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the specific entry
    entries = re.split(r'## ', content)[1:]
    target_entry = None
    for entry in entries:
        if target_company.lower() in entry.lower():
            target_entry = entry
            break
    
    if not target_entry:
        print(f"❌ Could not find pitch for {target_company}")
        return

    # Parse and Clean
    pitch_match = re.search(r'> (.*)', target_entry, re.DOTALL)
    if not pitch_match:
        print(f"⚠️ Could not parse pitch body.")
        return
    
    full_pitch = pitch_match.group(1).strip()
    
    # Extract Subject
    subject = f"Strategic GPU Cost Reduction for {target_company}"
    body = full_pitch
    
    subject_search = re.search(r'(Subject|SUBJECT):\s*(.*)', full_pitch)
    if subject_search:
        subject = subject_search.group(2).strip()
        body = re.sub(r'(Subject|SUBJECT):\s*.*', '', full_pitch).strip()
    
    # Final Clean (Remove ALL AI artifacts, especially asterisks and strategy blocks)
    subject = subject.replace('*', '').strip()
    
    # Truncate at common AI strategy headers if they exist
    strategy_markers = ["Why this works", "Strategic logic", "Strategy:", "Objective:"]
    for marker in strategy_markers:
        if marker in body:
            body = body.split(marker)[0].strip()

    # Replace placeholders with Jacob's real info
    body = body.replace("[Your Full Name]", "Jacob See")
    body = body.replace("[Your Name]", "Jacob See")
    body = body.replace("Senior Sales Engineer | Omega Protocol", "Founder & Creator | Omega Protocol")
    body = body.replace("[Your Direct Line]", "217-799-8720")
    body = body.replace("[Your Calendly Link]", "")
    
    # Ensure no double sign-offs
    if "Jacob See" not in body:
        body += "\n\nBest,\n\nJacob See\nFounder & Creator | Omega Protocol\n217-799-8720"

    # Append Datasheet for value verification
    if datasheet_content:
        body += "\n\n" + "="*40 + "\nTECHNICAL DATASHEET: OMEGA PROTOCOL V1.0\n" + "="*40 + "\n\n" + datasheet_content

    body = body.replace('*', '').replace('---', '').replace('"', '').strip()

    recipient = "jake.s.dev1991+lead@gmail.com"
    print(f"🚀 Sending clean pitch with Datasheet to {target_company} (Test Inbox)...")
    
    success = engine.send_email_to_lead(recipient, subject, body)
    if success:
        print(f"✅ Success! Check your inbox for the {target_company} pitch.")
    else:
        print(f"❌ Failed to send.")

if __name__ == "__main__":
    send_single("Vast Data")
