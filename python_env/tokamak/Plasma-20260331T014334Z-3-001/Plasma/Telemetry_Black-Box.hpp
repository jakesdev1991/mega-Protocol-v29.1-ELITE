#ifndef TELEMETRY_BLACK_BOX_HPP
#define TELEMETRY_BLACK_BOX_HPP

#include "Multi-Channel_Aggregator.hpp"

namespace TelemetryConfig { constexpr size_t RECORDING_WINDOW = 1024; }

struct ChannelSnapshot { float rcod, z_score; SystemMode mode; };

template<size_t NumChannels>
struct GlobalSnapshot {
    uint32_t tick_id;
    std::array<ChannelSnapshot, NumChannels> channels;
    bool global_trip;
    uint16_t trip_bitmask;
};

template<size_t NumChannels, size_t VoteThreshold = 3>
class TelemetryRecorder {
    std::array<GlobalSnapshot<NumChannels>, TelemetryConfig::RECORDING_WINDOW> buffer;
    size_t head = 0; uint32_t total_ticks = 0;
public:
    void record(const typename GovernorAggregator<NumChannels, VoteThreshold>::GlobalStatus& status,
                const std::array<OmegaGovernor, NumChannels>& governors) {
        GlobalSnapshot<NumChannels>& frame = buffer[head];
        frame.tick_id = total_ticks++;
        frame.global_trip = status.global_trip_actuated;
        frame.trip_bitmask = status.trip_bitmask;
        for (size_t i = 0; i < NumChannels; ++i) {
            frame.channels[i].rcod = (float)governors[i].get_rcod();
            frame.channels[i].z_score = (float)governors[i].get_z();
            frame.channels[i].mode = governors[i].get_mode();
        }
        head = (head + 1) % TelemetryConfig::RECORDING_WINDOW;
    }

    void record(const typename GovernorAggregator<NumChannels, VoteThreshold>::GlobalStatus& status,
                const GovernorAggregator<NumChannels, VoteThreshold>& aggregator) {
        record(status, aggregator.get_governors());
    }
};

#endif
