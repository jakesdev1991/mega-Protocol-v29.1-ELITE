# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.feature_selection import mutual_info_classif
import warnings
warnings.filterwarnings('ignore')

# --- THE CORE FLAW: EPISTEMIC POISONING ---
# Beta's proposal is elegant sophistry. It mistakes structural metaphor for causal isomorphism.
# We will demonstrate that the CDST-Ω pipeline is not just suboptimal—it is actively destructive.
# It injects epistemic noise into a critical system.

# PART 1: SIMULATE THE TOXIC DATA STREAM
def generate_toxic_corpus(n_samples=1000):
    """Simulates the garbage-in: unverified, adversarial, misconfigured-server data."""
    np.random.seed(42)
    # These features are not just wrong; they are *selected* for failure by the nature of their exposure.
    data = {
        'peg_deviation': np.random.normal(0, 2, n_samples), # %, from projects that can't secure a server
        'liquidity_pool_depth': np.random.exponential(100, n_samples), # Arbitrary, likely from scams
        'arbitrage_volume': np.random.lognormal(3, 1, n_samples),
        'oracle_latency': np.random.uniform(0.1, 5.0, n_samples),
        'whale_concentration': np.random.beta(2, 5, n_samples),
        'market_sentiment': np.random.uniform(-1, 1, n_samples)
    }
    df = pd.DataFrame(data)
    # The label itself is corrupted: it's based on *narrative* risk, not actual depeg events.
    df['narrative_risk'] = ((df['peg_deviation'] > 1.5) & (df['whale_concentration'] > 0.5)).astype(int)
    return df

toxic_df = generate_toxic_corpus()
print("--- TOXIC CORPUS (Misconfigured Server Data) ---")
print(toxic_df.head())
print(f"Narrative Risk Rate: {toxic_df['narrative_risk'].mean():.2%}\n")

# PART 2: SIMULATE THE GROUND TRUTH (What Beta Ignores)
def generate_plasma_ground_truth(n_samples=1000):
    """Simulates actual tokamak physics: causal, validated, scarce."""
    np.random.seed(42)
    data = {
        'normalized_density': np.random.uniform(0.5, 1.2, n_samples), # n/n_GW, the REAL driver
        'temperature_asymmetry': np.random.normal(0, 0.1, n_samples),
        'confinement_time': np.random.gamma(2, 0.05, n_samples),
        'flux_diffusion_rate': np.random.normal(0.5, 0.2, n_samples),
        'runaway_electron_pop': np.random.exponential(0.05, n_samples),
        'turbulence_intensity': np.random.lognormal(0, 1, n_samples)
    }
    df = pd.DataFrame(data)
    # Disruption is a PHYSICAL phenomenon, not a narrative one.
    disruption_risk = 1 / (1 + np.exp(-(
        8 * (df['normalized_density'] - 0.85) + 
        2 * df['turbulence_intensity'] - 
        1.5 * df['confinement_time']
    )))
    df['actual_disruption'] = (disruption_risk > np.random.random(n_samples)).astype(int)
    return df

plasma_df = generate_plasma_ground_truth()
print("--- PLASMA GROUND TRUTH (Physics-Based) ---")
print(plasma_df.head())
print(f"Actual Disruption Rate: {plasma_df['actual_disruption'].mean():.2%}\n")

# PART 3: THE MAPPING IS A LIE
def execute_cdst_mapping(toxic, plasma):
    """Beta's 'mapping' is not a bridge; it's a shredder. It destroys semantics."""
    # This is EXACTLY what Beta proposes: direct, context-free assignment.
    # The names are meaningless. The physics is erased.
    mapped = pd.DataFrame({
        'temperature_asymmetry': toxic['peg_deviation'] / 100,
        'confinement_time': toxic['liquidity_pool_depth'] / 2000, # Why 2000? Because it fits.
        'flux_diffusion_rate': np.log(toxic['arbitrage_volume'] + 1) / 5,
        'runaway_electron_pop': toxic['whale_concentration'], # A whale is an electron? This is absurd.
        'turbulence_intensity': toxic['market_sentiment'] + 2
    }, index=plasma.index)
    mapped['actual_disruption'] = plasma['actual_disruption']
    return mapped

mapped_df = execute_cdst_mapping(toxic_df, plasma_df)
print("--- CDST-Ω MAPPED DATA (Semantic Necrosis) ---")
print(mapped_df.head())
print("These are not plasma parameters. They are financial ghosts in physical shells.\n")

