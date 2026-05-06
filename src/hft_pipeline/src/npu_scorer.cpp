#include "omega/hft/npu_scorer.hpp"

#include <algorithm>
#include <cmath>

namespace omega::hft {

bool NpuScorer::load(const std::filesystem::path& compiled_model_path) {
    if (compiled_model_path.empty() || !std::filesystem::exists(compiled_model_path)) {
        available_ = false;
        backend_ = "heuristic-fallback";
        return false;
    }

    available_ = true;
    backend_ = "xdna-compiled-model-placeholder";
    return true;
}

float NpuScorer::score(const FeatureVector& features) const noexcept {
    const float predicted_profit = features.values[0];
    const float liquidity = std::max(features.values[1], 0.0F);
    const float volatility = std::max(features.values[2], 0.0F);
    const float cu_cost = std::max(features.values[3], 0.0F);
    const float latency_ms = std::max(features.values[4], 0.0F);
    const float slot_progress = std::clamp(features.values[5], 0.0F, 1.0F);

    const float raw = (2.25F * predicted_profit) + (1.15F * liquidity) -
                      (1.35F * volatility) - (cu_cost / 1'400'000.0F) -
                      (latency_ms / 400.0F) - slot_progress;
    return std::clamp(1.0F / (1.0F + std::exp(-raw)), 0.0F, 1.0F);
}

FeatureVector make_features(const Route& route, float latency_ms, float slot_progress) noexcept {
    return FeatureVector{{
        route.predicted_profit,
        route.liquidity_score,
        route.volatility_score,
        route.cu_cost,
        latency_ms,
        slot_progress,
    }};
}

} // namespace omega::hft
