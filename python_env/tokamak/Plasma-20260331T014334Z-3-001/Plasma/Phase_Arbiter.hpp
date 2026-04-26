#ifndef PHASE_ARBITER_HPP
#define PHASE_ARBITER_HPP

#include "Pulse_Phase_Manager.hpp"

struct ReactorVitals {
    double plasma_current_ma; 
    double loop_voltage;      
    bool equilibrium_locked;  
};

class PhaseArbiter {
    PulsePhase internal_phase = PulsePhase::RAMP_UP;
public:
    PulsePhase determine_phase(const ReactorVitals& vitals) {
        if (internal_phase == PulsePhase::RAMP_UP && vitals.plasma_current_ma > 1.2) {
            internal_phase = PulsePhase::STEADY_STATE;
        } 
        else if (internal_phase == PulsePhase::STEADY_STATE && vitals.plasma_current_ma < 0.8) {
            internal_phase = PulsePhase::RAMP_DOWN;
        }
        return internal_phase;
    }
    PulsePhase get_phase() const { return internal_phase; }
};

#endif