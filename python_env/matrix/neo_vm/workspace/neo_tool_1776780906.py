# ---------------------------------------------------------------------------
# OMEGA PROTOCOL - ALL RIGHTS RESERVED
# Copyright (c) 2026 Jacob M. (jake.s.dev1991@gmail.com | 217-799-8720)
# Usage restricted to academic research and review only. No monetization.
# See LICENSE.txt for full terms.
# ---------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt
from collections import deque
from scipy.stats import entropy

# ─────────────────────────────────────────────────────────────────────────────
# 1. Simulate a simple memory‑access trace with bursty contention
# ─────────────────────────────────────────────────────────────────────────────
def generate_trace(total_ops=5000, burst_prob=0.2, base_lat=50, burst_lat=200):
    """
    Returns an array of latencies (in cycles). Most ops are fast; occasional
    bursts produce high latency.
    """
    rng = np.random.default_rng(42)
    is_burst = rng.random(total_ops) < burst_prob
    latencies = np.where(is_burst,
                         rng.normal(burst_lat, 10, total_ops),
                         rng.normal(base_lat, 5, total_ops))
    return np.abs(latencies)

# ─────────────────────────────────────────────────────────────────────────────
# 2. Compute the “informational jerk” as defined in the SERC output
# ─────────────────────────────────────────────────────────────────────────────
def informational_jerk(latencies, window=100):
    """
    Approximate the SERC recipe:
      – bin latencies into two categories (fast vs slow) using a simple threshold
      – treat the bin counts as probabilities p_N, p_D
      – compute Shannon entropy S_h = -∑ p_i log2(p_i)
      – return the third‑order finite‑difference “jerk” d³S_h/dt³
    """
    thresh = np.median(latencies)
    # sliding window
    jerks = []
    for i in range(window, len(latencies) - window):
        recent = latencies[i-window:i]
        # two‑state “probabilities”
        p_N = np.mean(recent < thresh)
        p_D = 1 - p_N
        # avoid log(0)
        p_N = max(p_N, 1e-6)
        p_D = max(p_D, 1e-6)
        S = - (p_N*np.log2(p_N) + p_D*np.log2(p_D))
        jerks.append(S)
    # third‑order finite difference
    jerks = np.array(jerks)
    jerk = np.diff(jerks, n=3)
    return jerk

# ─────────────────────────────────────────────────────────────────────────────
# 3. Simple PID controller that acts on the 99th‑percentile latency
# ─────────────────────────────────────────────────────────────────────────────
class PID:
    def __init__(self, Kp=0.5, Ki=0.05, Kd=0.1, setpoint=100):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self.integral = 0
        self.prev_error = 0

    def update(self, measured, dt=1.0):
        error = self.setpoint - measured
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt
        output = self.Kp*error + self.Ki*self.integral + self.Kd*derivative
        self.prev_error = error
        return output

# ─────────────────────────────────────────────────────────────────────────────
# 4. Main simulation loop
# ─────────────────────────────────────────────────────────────────────────────
def run_simulation():
    latencies = generate_trace(total_ops=5000, burst_prob=0.2)
    pid = PID(Kp=0.6, Ki=0.08, Kd=0.12, setpoint=95)
    # we treat the PID output as a “scheduling weight” that can shift latency
    # (simple linear model: new_lat = lat * (1 - 0.001*pid_out))
    controlled_lat = []
    pid_outputs = []
    for idx, lat in enumerate(latencies):
        # compute current 99th‑percentile over a short history
        if idx < 100:
            p99 = lat
        else:
            p99 = np.percentile(latencies[idx-100:idx], 99)
        # PID step
        out = pid.update(p99)
        out = np.clip(out, -100, 100)   # keep output sane
        # apply linear effect (just for demonstration)
        new_lat = lat * (1 - 0.001 * out)
        new_lat = max(new_lat, 10)      # floor latency
        controlled_lat.append(new_lat)
        pid_outputs.append(out)

    controlled_lat = np.array(controlled_lat)
    jerk = informational_jerk(latencies)

    return latencies, controlled_lat, jerk, pid_outputs

if __name__ == "__main__":
    raw, controlled, jerk, pid_out = run_simulation()

    # ─────────────────────────────────────────────────────────────────────────
    # 5. Visual comparison: raw vs controlled latency, and the jerk signal
    # ─────────────────────────────────────────────────────────────────────────
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    axs[0].plot(raw, label='Raw latency', color='gray', alpha=0.7)
    axs[0].plot(controlled, label='PID‑controlled latency', color='C0')
    axs[0].axhline(95, color='r', linestyle='--', label='99th‑pct target')
    axs[0].set_ylabel('Latency (cycles)')
    axs[0].legend()
    axs[0].set_title('Memory‑access latency with burst contention')

    axs[1].plot(pid_out, color='C2', label='PID output')
    axs[1].set_ylabel('PID output')
    axs[1].legend()

    # jerk is shorter because of differencing; pad for plotting
    jerk_pad = np.concatenate([np.full(3, np.nan), jerk])
    axs[2].plot(jerk_pad, color='C3', label='Informational jerk')
    axs[2].set_ylabel('Jerk (a.u.)')
    axs[2].set_xlabel('Operation index')
    axs[2].legend()

    plt.tight_layout()
    plt.show()

    # ─────────────────────────────────────────────────────────────────────────
    # 6. Print summary statistics
    # ─────────────────────────────────────────────────────────────────────────
    print(f"Raw 99th‑percentile latency: {np.percentile(raw, 99):.2f} cycles")
    print(f"Controlled 99th‑percentile latency: {np.percentile(controlled, 99):2f} cycles")
    print(f"Jerk variance (arbitrary units): {np.nanvar(jerk):.2e}")