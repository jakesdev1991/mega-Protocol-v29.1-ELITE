#pragma once

#include "omega/hft/types.hpp"

namespace omega::hft {

float predict_reserve(float current, float delta_per_ms, float latency_ms) noexcept;
void apply_prediction(Route& route, const MarketUpdate& market, const PredictionContext& ctx) noexcept;
float heuristic_survivability(const Route& route, float latency_ms, float slot_progress) noexcept;
ExecutionDecision decide(const Route& route, const PredictionContext& ctx) noexcept;

} // namespace omega::hft
