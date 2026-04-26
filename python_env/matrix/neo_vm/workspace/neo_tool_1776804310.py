# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import random
import collections
import math
import statistics
import sys

# ----------------------------------------------------------------------
# Simple tree structure to model directory leakage surface
# ----------------------------------------------------------------------
class DirectoryNode:
    __slots__ = ('name', 'parent', 'children', 'sensitive')
    def __init__(self, name, parent=None, sensitive=False):
        self.name = name
        self.parent = parent
        self.children = []
        self.sensitive = sensitive

class LeakageSurface:
    def __init__(self, depth=4, branching=3):
        self.root = DirectoryNode('root')
        self._build_tree(self.root, depth, branching)
        # Mark one leaf as the "target" sensitive log
        leaves = self._leaves()
        if leaves:
            random.choice(leaves).sensitive = True

    def _build_tree(self, node, depth, branching):
        if depth == 0:
            return
        for i in range(branching):
            child = DirectoryNode(f'{node.name}_{i}', parent=node)
            node.children.append(child)
            self._build_tree(child, depth-1, branching)

    def _leaves(self):
        leaves = []
        stack = [self.root]
        while stack:
            n = stack.pop()
            if not n.children:
                leaves.append(n)
            else:
                stack.extend(n.children)
        return leaves

    # Curvature proxy: average degree (higher = "bushier" = positive curvature)
    def curvature_metric(self):
        total_nodes = 0
        total_degree = 0
        stack = [self.root]
        while stack:
            n = stack.pop()
            total_nodes += 1
            total_degree += len(n.children) + (1 if n.parent else 0)  # degree = children + parent
            stack.extend(n.children)
        return total_degree / total_nodes if total_nodes else 0

    # Simulate adversary BFS from root until sensitive node found
    def adversary_bfs(self, max_steps=1000):
        queue = collections.deque([self.root])
        visited = set()
        steps = 0
        while queue and steps < max_steps:
            node = queue.popleft()
            if node in visited:
                continue
            visited.add(node)
            steps += 1
            if node.sensitive:
                return True, steps
            queue.extend(node.children)
        return False, steps

    # Chaotic defense: randomly add/remove 30% of nodes (only leaves to keep tree valid)
    def chaotic_perturb(self, perturb_rate=0.3):
        leaves = self._leaves()
        # Remove random leaves
        remove_count = int(len(leaves) * perturb_rate)
        for _ in range(remove_count):
            if len(leaves) <= 1:
                break
            victim = random.choice(leaves)
            if victim.parent and victim in victim.parent.children:
                victim.parent.children.remove(victim)
                leaves.remove(victim)

        # Add random children to random nodes (including root)
        all_nodes = []
        stack = [self.root]
        while stack:
            n = stack.pop()
            all_nodes.append(n)
            stack.extend(n.children)
        add_count = int(len(all_nodes) * perturb_rate)
        for _ in range(add_count):
            parent = random.choice(all_nodes)
            new_child = DirectoryNode(f'{parent.name}_d{random.randint(0, 99999)}', parent=parent)
            parent.children.append(new_child)

# ----------------------------------------------------------------------
# Monte Carlo experiment
# ----------------------------------------------------------------------
def run_trials(trials=200, epochs=10, perturb=False):
    success_rates = []
    curvatures = []
    for _ in range(trials):
        tree = LeakageSurface(depth=4, branching=3)
        curvatures.append(tree.curvature_metric())
        success, _ = tree.adversary_bfs()
        success_rates.append(1.0 if success else 0.0)

        if perturb:
            for _ in range(epochs):
                tree.chaotic_perturb(perturb_rate=0.3)
                curvatures.append(tree.curvature_metric())
                success, _ = tree.adversary_bfs()
                success_rates.append(1.0 if success else 0.0)

    return success_rates, curvatures

if __name__ == '__main__':
    # Baseline (static tree)
    print("=== Baseline (static leakage surface) ===")
    base_success, base_curv = run_trials(trials=500, perturb=False)
    print(f"Avg success rate: {statistics.mean(base_success):.3f}")
    print(f"Avg curvature: {statistics.mean(base_curv):.3f}")
    print(f"Curvature CV: {statistics.stdev(base_curv)/statistics.mean(base_curv):.3f}")

    # Chaotic defense
    print("\n=== Chaotic defense (30% perturb/epoch) ===")
    chaos_success, chaos_curv = run_trials(trials=500, perturb=True, epochs=5)
    print(f"Avg success rate: {statistics.mean(chaos_success):.3f}")
    print(f"Avg curvature: {statistics.mean(chaos_curv):.3f}")
    print(f"Curvature CV: {statistics.stdev(chaos_curv)/statistics.mean(chaos_curv):.3f}")