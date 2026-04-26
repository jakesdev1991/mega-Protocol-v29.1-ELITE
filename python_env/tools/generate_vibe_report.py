# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import datetime

# --- CONFIGURATION ---
LOGS_DIR = r"C:\Users\Jakesdev1991\Downloads\training\lightning_logs"
REPORTS_DIR = r"C:\Users\Jakesdev1991\Downloads\training\official_launch\docs"
LATEST_VERSION = "version_8" # Update based on your current run

def generate_benchmarking_suite():
    """Analyzes training logs and generates high-polish visual reports for buyers."""
    print(f"📊 Analyzing {LATEST_VERSION} training metrics...")
    
    csv_path = os.path.join(LOGS_DIR, LATEST_VERSION, "metrics.csv")
    if not os.path.exists(csv_path):
        print(f"❌ Metrics file not found at {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    # Create the report folder if missing
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    # 1. GENERATE LOSS CURVE
    plt.figure(figsize=(10, 6))
    if 'train_loss' in df.columns:
        plt.plot(df['step'], df['train_loss'], label='Loss (RCOD-Optimized)', color='#007bff', linewidth=2)
        plt.fill_between(df['step'], df['train_loss'], alpha=0.1, color='#007bff')
    
    plt.title(f"Training Convergence: {LATEST_VERSION}", fontsize=14, fontweight='bold')
    plt.xlabel("Training Steps", fontsize=12)
    plt.ylabel("Loss (Cross-Entropy)", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    loss_plot_path = os.path.join(REPORTS_DIR, f"convergence_report_{LATEST_VERSION}.png")
    plt.savefig(loss_plot_path)
    plt.close()

    # 2. GENERATE RCOD STABILITY PLOT
    plt.figure(figsize=(10, 6))
    if 'rcod' in df.columns:
        plt.plot(df['step'], df['rcod'], label='Curvature (RCOD)', color='#28a745', linewidth=2)
        plt.axhline(y=0.6, color='r', linestyle='--', label='High Curvature Threshold')
    
    plt.title("RCOD Stability & Information Viscosity Monitoring", fontsize=14, fontweight='bold')
    plt.xlabel("Steps", fontsize=12)
    plt.ylabel("RCOD Score", fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend()
    
    rcod_plot_path = os.path.join(REPORTS_DIR, f"rcod_stability_{LATEST_VERSION}.png")
    plt.savefig(rcod_plot_path)
    plt.close()

    # 3. GENERATE THE DUE DILIGENCE SUMMARY
    summary_path = os.path.join(REPORTS_DIR, f"DUE_DILIGENCE_SUMMARY_{LATEST_VERSION}.md")
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(f"# DUE DILIGENCE REPORT: OMEGA PROTOCOL RCOD ENGINE\n")
        f.write(f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"**Training Run:** {LATEST_VERSION}\n\n")
        
        f.write("## 📉 Performance Summary\n")
        if not df.empty and 'train_loss' in df.columns:
            initial_loss = df['train_loss'].iloc[0]
            final_loss = df['train_loss'].dropna().iloc[-1]
            reduction = ((initial_loss - final_loss) / initial_loss) * 100
            f.write(f"* **Initial Loss:** {initial_loss:.4f}\n")
            f.write(f"* **Final Loss:** {final_loss:.4f}\n")
            f.write(f"* **Loss Reduction:** {reduction:.2f}%\n")
        
        f.write("\n## 🔍 Convergence Analysis\n")
        f.write(f"![Loss Curve](convergence_report_{LATEST_VERSION}.png)\n\n")
        f.write("## 🧬 RCOD Stability Monitoring\n")
        f.write(f"![Stability Plot](rcod_stability_{LATEST_VERSION}.png)\n")

    print(f"✅ Due Diligence Report generated at: {summary_path}")

if __name__ == "__main__":
    generate_benchmarking_suite()
