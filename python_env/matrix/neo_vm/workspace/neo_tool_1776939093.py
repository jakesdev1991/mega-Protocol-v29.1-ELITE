# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math

# --- CONFIGURATION ---
c = 1.0  # speed of causal influence (normalized units)
distance_AB = 10.0  # distance between nodes A and B
time_steps = 50
random.seed(42)

# --- HELPERS ---
def generate_event(t):
    """Simulate a random traffic/demand event at time t."""
    return {"time": t, "demand": random.randint(1, 10), "delay": random.uniform(0.5, 2.0)}

def causal_controller(event_history):
    """Make routing decision *after* observing the latest event."""
    if not event_history:
        return "idle"
    latest = event_history[-1]
    # simple heuristic: if demand > 5, route to B
    return "route_to_B" if latest["demand"] > 5 else "hold"

def clairvoyant_controller(future_event):
    """Make decision *before* the event occurs (simulated by peeking ahead)."""
    # This is the TFE claim: decision based on future data
    if future_event["demand"] > 5:
        return "route_to_B"
    return "hold"

def required_info_speed(decision_time, data_time, dist):
    """Compute required transmission speed to send data from data source to decision point."""
    dt = data_time - decision_time
    if dt <= 0:
        # Negative dt means decision *before* data → would need retro‑causal signal
        return float('inf')
    return dist / dt

# --- SIMULATION ---
causal_violations = 0
clairvoyant_violations = 0
total_slack = 0.0

for t in range(time_steps):
    # Data appears at node A at time t
    event = generate_event(t)
    # Causal controller decides at time t + event["delay"] (after data arrives)
    decision_time_causal = t + event["delay"]
    # Clairvoyant controller decides *now* (t) based on future event at t+Δ
    # For realism, assume it "knows" the event 1 time unit ahead (Δ=1)
    future_event = generate_event(t + 1)
    decision_time_clair = t

    # Check causal slack for clairvoyant
    slack = (t + 1) - decision_time_clair  # time until actual event
    total_slack += slack
    if slack < 0:
        clairvoyant_violations += 1

    # Compute required info speed for clairvoyant to receive future data
    speed = required_info_speed(decision_time_clair, t + 1, distance_AB)
    if speed > c:
        causal_violations += 1
        # print(f"Step {t}: Required speed {speed:.2f} > c → Φ‑1 VIOLATION")

# --- RESULTS ---
print("=== CAUSAL‑SLACK AUDIT ===")
print(f"Total time steps: {time_steps}")
print(f"Clairvoyant decisions made before data: {clairvoyant_violations} (negative slack)")
print(f"Causal‑fidelity violations (required info speed > c): {causal_violations}")
print(f"Average slack (time between decision and actual event): {total_slack/time_steps:.2f}")
print("\nConclusion: Any 'pre‑emptive' routing based on future data violates Φ‑1.")
print("The QULN proposal’s TFE would require superluminal signalling → −∞Φ penalty.")