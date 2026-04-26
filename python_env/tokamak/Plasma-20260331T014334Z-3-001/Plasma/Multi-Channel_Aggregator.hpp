#ifndef MULTI_CHANNEL_AGGREGATOR_HPP
#define MULTI_CHANNEL_AGGREGATOR_HPP

#include "Governor.hpp"

template<size_t NumChannels, size_t VoteThreshold>
class GovernorAggregator {
    std::array<OmegaGovernor, NumChannels> governors;
public:
    struct GlobalStatus {
        SystemMode aggregate_mode = SystemMode::INIT;
        bool global_trip_actuated = false;
        bool any_supervisory_warning = false;
        uint16_t trip_bitmask = 0, fault_bitmask = 0;
    };

    void apply_thresholds(const PhaseParameters& params) {
        for (auto& gov : governors) gov.update_thresholds(params);
    }

    const std::array<OmegaGovernor, NumChannels>& get_governors() const { return governors; }

    GlobalStatus tick(const std::array<double, NumChannels>& signals, bool watchdog_ok) {
        GlobalStatus status; int trip_votes = 0, fault_count = 0;
        for (size_t i = 0; i < NumChannels; ++i) {
            auto payload = governors[i].tick(signals[i], watchdog_ok);
            if (payload.fast_trip_actuation) { status.trip_bitmask |= (1 << i); trip_votes++; }
            if (payload.mode == SystemMode::HARDWARE_FAULT) { status.fault_bitmask |= (1 << i); fault_count++; }
            if (payload.supervisory_warning) status.any_supervisory_warning = true;
        }
        if (trip_votes >= VoteThreshold) { status.global_trip_actuated = true; status.aggregate_mode = SystemMode::TRIPPED; } 
        else if (fault_count == NumChannels) status.aggregate_mode = SystemMode::HARDWARE_FAULT;
        else if (status.any_supervisory_warning) status.aggregate_mode = SystemMode::ALARM_FRACTURE;
        else status.aggregate_mode = SystemMode::MONITORING;
        return status;
    }

    void reset_all() { for (auto& g : governors) g.reset(); }
};

#endif
