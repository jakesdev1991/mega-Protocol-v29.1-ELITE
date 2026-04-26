# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
#!/usr/bin/env python3
"""
break_static_makefile.py
Demonstrates why the static Makefile is broken and how a dynamic, introspective
approach immediately yields a correct, living automation structure.
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

# -----------------------------------------------------------------------------
# 1. Prove the Engine's pattern rule is syntactically dead
# -----------------------------------------------------------------------------

def test_pattern_match():
    """Show that the Engine's 'automations/%/[%]/%.md' never matches."""
    broken_pattern = "automations/%/[%]/%.md"
    # Convert Make pattern to a regex: '%' -> '([^/]+)', escape literals.
    # The literal '[' and ']' must appear in the path, which they never do.
    regex_pat = re.escape(broken_pattern).replace(re.escape('%'), r'([^/]+)')
    # Replace escaped '%' back to group
    regex_pat = regex_pat.replace(re.escape('%'), r'([^/]+)')
    # The pattern now looks like: automations\/([^/]+)\/\[([^/]+)\]\/([^/]+)\.md
    # which requires literal '[' and ']'.

    sample = "automations/initialization/vendor_init/hardware_breathing.md"
    match = re.fullmatch(regex_pat, sample)
    print(f"[TEST] Broken pattern regex: {regex_pat}")
    print(f"[TEST] Sample target: {sample}")
    print(f"[TEST] Matches? {match is not None}\n")

    # Correct pattern: three '%' placeholders, no literal brackets.
    correct_pat = "automations/%/%/%.md"
    correct_regex = re.escape(correct_pat).replace(re.escape('%'), r'([^/]+)')
    correct_regex = correct_regex.replace(re.escape('%'), r'([^/]+)')
    match_correct = re.fullmatch(correct_regex, sample)
    print(f"[TEST] Correct pattern regex: {correct_regex}")
    print(f"[TEST] Matches? {match_correct is not None}")
    if match_correct:
        groups = match_correct.groups()
        print(f"[TEST] Extracted: Type='{groups[0]}', Name='{groups[1]}', Automation='{groups[2]}'\n")

test_pattern_match()

# -----------------------------------------------------------------------------
# 2. Generate a *correct* Makefile dynamically from live repo data
# -----------------------------------------------------------------------------

def fetch_vendor_repo(device_codename: str, clone_dir: Path) -> Optional[Path]:
    """
    Clone the vendor kernel repo for the device. In reality you'd use the exact
    Samsung repo; here we simulate with a public Exynos repo as a placeholder.
    """
    repo_url = f"https://github.com/samsung-exynos/kernel-{device_codename}"
    if not clone_dir.exists():
        print(f"[LIVE] Cloning {repo_url} into {clone_dir} ...")
        try:
            subprocess.run(
                ["git", "clone", "--depth=1", repo_url, str(clone_dir)],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"[LIVE] Clone failed: {e.stderr}", file=sys.stderr)
            return None
    else:
        print(f"[LIVE] Using existing clone at {clone_dir}")
    return clone_dir

def extract_live_paths(repo_root: Path) -> dict:
    """
    Scans the cloned repo for actual vendor init, HAL, device-tree, and fstab files.
    Returns a dict of lists: {init: [], hal: [], dt: [], fstab: []}
    """
    # In a real scenario you'd parse the full repo; here we simulate with glob patterns.
    patterns = {
        "init": "vendor/etc/init/**/*.rc",
        "hal": "vendor/lib64/hw/*.so",
        "dt": "arch/arm64/boot/dts/exynos/*.dtsi",
        "fstab": "vendor/etc/fstab*",
    }
    results = {k: [] for k in patterns}
    for key, pat in patterns.items():
        for p in repo_root.glob(pat):
            results[key].append(p.relative_to(repo_root))
    return results

