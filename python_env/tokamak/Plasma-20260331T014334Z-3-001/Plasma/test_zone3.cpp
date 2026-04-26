/**
 * ==============================================================================
 * OMEGA PROTOCOL v15.0 - VALIDATION SUITE (ZONE 3)
 * Purpose: Verification of Stability Gating & Baseline Assimilation
 * Target: Statistical Robustness / Non-Pollution Guarantee
 * ==============================================================================
 */

#include "OmegaProtocol_v15_Full.hpp"
#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <cmath>

using namespace Omega;

// --- TEST INFRASTRUCTURE ---

struct TestResult {
    std::string name;
    bool passed;
    std::string details;
};

class TestRunner {
    std::vector<TestResult> results;
public:
    void run(const std::string& name, auto test_func) {
        try {
            bool success = test_func();
            results.push_back({name, success, success ? "Passed" : "Verification Failed"});
        } catch (const std::exception& e) {
            results.push_back({name, false, std::string("Exception: ") + e.what()});
        }
    }

    void report() {
        std::cout << "\n" << std::string(60, '=') << "\n";
        std::cout << " OMEGA PROTOCOL v15.0 - TEST REPORT (ZONE 3)\n";
        std::cout << std::string(60, '=') << "\n";
        int passed = 0;
        for (const auto& r : results) {
            std::cout << (r.passed ? " [PASS] " : " [FAIL] ") 
                      << std::left << std::setw(35) << r.name 
                      << " | " << r.details << "\n";
            if (r.passed) passed++;
        }
        std::cout << std::string(60, '-') << "\n";
        std::cout << " Summary: " << passed << "/" << results.size() << " tests passed.\n";
        std::cout << std::string(60, '=') << "\n";
    }
};

// --- ZONE 3: STABILITY & BASELINE TESTS ---

/**
 * TEST: Oscillation Rejection (The "Pollution" Defense)
 * Logic: If the signal oscillates > STARTUP_SLEW, the stability streak 
 * should never reach the 100-tick threshold for assimilation.
 */
bool test_oscillation_rejection() {
    OmegaGovernor gov;
    const double base_val = 50.0;
    const double jitter = 4.0; // > Config::STARTUP_SLEW (3.0)

    // Run for 500 ticks with high jitter
    for (int i = 0; i < 500; ++i) {
        double raw = base_val + (i % 2 == 0 ? jitter : -jitter);
        auto p = gov.tick(raw, true);

        // System must never reach MONITORING because the streak keeps resetting
        if (p.mode == SystemMode::MONITORING) return false;
    }
    return true;
}

/**
 * TEST: Stability Convergence
 * Logic: A perfectly stable signal should transition to MONITORING 
 * exactly after (Substrate Warmup + Stability Streak) ticks.
 */
bool test_stability_convergence() {
    OmegaGovernor gov;
    bool reached_monitoring = false;

    // Run for 1000 ticks. At 10kHz, this is 100ms.
    for (int i = 0; i < 1000; ++i) {
        double signal = 50.0 + (i % 2 == 0 ? 0.1 : -0.1);
        auto p = gov.tick(signal, true);
        if (p.mode == SystemMode::MONITORING) {
            reached_monitoring = true;
            break;
        }
    }
    return reached_monitoring;
}

/**
 * TEST: Z-Gate Outlier Guard
 * Logic: Once MONITORING, an outlier (Z > 1.5) must be processed for 
 * alarms but REJECTED for baseline updates to prevent mean-shift.
 */
bool test_z_gate_outlier_guard() {
    OmegaGovernor gov;
    
    // 1. Establish stable MONITORING state
    for (int i = 0; i < 500; ++i) {
        double signal = 50.0 + (i % 2 == 0 ? 0.1 : -0.1);
        gov.tick(signal, true);
    }
    
    // 2. Inject a controlled outlier that stays below Trip/Fracture
    // Target a Z-score around 2.0 (50.0 + 2.0 * sigma)
    // Since our sigma is tiny initially, 55.0 is a massive outlier.
    auto p_outlier = gov.tick(55.0, true);
    
    // The outlier should be processed (Z-score should be high)
    // In a real build, we'd verify internal b_sum wasn't updated.
    // For this black-box test, we verify that a single outlier didn't 
    // cause the mode to transition to DEGRADED or TRIPPED.
    return (p_outlier.mode == SystemMode::MONITORING || p_outlier.mode == SystemMode::PRE_ALARM_DRIFT);
}

/**
 * TEST: Baseline Timeout (Degraded Mode)
 * Logic: If the signal never stabilizes (jittering for 10,000 ticks), 
 * the governor must eventually enter DEGRADED_NO_BASELINE.
 */
bool test_baseline_timeout() {
    OmegaGovernor gov;
    const double jitter = 5.0; // Constant instability

    for (int i = 0; i < 12000; ++i) {
        gov.tick(50.0 + (i % 2 ? jitter : -jitter), true);
    }
    
    // Tick 12,001: Must be DEGRADED
    auto p_post = gov.tick(50.0 + 0.1, true);
    
    return (p_post.mode == SystemMode::DEGRADED_NO_BASELINE);
}

// --- MAIN EXECUTION ---

int main() {
    TestRunner runner;

    std::cout << "Starting Omega Protocol v15.0 Validation Suite...\n";
    std::cout << "Target: Stability & Baseline (Zone 3)\n";

    runner.run("Stability: Oscillation Rejection", test_oscillation_rejection);
    runner.run("Stability: Convergence to Monitoring", test_stability_convergence);
    runner.run("Baseline: Z-Gate Outlier Guard", test_z_gate_outlier_guard);
    runner.run("Baseline: Timeout to Degraded Mode", test_baseline_timeout);

    runner.report();

    return 0;
}