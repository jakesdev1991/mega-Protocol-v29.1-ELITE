#ifndef OMEGAPROTOCOL_V15_FULL_HPP
#define OMEGAPROTOCOL_V15_FULL_HPP

#include "Pulse_Phase_Manager.hpp"
#include "Governor.hpp"
#include "Multi-Channel_Aggregator.hpp"
#include "Phase_Arbiter.hpp"
#include "Telemetry_Black-Box.hpp"
#include "Omega_System_Executive.hpp"

namespace Omega {
    using ::PulsePhase;
    using ::PulsePhaseManager;
    using ::PhaseParameters;
    using ::FastRing;
    using ::InertialSubstrate;
    using ::OmegaGovernor;
    using ::GovernorPayload;
    using ::SystemMode;
    using ::FaultBit;
    using ::GovernorAggregator;
    using ::ReactorVitals;
    using ::PhaseArbiter;
    using ::TelemetryRecorder;
    using ::OmegaSystem;

    // Enums values
    using ::FAULT_NONE;
    using ::FAULT_NAN_INF;
    using ::FAULT_CLIPPING;
    using ::FAULT_SLEW;
    using ::FAULT_FLATLINE;
    using ::FAULT_WATCHDOG;

    namespace Config = ::Config;
}

#endif
