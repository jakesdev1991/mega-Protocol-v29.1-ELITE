#include "omega/hft/avx_evaluator.hpp"
#include "omega/hft/npu_scorer.hpp"
#include "omega/hft/prediction.hpp"
#include "omega/hft/ring_buffer.hpp"
#include "omega/hft/yellowstone_ingestor.hpp"

#include <array>
#include <cstdint>
#include <cstring>
#include <iostream>

namespace {

struct DemoPoolWireView {
    float reserve_in;
    float reserve_out;
    float delta_reserve_in;
    float delta_reserve_out;
};

std::array<std::uint8_t, sizeof(DemoPoolWireView)> encode_pool(const DemoPoolWireView& pool) {
    std::array<std::uint8_t, sizeof(DemoPoolWireView)> bytes{};
    std::memcpy(bytes.data(), &pool, sizeof(pool));
    return bytes;
}

} // namespace

int main() {
    using namespace omega::hft;

    SpscRingBuffer<MarketUpdate, 1024> market_queue;
    YellowstoneIngestor ingestor(market_queue);

    const auto account_bytes = encode_pool(DemoPoolWireView{1'000.0F, 1'010.0F, 0.0002F, -0.0001F});
    if (!ingestor.ingest_account_update(42, 0xC0FFEE, account_bytes, 0.35F)) {
        std::cerr << "failed to ingest market update\n";
        return 1;
    }

    MarketUpdate market{};
    if (!market_queue.pop(market)) {
        std::cerr << "market queue unexpectedly empty\n";
        return 1;
    }

    RouteBatch batch{};
    batch.count = 2;
    batch.routes[0].id = 1001;
    batch.routes[0].reserve_in[0] = market.reserve_in;
    batch.routes[0].reserve_out[0] = market.reserve_out;
    batch.routes[0].fee[0] = 0.0025F;
    batch.routes[0].input_size = 1.0F;
    batch.routes[0].liquidity_score = 0.92F;
    batch.routes[0].volatility_score = 0.15F;
    batch.routes[0].cu_cost = 900'000.0F;
    batch.routes[0].hops = 2;

    batch.routes[1] = batch.routes[0];
    batch.routes[1].id = 1002;
    batch.routes[1].volatility_score = 1.75F;
    batch.routes[1].cu_cost = 1'550'000.0F;

    PredictionContext ctx{};
    evaluate_batch(batch, ctx.priority_fee);

    NpuScorer scorer;
    scorer.load({});

    for (std::size_t i = 0; i < batch.count; ++i) {
        Route& route = batch.routes[i];
        apply_prediction(route, market, ctx);
        route.survivability = scorer.score(make_features(route, ctx.latency_ms, market.slot_progress));
        const ExecutionDecision decision = decide(route, ctx);
        std::cout << "route=" << decision.route_id
                  << " expected=" << decision.expected_profit
                  << " predicted=" << decision.predicted_profit
                  << " survival=" << decision.survivability
                  << " execute=" << (decision.execute ? "yes" : "shadow") << '\n';
    }

    return 0;
}
