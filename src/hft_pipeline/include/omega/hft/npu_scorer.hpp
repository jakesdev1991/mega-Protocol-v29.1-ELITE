#pragma once

#include "omega/hft/types.hpp"

#include <array>
#include <filesystem>
#include <string>

namespace omega::hft {

struct FeatureVector {
    std::array<float, 6> values{};
};

class NpuScorer {
public:
    bool load(const std::filesystem::path& compiled_model_path);
    float score(const FeatureVector& features) const noexcept;
    bool available() const noexcept { return available_; }
    const std::string& backend() const noexcept { return backend_; }

private:
    bool available_{false};
    std::string backend_{"heuristic-fallback"};
};

FeatureVector make_features(const Route& route, float latency_ms, float slot_progress) noexcept;

} // namespace omega::hft
