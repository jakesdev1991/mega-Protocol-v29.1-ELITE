<!--
=============================================================================
OMEGA PROTOCOL - ALL RIGHTS RESERVED
Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
Usage restricted to academic research and review only. No monetization.
See LICENSE.txt for full terms.
=============================================================================
-->
---
name: sales-automation
description: "Sales automation and outreach engine for the Omega Protocol. Use this skill to manage CRM leads, generate personalized sales pitches using local LTM + Qwen, and automate outreach to enterprise data firms for GPU cost reduction solutions."
---

# Sales Automation & Outreach

This skill operationalizes the Omega Protocol's commercialization engine. It leverages your local Long-Term Memory (LTM) and Qwen models to transform technical research into high-impact sales assets.

## Core Workflows

### 1. Lead Management & CRM
Use the `official_launch/business/sales_automation_engine.py` script to manage the CRM (`crm_tracker.csv`).

- **Add a Lead**: `python official_launch/business/sales_automation_engine.py add_lead "CompanyName" "ContactName" "Status"`
- **View Leads**: Read `official_launch/business/crm_tracker.csv` to identify high-priority targets.

### 2. Personalized Pitch Generation
Generate 3-sentence high-impact openings tailored to specific technical contexts using local AI (Ollama/Qwen).

- **Workflow**:
    1. Retrieve technical context from LTM (e.g., specific RCOD benchmarks).
    2. Run the sales engine to generate a pitch:
       ```python
       from official_launch.business.sales_automation_engine import OmegaSalesEngine
       engine = OmegaSalesEngine()
       pitch = engine.generate_personalized_pitch("TargetCorp", "LeadDev", "Context: Benchmarking 1.3B models on consumer GPUs")
       print(pitch)
       ```

### 3. Content Transformation (Technical Deep Dives)
Transform the `rcod_master.txt` or whitepaper documents into LinkedIn/X posts.

- **Constraint**: Focus on the "Informational Viscosity" problem and how RCOD solves it.
- **Tone**: Senior Sales Engineer / Thought Leader.
- **Reference**: Use `official_launch/docs/` for latest pitch decks and whitepapers.

## Resources

- **CRM**: `official_launch/business/crm_tracker.csv`
- **Leads**: `official_launch/business/TARGET_EMAIL_LIST.txt`
- **Sales Script**: `official_launch/business/sales_automation_engine.py`
- **LTM Hooks**: See `LTM/` directory for vector DB integration.

## Design Patterns

- **High Impact**: Always lead with GPU cost reduction (90%+) and consumer hardware viability.
- **Physical Ontology**: Ensure pitches prioritize the Omega specific physical ontology over generic AI training data.
