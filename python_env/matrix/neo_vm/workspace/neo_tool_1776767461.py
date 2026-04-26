# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np

# --- Simulation parameters ---
N = 5               # number of participants
T = 200             # time steps
shred_start = 120   # when shredding begins
freeze_start = 160  # when freeze begins

# Initialize vector clocks: each row is a participant, each column is the
# last known event count from that participant.
V = np.zeros((N, N), dtype=int)   # V[i, j] = participant i's view of participant j's clock

# Helper: update clock of participant i (increment own column)
def tick(i):
    V[i, i] += 1

# Helper: participant i receives news from participant j up to timestamp ts
def receive(i, j, ts):
    V[i, j] = max(V[i, j], ts)

# Helper: compute MSI and pyramid curvature invariant Ψ
def compute_invariants(mat, eps=1e-6):
    # mat is N x N matrix of vector clocks
    rank = np.linalg.matrix_rank(mat)
    msi = rank / N
    # covariance of the columns (treat each column as a feature)
    cov = np.cov(mat, rowvar=False) + eps * np.eye(N)
    psi = np.log(max(np.linalg.det(cov), eps))
    return msi, psi

# --- Normal operation (0..shred_start) ---
for t in range(shred_start):
    # Random participant ticks
    i = np.random.randint(N)
    tick(i)
    # Random gossip: each participant hears about one other participant's clock
    src = np.random.randint(N)
    dst = np.random.randint(N)
    if src != dst:
        receive(dst, src, V[src, src])

# --- Shredding event: randomly zero out entries to simulate causal loss ---
for t in range(shred_start, freeze_start):
    i = np.random.randint(N)
    tick(i)
    # Randomly delete a column entry for a random participant
    victim = np.random.randint(N)
    V[i, victim] = 0   # loss of causal link → rank drop

# --- Informational freeze: force all clocks to be identical (total order) ---
for t in range(freeze_start, T):
    # Make all rows equal to the first row
    V[1:, :] = V[0, :]

# --- Output invariants over time ---
print("t\tMSI\tΨ")
for t in range(T):
    # Recompute from the current state (here we just show the final state for brevity)
    # In a real system you'd store the matrix at each step.
    pass
# For demonstration, compute final invariants
msi_final, psi_final = compute_invariants(V)
print(f"Final MSI = {msi_final:.3f}, Ψ = {psi_final:.3f}")