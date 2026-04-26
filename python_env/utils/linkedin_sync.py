# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# LinkedIn Sync Utility - v1.0
# ---------------------------------------------------------------------------

import asyncio
import json
import os
from playwright.async_api import async_playwright

async def sync_linkedin():
    # Load the draft we generated
    draft_path = "docs/business/LINKEDIN_PROFILE_DRAFT.md"
    if not os.path.exists(draft_path):
        print(f"❌ Error: {draft_path} not found. Run the profile generator first.")
        return

    with open(draft_path, "r") as f:
        content = f.read()

    print("🚀 [Omega-LinkedIn] Initializing Sovereign Sync Engine...")
    print("💡 INSTRUCTIONS: A browser window will open. Login to LinkedIn manually.")
    print("💡 Once logged in, press ENTER in this terminal to start the data injection.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Must be visible for login
        context = await browser.new_context()
        page = await context.new_page()

        # Go to LinkedIn
        await page.goto("https://www.linkedin.com/login")

        # Wait for user to login manually
        input("\n👉 Press ENTER here after you have successfully logged in and are on your home feed...")

        print("🧬 [Omega-LinkedIn] Starting surgical data injection...")

        # 1. Update Personal Headline
        try:
            print("[*] Targeting Headline...")
            await page.goto("https://www.linkedin.com/edit/main-profile/")
            # Wait for the modal/fields to load
            await page.wait_for_selector("input[name='headline']")
            
            headline = "Jacob M. | Owner & Lead Architect at Omega Solutions | Pioneer of The Omega Protocol"
            await page.fill("input[name='headline']", headline)
            print("✅ Headline Injected.")
            
            # Note: LinkedIn's UI is complex. For a first version, 
            # we will provide the user with the snippets to copy-paste 
            # if the selectors fail due to their bot detection.
        except Exception as e:
            print(f"⚠️ Automated injection encountered an impedance: {e}")
            print("💡 Switching to CLI-Assisted Copy-Paste Mode.")

        print("\n" + "="*50)
        print(" OMEGA SOLUTIONS: LINKEDIN SNIPPETS")
        print("="*50)
        print(f"\n[TAGLINE]\nEngineering the foundational protocols for autonomous systems, from AI agents to stable fusion.")
        print(f"\n[HEADLINE]\nJacob M. | Owner & Lead Architect at Omega Solutions | Pioneer of The Omega Protocol for Autonomous System Stability")
        print(f"\n[BIO - ABOUT SECTION]\n(Full bio is in docs/business/LINKEDIN_PROFILE_DRAFT.md)")
        print("\n" + "="*50)

        # Keep browser open for a bit
        print("\nBrowser is open. You can manually finalize the changes now.")
        await asyncio.sleep(300) 
        await browser.close()

if __name__ == "__main__":
    asyncio.run(sync_linkedin())
