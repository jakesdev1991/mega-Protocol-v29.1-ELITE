#ifndef PULSE_PHASE_MANAGER_HPP
#define PULSE_PHASE_MANAGER_HPP

#include <cstdint>

struct PhaseParameters {
    double shock_limit;
    double spread_limit;
    double flow_enter;
    double cusum_h;
};

enum class PulsePhase : uint8_t { RAMP_UP, STEADY_STATE, RAMP_DOWN, POST_PULSE };

// Forward declaration of GovernorAggregator to allow apply_phase
template<size_t NumChannels, size_t VoteThreshold>
class GovernorAggregator;

class PulsePhaseManager {
    PhaseParameters ramp_up_cfg     = {0.85, 0.25, 0.20, 6.0};
    PhaseParameters steady_state_cfg = {0.70, 0.15, 0.15, 4.0};
    PhaseParameters ramp_down_cfg   = {0.80, 0.20, 0.18, 5.5};
public:
    PhaseParameters get_config_for_phase(PulsePhase phase) {
        switch (phase) {
            case PulsePhase::STEADY_STATE: return steady_state_cfg;
            case PulsePhase::RAMP_DOWN:    return ramp_down_cfg;
            default:                       return ramp_up_cfg;
        }
    }

    template<size_t N, size_t T>
    void apply_phase(PulsePhase phase, GovernorAggregator<N, T>& aggregator) {
        aggregator.apply_thresholds(get_config_for_phase(phase));
    }
};

#endif
