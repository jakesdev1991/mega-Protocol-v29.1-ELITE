#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace omega::hft {

constexpr std::size_t kMaxHops = 4;
constexpr std::size_t kBatchSize = 4096;

struct alignas(64) Route {
    std::uint64_t id{};
    std::array<float, kMaxHops> reserve_in{};
    std::array<float, kMaxHops> reserve_out{};
    std::array<float, kMaxHops> fee{};
    float input_size{};

    float liquidity_score{};
    float volatility_score{};
    float cu_cost{};

    float expected_profit{};
    float predicted_profit{};
    float survivability{};

    std::uint8_t hops{};
};

static_assert(alignof(Route) == 64, "Route must remain cache-line aligned");

struct RouteBatch {
    std::array<Route, kBatchSize> routes{};
    std::size_t count{};
};

struct MarketUpdate {
    std::uint64_t slot{};
    std::uint64_t account_hash{};
    float reserve_in{};
    float reserve_out{};
    float delta_reserve_in{};
    float delta_reserve_out{};
    float slot_progress{};
};

struct PredictionContext {
    float latency_ms{200.0F};
    float priority_fee{0.0001F};
    float min_edge_score{0.0005F};
    float max_cu_cost{1'400'000.0F};
};

struct ExecutionDecision {
    std::uint64_t route_id{};
    float expected_profit{};
    float predicted_profit{};
    float survivability{};
    bool execute{};
};

} // namespace omega::hft
