#include "omega/hft/avx_evaluator.hpp"

#if defined(__AVX512F__)
#include <immintrin.h>
#endif

#include <algorithm>
#include <array>

namespace omega::hft {
namespace {

constexpr float kEpsilon = 1.0e-8F;

#if defined(__AVX512F__)
inline __m512 fast_reciprocal(__m512 den) noexcept {
    const __m512 eps = _mm512_set1_ps(kEpsilon);
    den = _mm512_max_ps(den, eps);
    const __m512 rcp = _mm512_rcp14_ps(den);
    const __m512 two = _mm512_set1_ps(2.0F);
    return _mm512_mul_ps(rcp, _mm512_fnmadd_ps(den, rcp, two));
}
#endif

} // namespace

float evaluate_single_hop(float reserve_in, float reserve_out, float fee, float input, float priority_fee) noexcept {
    const float net_in = input * (1.0F - fee);
    const float den = std::max(reserve_in + net_in, kEpsilon);
    const float out = (reserve_out * net_in) / den;
    return out - input - priority_fee;
}

void evaluate_batch(RouteBatch& batch, float priority_fee) noexcept {
#if defined(__AVX512F__)
    alignas(64) std::array<float, 16> input{};
    alignas(64) std::array<float, 16> reserve_in{};
    alignas(64) std::array<float, 16> reserve_out{};
    alignas(64) std::array<float, 16> fee{};

    std::size_t i = 0;
    for (; i + 15 < batch.count; i += 16) {
        for (std::size_t lane = 0; lane < 16; ++lane) {
            const Route& route = batch.routes[i + lane];
            input[lane] = route.input_size;
            reserve_in[lane] = route.reserve_in[0];
            reserve_out[lane] = route.reserve_out[0];
            fee[lane] = route.fee[0];
        }

        const __m512 v_in = _mm512_load_ps(input.data());
        const __m512 v_x = _mm512_load_ps(reserve_in.data());
        const __m512 v_y = _mm512_load_ps(reserve_out.data());
        const __m512 v_fee = _mm512_load_ps(fee.data());
        const __m512 one = _mm512_set1_ps(1.0F);
        const __m512 v_net = _mm512_mul_ps(v_in, _mm512_sub_ps(one, v_fee));
        const __m512 v_num = _mm512_mul_ps(v_y, v_net);
        const __m512 v_den = _mm512_add_ps(v_x, v_net);
        const __m512 v_out = _mm512_mul_ps(v_num, fast_reciprocal(v_den));
        const __m512 v_profit = _mm512_sub_ps(_mm512_sub_ps(v_out, v_in), _mm512_set1_ps(priority_fee));

        alignas(64) std::array<float, 16> profit{};
        _mm512_store_ps(profit.data(), v_profit);
        for (std::size_t lane = 0; lane < 16; ++lane) {
            batch.routes[i + lane].expected_profit = profit[lane];
        }
    }
    for (; i < batch.count; ++i) {
        Route& route = batch.routes[i];
        route.expected_profit = evaluate_single_hop(route.reserve_in[0], route.reserve_out[0], route.fee[0], route.input_size, priority_fee);
    }
#else
    for (std::size_t i = 0; i < batch.count; ++i) {
        Route& route = batch.routes[i];
        route.expected_profit = evaluate_single_hop(route.reserve_in[0], route.reserve_out[0], route.fee[0], route.input_size, priority_fee);
    }
#endif
}

} // namespace omega::hft
