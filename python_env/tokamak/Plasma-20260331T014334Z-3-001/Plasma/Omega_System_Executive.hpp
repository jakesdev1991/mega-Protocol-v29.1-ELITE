#ifndef OMEGA_SYSTEM_EXECUTIVE_HPP
#define OMEGA_SYSTEM_EXECUTIVE_HPP

#include "Governor.hpp"
#include "Multi-Channel_Aggregator.hpp"
#include "Phase_Arbiter.hpp"
#include "Pulse_Phase_Manager.hpp"
#include "Telemetry_Black-Box.hpp"

class OmegaSystem {
    GovernorAggregator<8, 3> aggregator;
    TelemetryRecorder<8> recorder;
    PulsePhaseManager phase_manager;
    PhaseArbiter arbiter;
    PulsePhase current_phase = PulsePhase::RAMP_UP;
public:
    typename GovernorAggregator<8, 3>::GlobalStatus 
    run_cycle(const std::array<double, 8>& sensor_data, const ReactorVitals& vitals, bool watchdog_ok = true) {
        PulsePhase active_phase = arbiter.determine_phase(vitals);
        if (active_phase != current_phase) {
            current_phase = active_phase;
            aggregator.apply_thresholds(phase_manager.get_config_for_phase(current_phase));
        }
        auto status = aggregator.tick(sensor_data, watchdog_ok);
        recorder.record(status, aggregator.get_governors());
        return status;
    }
    void reset() { aggregator.reset_all(); current_phase = PulsePhase::RAMP_UP; }
    PulsePhase get_phase() const { return current_phase; }
};

#endif