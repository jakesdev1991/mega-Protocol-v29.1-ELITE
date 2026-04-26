/**
 * ==============================================================================
 * OMEGA PROTOCOL v15.0 - VALIDATION SUITE (ZONE 1 & ZONE 2)
 * Purpose: Verification of Mathematical Invariants & Integrity Guards
 * Target: Hardened Specification / RTOS Compliance
 * ==============================================================================
 */

#include "OmegaProtocol_v15_Full.hpp"
#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <limits>

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
        std::cout << " OMEGA PROTOCOL v15.0 - TEST REPORT (ZONE 1 & 2)\n";
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

// --- ZONE 1: UNIT & INVARIANT TESTS (The Foundation) ---

bool test_fast_ring_masking() {
    // Verifies power-of-2 wrapping without using modulo operator
    FastRing<int, 8> ring;
    for (int i = 0; i < 20; ++i) ring.push(i);
    
    // Size should be 8 (capacity), not 20
    if (ring.size() != 8) return false;
    
    // Oldest should be 12, newest should be 19
    if (ring.get_from_oldest(0) != 12) return false;
    if (ring.get_from_oldest(7) != 19) return false;
    
    return true;
}

bool test_rcod_ontological_bounds() {
    InertialSubstrate substrate;
    double rcod, spread;

    // Test Case A: Perfect Convergence (RCOD must be 0)
    for(int i=0; i<64; ++i) {
        double raw = 50.0 + (i % 2 == 0 ? 0.03 : -0.03);
        substrate.process(raw, rcod, spread);
    }
    if (rcod > 0.001) return false;

    // Test Case B: Maximum Divergence (RCOD must approach 1.0)
    // We simulate a violent fracture by alternating extremes
    for(int i=0; i<64; ++i) {
        substrate.process((i % 2 == 0) ? 90.0 : 10.0, rcod, spread);
    }
    
    // RCOD is 1 - (max_cluster / 10). With 10 nodes diverging, 
    // max_cluster should drop significantly.
    if (rcod < 0.5) return false; 
    if (rcod > 1.0) return false; // Hard ontological invariant

    return true;
}

// --- ZONE 2: INTEGRITY & FAULT TESTS (The Immune System) ---

bool test_poison_signal_rejection() {
    OmegaGovernor gov;
    
    // 1. NaN Injection
    auto p1 = gov.tick(std::numeric_limits<double>::quiet_NaN(), true);
    if (!(p1.fault_mask & FAULT_NAN_INF)) return false;
    if (p1.mode != SystemMode::HARDWARE_FAULT) return false;

    gov.reset();

    // 2. Clipping Injection
    auto p2 = gov.tick(Config::SIGNAL_MAX + 10.0, true);
    if (!(p2.fault_mask & FAULT_CLIPPING)) return false;

    return true;
}

bool test_flatline_detector() {
    OmegaGovernor gov;
    GovernorPayload p;

    // Feed a perfectly static signal for the entire window
    for (size_t i = 0; i < Config::FLATLINE_WIN + 1; ++i) {
        p = gov.tick(50.0, true);
    }

    // Must detect lack of thermal dither
    return (p.fault_mask & FAULT_FLATLINE);
}

bool test_slew_limit_interlock() {
    OmegaGovernor gov;
    gov.tick(50.0, true); // Establish baseline pos

    // Jump 60 units (Limit is 50 for sensor)
    auto p = gov.tick(110.0, true);
    
    return (p.fault_mask & FAULT_SLEW);
}

bool test_watchdog_failure() {
    OmegaGovernor gov;
    auto p = gov.tick(50.0, false); // Watchdog reports NOT OK
    
    return (p.fault_mask & FAULT_WATCHDOG) && (p.mode == SystemMode::HARDWARE_FAULT);
}

// --- MAIN EXECUTION ---

int main() {
    TestRunner runner;

    std::cout << "Starting Omega Protocol v15.0 Validation Suite...\n";
    std::cout << "Target: Invariants (Zone 1) & Integrity (Zone 2)\n";

    // Zone 1
    runner.run("Invariant: FastRing Masking", test_fast_ring_masking);
    runner.run("Invariant: RCOD Ontological Bounds", test_rcod_ontological_bounds);

    // Zone 2
    runner.run("Fault: Poison Signal Rejection", test_poison_signal_rejection);
    runner.run("Fault: Flatline Detection", test_flatline_detector);
    runner.run("Fault: Sensor Slew Interlock", test_slew_limit_interlock);
    runner.run("Fault: Watchdog Failure Logic", test_watchdog_failure);

    runner.report();

    return 0;
}