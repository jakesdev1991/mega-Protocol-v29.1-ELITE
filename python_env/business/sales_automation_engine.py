# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import json
import csv
import requests
import datetime
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Add project root to path to ensure utils is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(PROJECT_ROOT)

from utils.nvidia_client import NvidiaClient

try:
    from psychology.sales_resonance_refiner import SalesResonanceRefiner
    HAS_PSYCH = True
except ImportError:
    HAS_PSYCH = False

# --- CONFIGURATION ---
ENV_FILE = os.path.join(PROJECT_ROOT, "business", "API_CONNECTION_KEYS.env")
load_dotenv(ENV_FILE)
CRM_FILE = os.path.join(PROJECT_ROOT, "official_launch", "business", "crm_tracker.csv")
LEADS_FILE = os.path.join(PROJECT_ROOT, "official_launch", "business", "TARGET_EMAIL_LIST.txt")
PITCH_FILE = os.path.join(PROJECT_ROOT, "official_launch", "docs", "OMEGA_COMMERCIAL_PITCH.md")

class OmegaSalesEngine:
    def __init__(self):
        self.pitch_content = self._load_pitch()
        self._ensure_crm_exists()
        self.nvidia = NvidiaClient()

    def _load_pitch(self):
        if not os.path.exists(PITCH_FILE):
            return "Omega Protocol: 90% GPU cost reduction via RCOD curvature gating."
        with open(PITCH_FILE, 'r') as f:
            return f.read()

    def _ensure_crm_exists(self):
        os.makedirs(os.path.dirname(CRM_FILE), exist_ok=True)
        if not os.path.exists(CRM_FILE):
            with open(CRM_FILE, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Company", "Contact", "Status", "Last_Action", "Next_Step"])

    def generate_personalized_pitch(self, company_name, contact_person, context="", provider="local", model="qwen2.5:0.5b"):
        """
        Uses either local LTM + Qwen or NVIDIA APIs to personalize the pitch.
        """
        print(f"🤖 Generating personalized pitch for {company_name} using {provider}/{model}...")
        
        system_prompt = "You are a Senior Sales Engineer for Omega Protocol. Your goal is to convert technical benchmarks into multi-million dollar business value."
        
        prompt = f"""
        Target: {contact_person} at {company_name}.
        Context: {context}
        
        Core Value Proposition:
        {self.pitch_content[:1000]}
        
        Task: Write a highly personal, professional, and urgent email to this individual as Jacob See, the Founder & Creator of the Omega Protocol.
        1. Incorporate strategic urgency (e.g., this quarter, next procurement cycle).
        2. Establish deep technical credibility (mention RCOD curvature gating, near-linear efficiency, and optionally our PV-BESS multi-market dispatch optimization framework).
        3. Frame the 90% cost reduction or energy self-consumption gains as a strategic competitive weapon, not just a simple cost cut.
        4. Mention that you have attached or can provide a Technical Datasheet with specific benchmarks.
        5. Sign off as Jacob See, Founder & Creator, phone: 217-799-8720.

        Constraint: Provide ONLY the final email text (Subject and Body). 
        Do NOT include any "Why this works" sections, checklists, or meta-commentary. 
        The tone must be indistinguishable from an independent, high-level architect/founder.
        """
        
        if provider == "nvidia":
            try:
                pitch = self.nvidia.chat(model, prompt, system_prompt=system_prompt)
                if HAS_PSYCH:
                    refiner = SalesResonanceRefiner()
                    pitch = refiner.refine(pitch, company_name, contact_person, context)
                return pitch
            except Exception as e:
                print(f"NVIDIA API Error: {e}")
                return f"Error using NVIDIA API: {e}. Falling back to standard pitch."

        # Default Local Ollama
        try:
            response = requests.post("http://localhost:11434/api/generate", 
                                     json={
                                         "model": model, 
                                         "prompt": f"{system_prompt}\n\n{prompt}", 
                                         "stream": False,
                                         "options": {
                                             "num_thread": 12,
                                             "num_ctx": 16384
                                         }
                                     }, timeout=30)
            return response.json().get("response", "Error generating pitch.")
        except Exception as e:
            print(f"Local AI Error: {e}")
            return "Standard Pitch: We can reduce your GPU costs by 90% using the Omega Protocol RCOD gateway."

    def add_lead_to_crm(self, company, contact, status="New"):
        with open(CRM_FILE, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([datetime.date.today(), company, contact, status, "Added to CRM", "Generate Pitch"])
        print(f"✅ Lead {company} added to CRM.")

    def send_email_to_lead(self, recipient_email, subject, body, attachments=None):
        """
        Sends an email with optional attachments.
        attachments: List of file paths.
        """
        sender_email = os.getenv("SENDER_EMAIL")
        app_password = os.getenv("SENDER_APP_PASSWORD")

        if not sender_email or not app_password:
            print("❌ Error: Email credentials not configured.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            if attachments:
                from email.mime.base import MIMEBase
                from email import encoders
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f"attachment; filename= {os.path.basename(file_path)}",
                        )
                        msg.attach(part)

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)
            server.quit()
            
            print(f"📧 Email (with {len(attachments) if attachments else 0} attachments) sent to {recipient_email}")
            return True
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

if __name__ == "__main__":
    engine = OmegaSalesEngine()
    # Example usage:
    # print(engine.generate_personalized_pitch("AMD", "Director of Software", "Optimizing DirectML", provider="nvidia", model="devstral"))