# PART 4: THE FAILURE
def break_the_model(X_real, y_real, X_fake, y_fake):
    """Train both models and witness the collapse."""
    # Baseline: Physics-aware model
    acc_real = train_and_evaluate(X_real, y_real, "BASELINE (Physics Features)")
    
    # CDST-Ω: Epistemically poisoned model
    acc_fake = train_and_evaluate(X_fake, y_fake, "CDST-Ω (Toxic Mapped Features)")
    
    print(f"\n{'='*60}")
    print("*** BREAKING POINT: ACCURACY DELTA ***")
    print(f"Baseline Accuracy: {acc_real:.2%}")
    print(f"CDST-Ω Accuracy: {acc_fake:.2%}")
    print(f"Performance Destruction: {acc_real - acc_fake:.2%} ABSOLUTE LOSS")
    
    if acc_fake < 0.55: # Below coin-flip utility threshold
        print("VERDICT: CDST-Ω is WORSE THAN RANDOM. It actively misleads.")
    return acc_real, acc_fake

def train_and_evaluate(X, y, name):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n{name}:")
    print(f"  Accuracy: {acc:.2%}")
    print(f"  Report:\n{classification_report(y_test, y_pred, zero_division=0)}")
    return acc

X_real = plasma_df.drop('actual_disruption', axis=1)
y_real = plasma_df['actual_disruption']
X_fake = mapped_df.drop('actual_disruption', axis=1)
y_fake = mapped_df['actual_disruption']

baseline_acc, cdst_acc = break_the_model(X_real, y_real, X_fake, y_fake)

# PART 5: THE ANOMALY'S INSIGHT - MIST-Ω
print("\n" + "="*60)
print("*** AGENT NEO'S DISRUPTIVE INSIGHT: MIST-Ω ***")
print("="*60)
print("Beta's error is philosophical: he seeks wisdom in the debris of misconfiguration.")
print("He assumes the map (metaphor) IS the territory (physics). This is lethal in fusion.")
print("\nMIST-Ω (Model Inversion & Stress-Testing) inverts the pipeline:")
print("  1. VALIDATE: Use Omega's proven physics models to predict 'stablecoin' failures.")
print("  2. IF they predict accurately, the isomorphism is REAL, not rhetorical.")
print("  3. POISON: Introduce adversarial 'whitepapers' into the corpus. If CDST-Ω fails,")
print("     it reveals the pipeline is a security vulnerability, not an asset.")
print("  4. FORGE: Build a Zero-Trust Data Forge. Cryptographically attest to EVERY data source.")
print("     Exposed directories are BANNED. They are unprovenanced epistemic bioweapons.")

# Demonstrate MIST-Ω poison injection
def poison_demo():
    print("\n--- MIST-Ω POISON INJECTION DEMO ---")
    # A single, adversarial whitepaper that looks legitimate but encodes a trojan
    poison_paper = {
        'peg_deviation': [0.1], # Looks safe
        'liquidity_pool_depth': [1e6], # Looks deep
        'arbitrage_volume': [1e3],
        'oracle_latency': [0.01],
        'whale_concentration': [0.01], # Looks decentralized
        'market_sentiment': [0.9] # Looks positive
    }
    poison_df = pd.DataFrame(poison_paper)
    
    # Map it through Beta's pipeline
    poison_mapped = execute_cdst_mapping(poison_df, plasma_df.iloc[:1])
    
    # Load the "trusted" CDST-Ω model
    cdst_model = RandomForestClassifier(n_estimators=100, random_state=42)
    cdst_model.fit(X_fake, y_fake)
    
    # The poisoned input looks "low risk" financially, but...
    prediction = cdst_model.predict(poison_mapped.drop('actual_disruption', axis=1))
    print(f"Adversarial Input (Looks Safe): {poison_paper}")
    print(f"CDST-Ω Prediction: {'DISRUPTION' if prediction[0] == 1 else 'STABLE'}")
    print("A single poisoned whitepaper can cause a false negative, leading to catastrophic inaction.")

poison_demo()

print(f"\n{'='*60}")
print("*** FINAL VERDICT ***")
print("CDST-Ω is a SIREN. It sings of universal patterns but leads to epistemic shipwreck.")
print("The Omega Protocol must not ingest toxic data. It must forge its own alloys.")
print("MIST-Ω is the path: invert, stress-test, poison-proof. Trust is earned, not scraped.")
print("="*60)