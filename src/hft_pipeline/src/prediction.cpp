#include "omega/hft/prediction.hpp"

#include <algorithm>

namespace omega::hft {

float predict_reserve(float current, float delta_per_ms, float latency_ms) noexcept {
    return std::max(current + (delta_per_ms * latency_ms), 1.0e-8F);
}

void apply_prediction(Route& route, const MarketUpdate& market, const PredictionContext& ctx) noexcept {
    const float predicted_in = predict_reserve(route.reserve_in[0], market.delta_reserve_in, ctx.latency_ms);
    const float predicted_out = predict_reserve(route.reserve_out[0], market.delta_reserve_out, ctx.latency_ms);
    const float net_in = route.input_size * (1.0F - route.fee[0]);
    const float out = (predicted_out * net_in) / (predicted_in + net_in);
    route.predicted_profit = out - route.input_size - ctx.priority_fee;
}

float heuristic_survivability(const Route& route, float latency_ms, float slot_progress) noexcept {
    const float latency_penalty = 1.0F + (latency_ms / 400.0F);
    const float slot_penalty = 1.0F + std::clamp(slot_progress, 0.0F, 1.0F);
    const float liquidity = std::max(route.liquidity_score, 0.0F);
    const float volatility = std::max(route.volatility_score, 0.0F);
    const float score = liquidity / ((1.0F + volatility) * latency_penalty * slot_penalty);
    return std::clamp(score, 0.0F, 1.0F);
}

ExecutionDecision decide(const Route& route, const PredictionContext& ctx) noexcept {
    const float edge_score = route.predicted_profit * route.survivability;
    return ExecutionDecision{
        route.id,
        route.expected_profit,
        route.predicted_profit,
        route.survivability,
        edge_score > ctx.min_edge_score && route.cu_cost < ctx.max_cu_cost,
    };
}

} // namespace omega::hft
