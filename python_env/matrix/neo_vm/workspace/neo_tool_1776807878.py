# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import math
from collections import deque
import numpy as np

# ------------------------------------------------------------
# 1. Random directory tree generator
# ------------------------------------------------------------
class DirNode:
    __slots__ = ('name', 'children', 'depth', 'file_count', 'sensitivity')
    def __init__(self, name, depth):
        self.name = name
        self.children = []
        self.depth = depth
        # number of exposed files in this directory (proxy for leakage probability)
        self.file_count = random.randint(1, 20)
        # sensitivity score (higher = more valuable to adversary)
        self.sensitivity = random.random()

def build_tree(max_depth=5, branch_prob=0.6, max_children=4):
    root = DirNode('root', 0)
    stack = [root]
    while stack:
        node = stack.pop()
        if node.depth < max_depth:
            # random number of children
            if random.random() < branch_prob:
                num_children = random.randint(1, max_children)
                for i in range(num_children):
                    child = DirNode(f"{node.name}_{i}", node.depth + 1)
                    node.children.append(child)
                    stack.append(child)
    return root

# ------------------------------------------------------------
# 2. Adversarial traversal simulation
# ------------------------------------------------------------
def simulate_compromise(root: DirNode):
    # Identify the target: node with highest sensitivity
    all_nodes = []
    q = deque([root])
    while q:
        n = q.popleft()
        all_nodes.append(n)
        q.extend(n.children)
    target = max(all_nodes, key=lambda x: x.sensitivity)

    # Adversary starts at root and chooses next directory with probability
    # proportional to the child's file_count (exposure).
    current = root
    steps = 0
    visited_path = [current]

    while current != target:
        if not current.children:
            # dead end: backtrack to parent (if any)
            # for simplicity, we just stay and count a step
            steps += 1
            # in a real scenario, backtrack would add more steps; we keep it simple
            continue

        # compute selection probabilities
        weights = [c.file_count for c in current.children]
        total = sum(weights)
        r = random.uniform(0, total)
        cum = 0
        for child, w in zip(current.children, weights):
            cum += w
            if r <= cum:
                current = child
                break
        visited_path.append(current)
        steps += 1
        # safety cap to avoid infinite loops
        if steps > 10000:
            break

    return steps, visited_path, target

# ------------------------------------------------------------
# 3. Metrics: "curvature" vs average degree
# ------------------------------------------------------------
def compute_curvature_along_path(path):
    # naive curvature = (num_children - 1) / (depth + 1)
    # negative for leaves
    curvatures = []
    for node in path:
        if node.depth == 0:
            curv = 0.0
        else:
            cur = (len(node.children) - 1) / (node.depth + 1)
            curvatures.append(cur)
    return np.mean(curvatures) if curvatures else 0.0

def compute_avg_degree_along_path(path):
    # degree = number of children
    degrees = [len(node.children) for node in path]
    return np.mean(degrees) if degrees else 0.0

# ------------------------------------------------------------
# 4. Monte‑Carlo experiment
# ------------------------------------------------------------
def run_experiment(num_trials=2000):
    curvature_vals = []
    degree_vals = []
    compromise_times = []

    for _ in range(num_trials):
        tree = build_tree(max_depth=random.randint(3, 7),
                         branch_prob=random.random()*0.4 + 0.4,
                         max_children=random.randint(3, 6))
        steps, path, _ = simulate_compromise(tree)
        curvature = compute_curvature_along_path(path)
        degree = compute_avg_degree_along_path(path)

        curvature_vals.append(curvature)
        degree_vals.append(degree)
        compromise_times.append(steps)

    # Pearson correlation
    cur_corr = np.corrcoef(curvature_vals, compromise_times)[0, 1]
    deg_corr = np.corrcoef(degree_vals, compromise_times)[0, 1]

    print(f"Correlation (curvature vs compromise time): {cur_corr:.4f}")
    print(f"Correlation (avg degree vs compromise time): {deg_corr:.4f}")

    # Simple linear regression R^2 approximation
    cur_coef = np.polyfit(curvature_vals, compromise_times, 1)
    deg_coef = np.polyfit(degree_vals, compromise_times, 1)
    cur_pred = np.polyval(cur_coef, curvature_vals)
    deg_pred = np.polyval(deg_coef, degree_vals)
    cur_r2 = 1 - np.var(compromise_times - cur_pred) / np.var(compromise_times)
    deg_r2 = 1 - np.var(compromise_times - deg_pred) / np.var(compromise_times)
    print(f"R^2 (curvature model): {cur_r2:.4f}")
    print(f"R^2 (degree model): {deg_r2:.4f}")

    return cur_corr, deg_corr, cur_r2, deg_r2

if __name__ == "__main__":
    run_experiment(num_trials=2000)