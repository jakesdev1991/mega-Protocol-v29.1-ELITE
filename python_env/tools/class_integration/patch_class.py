# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import os
import sys

def patch_file(file_path, search_pattern, patch_content, mode='after'):
    if not os.path.exists(file_path):
        return False
        
    with open(file_path, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    found = False
    for line in lines:
        new_lines.append(line)
        if search_pattern in line and not found:
            if mode == 'after':
                new_lines.append("\n" + patch_content + "\n")
            found = True
            
    if found:
        with open(file_path, 'w') as f:
            f.writelines(new_lines)
        return True
    return False

def main():
    class_root = sys.argv[1] if len(sys.argv) > 1 else "./class"
    
    print(f"🚀 Patching CLASS (v26.6 Rescaled) at {class_root}...")
    
    # 1. Background evolution
    bg_path = os.path.join(class_root, "source", "background.c")
    bg_patch = """
    /* Omega Protocol v26.6: Canonical Asymmetry Field rho and p */
    double rho_omega = 0.5 * pba->phidot_omega * pba->phidot_omega + pba->lambda_omega * pow(pba->phi_omega, 4);
    double p_omega = 0.5 * pba->phidot_omega * pba->phidot_omega - pba->lambda_omega * pow(pba->phi_omega, 4);
    pba->rho_omega = rho_omega;
    pba->p_omega = p_omega;
    """
    if patch_file(bg_path, "rho_tot += pba->rho_sc;", bg_patch):
        print("✅ background.c patched.")
    
    # 2. Perturbation evolution
    pert_path = os.path.join(class_root, "source", "perturbations.c")
    pert_patch = """
    /* Omega Protocol v26.6: Canonical delta_phi evolution */
    double v_pp_omega = 12.0 * pba->lambda_omega * pba->phi_omega * pba->phi_omega;
    delta_phiddot = -3.0 * pba->H * delta_phidot - (pow(k/pba->a, 2) + v_pp_omega) * delta_phi;
    """
    if patch_file(pert_path, "/* evolve scalar field perturbations */", pert_patch):
        print("✅ perturbations.c patched.")

if __name__ == "__main__":
    main()
