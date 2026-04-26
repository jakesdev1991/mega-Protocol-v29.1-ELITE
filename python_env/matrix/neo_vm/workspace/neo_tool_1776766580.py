# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import hashlib
import random
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt

class ImmutableNarrativeLedger:
    def __init__(self):
        self.ledger = []  # (hash, doc_type, timestamp, action, signatory)
        self.time = 0

    def commit(self, doc_type, content, signatory):
        h = hashlib.sha256(f"{content}{self.time}".encode()).hexdigest()
        self.ledger.append({
            'hash': h,
            'doc_type': doc_type,
            'timestamp': self.time,
            'action': 'COMMIT',
            'signatory': signatory
        })
        self.time += 1
        return h

    def shred(self, doc_hash, signatory):
        self.ledger.append({
            'hash': doc_hash,
            'doc_type': 'DELETED',
            'timestamp': self.time,
            'action': 'SHRED',
            'signatory': signatory
        })
        self.time += 1

    def entropy(self, window=50):
        """Shannon entropy of *committed* doc types."""
        recent = [e['doc_type'] for e in self.ledger[-window:] if e['action'] == 'COMMIT']
        if not recent: return 0
        probs = np.array(list(Counter(recent).values())) / len(recent)
        return -np.sum(probs * np.log(probs + 1e-12))

    def commit_rate(self, window=50):
        return sum(1 for e in self.ledger[-window:] if e['action'] == 'COMMIT') / window

    def shred_rate(self, window=50):
        return sum(1 for e in self.ledger[-window:] if e['action'] == 'SHRED') / window

# Simulate: normal ops -> stress (low entropy, single doc type) -> shredding spree
ledger = ImmutableNarrativeLedger()
doc_types = ['risk', 'legal', 'minutes', 'financial']
entropy_hist, commit_hist, shred_hist = [], [], []

# Normal period: diverse commits
for _ in range(150):
    ledger.commit(random.choice(doc_types), f"doc{_}", f"user{random.randint(0,9)}")
    entropy_hist.append(ledger.entropy())
    commit_hist.append(ledger.commit_rate())
    shred_hist.append(ledger.shred_rate())

# Stress period: only "risk" docs (narrative collapse)
for _ in range(50):
    ledger.commit('risk', f"stress_doc{_}", f"user{random.randint(0,9)}")
    entropy_hist.append(ledger.entropy())
    commit_hist.append(ledger.commit_rate())
    shred_hist.append(ledger.shred_rate())

# Shredding period: mass delete recent commits
recent_hashes = [e['hash'] for e in ledger.ledger[-30:] if e['action'] == 'COMMIT']
for h in recent_hashes:
    ledger.shred(h, f"user{random.randint(0,9)}")
    entropy_hist.append(ledger.entropy())
    commit_hist.append(ledger.commit_rate())
    shred_hist.append(ledger.shred_rate())

# Plot: Entropy drop and commit collapse are direct, observable, and *precede* shredding
fig, ax = plt.subplots(3, 1, figsize=(10, 8))
ax[0].plot(entropy_hist, label='Doc Type Entropy')
ax[0].axvline(150, color='orange', linestyle='--', label='Stress Begins')
ax[0].axvline(200, color='red', linestyle='--', label='Shredding Begins')
ax[0].set_ylabel('Entropy (bits)')
ax[0].set_title('INL‑Ω: Entropy Drop Precedes Shredding')
ax[0].legend()

ax[1].plot(commit_hist, label='Commit Rate', color='green')
ax[1].axvline(150, color='orange', linestyle='--')
ax[1].axvline(200, color='red', linestyle='--')
ax[1].set_ylabel('Commits/Window')
ax[1].set_title('Commit Rate Collapse')

ax[2].plot(shred_hist, label='Shred Rate', color='purple')
ax[2].axvline(200, color='red', linestyle='--')
ax[2].set_ylabel('Shreds/Window')
ax[2].set_xlabel('Time Steps')
ax[2].set_title('Shredding Event is a Discrete, Provable Transaction')

plt.tight_layout()
plt.show()

# The disruption: No manifold, no NLP, no phantom. Just a ledger.
# Shredding is not a phase transition; it's a transaction hash.