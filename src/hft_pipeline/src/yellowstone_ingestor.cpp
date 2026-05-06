#include "omega/hft/yellowstone_ingestor.hpp"

#include <cstring>

namespace omega::hft {
namespace {

struct PoolWireView {
    float reserve_in;
    float reserve_out;
    float delta_reserve_in;
    float delta_reserve_out;
};

} // namespace

YellowstoneIngestor::YellowstoneIngestor(SpscRingBuffer<MarketUpdate, 1024>& output) noexcept
    : output_(output) {}

bool YellowstoneIngestor::ingest_account_update(std::uint64_t slot,
                                                std::uint64_t account_hash,
                                                std::span<const std::uint8_t> account_data,
                                                float slot_progress) noexcept {
    if (account_data.size() < sizeof(PoolWireView)) {
        return false;
    }

    PoolWireView pool{};
    std::memcpy(&pool, account_data.data(), sizeof(PoolWireView));

    const MarketUpdate update{
        slot,
        account_hash,
        pool.reserve_in,
        pool.reserve_out,
        pool.delta_reserve_in,
        pool.delta_reserve_out,
        slot_progress,
    };
    return output_.push(update);
}

} // namespace omega::hft
