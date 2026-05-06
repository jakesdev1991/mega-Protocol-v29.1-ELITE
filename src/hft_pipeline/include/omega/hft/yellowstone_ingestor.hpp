#pragma once

#include "omega/hft/ring_buffer.hpp"
#include "omega/hft/types.hpp"

#include <cstdint>
#include <span>

namespace omega::hft {

class YellowstoneIngestor {
public:
    explicit YellowstoneIngestor(SpscRingBuffer<MarketUpdate, 1024>& output) noexcept;

    bool ingest_account_update(std::uint64_t slot,
                               std::uint64_t account_hash,
                               std::span<const std::uint8_t> account_data,
                               float slot_progress) noexcept;

private:
    SpscRingBuffer<MarketUpdate, 1024>& output_;
};

} // namespace omega::hft