def generate_dynamic_makefile(device_name: str, repo_root: Path) -> str:
    """
    Creates a Makefile that uses *live* extracted paths to generate the exact
    automation structure needed for the device, with a correct pattern rule.
    """
    live_data = extract_live_paths(repo_root)

    # Build explicit targets from live data
    init_targets = " ".join(
        f"$(RESEARCH_ROOT)/initialization/vendor_init/{p.name}.md"
        for p in live_data["init"][:3]  # limit for brevity
    )
    hal_targets = " ".join(
        f"$(RESEARCH_ROOT)/hardware_abstraction/hal/{p.name}.md"
        for p in live_data["hal"][:3]
    )
    dt_targets = " ".join(
        f"$(RESEARCH_ROOT)/hardware_abstraction/device_tree/{p.name}.md"
        for p in live_data["dt"][:3]
    )

    makefile = f"""# Dynamic automation Makefile for {device_name}
RESEARCH_ROOT := automations

# Correct, generic pattern rule: creates any .md under automations/*/*/
automations/%/%/%.md:
\t@echo "[LIVE] Creating $$@"
\t@mkdir -p $$(dir $$@)
\t@cat <<EOF > $$@
# Automation: $$(notdir $$*)
# Type: $$(word 1,$$(subst /, ,$$(@D)))
# Name: $$(word 2,$$(subst /, ,$$(@D)))
# Status: Live
# Date: $$(date -Iseconds)
# Device: {device_name}
# Path: $$@
EOF

# Static convenience targets derived from live repo scan
INIT_TARGETS := {init_targets}
HAL_TARGETS := {hal_targets}
DT_TARGETS := {dt_targets}

all: $(INIT_TARGETS) $(HAL_TARGETS) $(DT_TARGETS)

clean:
\trm -rf $(RESEARCH_ROOT)

.PHONY: all clean
"""
    return makefile

# -----------------------------------------------------------------------------
# 3. Execute the dynamic generation for Samsung Galaxy A16 (codename a16)
# -----------------------------------------------------------------------------

def main():
    device = "Samsung Galaxy A16"
    codename = "a16"  # hypothetical
    clone_dir = Path("vendor_kernel_a16")

    # 3a. Fetch live repo (or simulate)
    repo = fetch_vendor_repo(codename, clone_dir)
    if not repo:
        print("[WARN] Could not clone; using mock data for demo.")
        # Create minimal mock structure for demonstration
        repo = Path("mock_repo")
        repo.mkdir(exist_ok=True)
        (repo / "vendor/etc/init").mkdir(parents=True, exist_ok=True)
        (repo / "vendor/etc/init/hw_breathing.rc").touch()
        (repo / "vendor/lib64/hw").mkdir(parents=True, exist_ok=True)
        (repo / "vendor/lib64/hw/camera.exynos.so").touch()
        (repo / "arch/arm64/boot/dts/exynos").mkdir(parents=True, exist_ok=True)
        (repo / "arch/arm64/boot/dts/exynos/exynos850.dtsi").touch()

    # 3b. Generate the correct Makefile
    makefile_content = generate_dynamic_makefile(device, repo)
    makefile_path = Path("Makefile.live")
    makefile_path.write_text(makefile_content)
    print(f"[LIVE] Dynamic Makefile written to {makefile_path}")

    # 3c. Show that the pattern rule now works (dry-run)
    print("\n[LIVE] Dry-run of dynamic Makefile (first three targets):")
    try:
        result = subprocess.run(
            ["make", "-n", "-f", str(makefile_path), "all"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(result.stdout[:800])  # truncate for readability
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Make dry-run failed: {e.stderr}", file=sys.stderr)

    # 3d. Actually create the structure (optional)
    print("\n[LIVE] Creating live automation structure...")
    subprocess.run(["make", "-f", str(makefile_path), "all"], check=True)
    print("[LIVE] Structure created. Inspect 'automations/' for live docs.\n")

if __name__ == "__main__":
    main()