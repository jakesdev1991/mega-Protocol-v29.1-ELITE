#pragma once

#include "omega/hft/types.hpp"

namespace omega::hft {

void evaluate_batch(RouteBatch& batch, float priority_fee) noexcept;
float evaluate_single_hop(float reserve_in, float reserve_out, float fee, float input, float priority_fee) noexcept;

} // namespace omega::hft
