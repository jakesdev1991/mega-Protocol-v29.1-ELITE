#ifndef GOVERNOR_HPP
#define GOVERNOR_HPP

#include <iostream>
#include <cmath>
#include <array>
#include <cstdint>
#include <algorithm>
#include "Pulse_Phase_Manager.hpp"

namespace Config {
    constexpr double SIGNAL_MAX         = 100.0;
    constexpr double SIGNAL_MIN         = -100.0;
    constexpr double SENSOR_SLEW_LIMIT  = 50.0; 
    constexpr double PLASMA_SLEW_LIMIT  = 25.0; 
    constexpr double STARTUP_SLEW       = 3.0;
    constexpr size_t FLATLINE_WIN       = 256;   
    constexpr double LSB_NOISE_FLOOR    = 0.05; 
    constexpr size_t NUM_NODES          = 10;
    constexpr size_t NODE_DIM           = 32;    
    constexpr double QUANTIZE_SCALE     = 20.0;
    constexpr int    TOLERANCE_BANDS    = 1;    
    constexpr size_t BASELINE_WIN       = 128;   
    constexpr double CUSUM_K            = 0.5;  
    constexpr int    STABILITY_STREAK   = 10;   
    constexpr int    BASELINE_TIMEOUT   = 10000; 
    constexpr int    PERSISTENCE_ENTER  = 3;
}

enum class SystemMode : uint8_t {
    INIT = 0, WARMUP_SUBSTRATE, WARMUP_BASELINE, DEGRADED_NO_BASELINE, 
    MONITORING, PRE_ALARM_DRIFT, ALARM_FRACTURE, TRIPPED, HARDWARE_FAULT        
};

enum FaultBit : uint32_t {
    FAULT_NONE = 0, FAULT_NAN_INF = 1<<0, FAULT_CLIPPING = 1<<1, 
    FAULT_SLEW = 1<<2, FAULT_FLATLINE = 1<<3, FAULT_WATCHDOG = 1<<4
};

struct GovernorPayload {
    SystemMode mode = SystemMode::INIT;
    bool fast_trip_actuation = false;
    bool supervisory_warning = false;
    uint32_t fault_mask = 0; 
};

template<typename T, size_t Capacity>
class FastRing {
    std::array<T, Capacity> buffer{};
    size_t head = 0; size_t count = 0;
public:
    void push(T value) {
        buffer[head] = value;
        head = (head + 1) % Capacity;
        if (count < Capacity) count++;
    }
    T get_from_oldest(size_t idx) const { return buffer[((head + Capacity - count) + idx) % Capacity]; }
    size_t size() const { return count; }
    bool full() const { return count == Capacity; }
    void reset() { head = 0; count = 0; }
};

class InertialSubstrate {
    struct Node {
        FastRing<int, Config::NODE_DIM> ring;
        double alpha, state = 0.0; bool init = false;
        void encode(double raw) {
            state = !init ? raw : (alpha * raw) + ((1.0 - alpha) * state);
            init = true;
            ring.push(static_cast<int>(std::lround(state * Config::QUANTIZE_SCALE)));
        }
    };
    std::array<Node, Config::NUM_NODES> nodes;
public:
    InertialSubstrate() { for(size_t i=0; i<10; ++i) nodes[i].alpha = 1.0 - (i*0.07); }
    void process(double raw, double& rcod, double& spread) {
        for(auto& n : nodes) n.encode(raw);
        std::array<int, 10> slice;
        for(size_t i=0; i<10; ++i) slice[i] = nodes[i].ring.get_from_oldest(nodes[i].ring.size()-1);
        std::sort(slice.begin(), slice.end());
        int max_c = 1;
        for(size_t i=0; i<10; ++i) {
            size_t j = i;
            while(j+1 < 10 && (slice[j+1]-slice[i]) <= Config::TOLERANCE_BANDS) ++j;
            max_c = std::max(max_c, (int)(j-i+1));
        }
        rcod = std::clamp(1.0 - ((double)max_c / 10.0), 0.0, 1.0);
        spread = (double)(slice.back() - slice.front()) / Config::QUANTIZE_SCALE;
    }
    bool ready() const { return nodes[0].ring.full(); }
    void reset() { for(auto& n : nodes) { n.ring.reset(); n.init = false; } }
};

class OmegaGovernor {
    InertialSubstrate substrate;
    FastRing<double, Config::BASELINE_WIN> baseline_buf;
    FastRing<double, Config::FLATLINE_WIN> flatline_buf;
    SystemMode mode = SystemMode::INIT;
    uint32_t fault_mask = FAULT_NONE;
    double last_raw = 0.0, s_pos = 0.0, s_neg = 0.0, b_sum = 0.0, b_sum_sq = 0.0;
    double cur_rcod = 0.0, cur_z = 0.0;
    double shock_limit = 0.70, spread_limit = 0.15, flow_enter = 0.15, cusum_h = 5.0;
    int stability_streak = 0, baseline_ticks = 0, persistence = 0;
    bool has_last = false;

public:
    void update_thresholds(const PhaseParameters& p) {
        shock_limit = p.shock_limit; spread_limit = p.spread_limit;
        flow_enter = p.flow_enter; cusum_h = p.cusum_h;
    }
    double get_rcod() const { return cur_rcod; }
    double get_z() const { return cur_z; }
    SystemMode get_mode() const { return mode; }

    GovernorPayload tick(double raw, bool watchdog_ok) {
        GovernorPayload p;
        if(!watchdog_ok) fault_mask |= FAULT_WATCHDOG;
        if(!std::isfinite(raw)) fault_mask |= FAULT_NAN_INF;
        if(raw >= Config::SIGNAL_MAX || raw <= Config::SIGNAL_MIN) fault_mask |= FAULT_CLIPPING;
        double delta = has_last ? std::abs(raw - last_raw) : 0.0;
        if(delta > Config::SENSOR_SLEW_LIMIT) fault_mask |= FAULT_SLEW;
        flatline_buf.push(raw);
        if(flatline_buf.full()){
            double min_v = flatline_buf.get_from_oldest(0), max_v = flatline_buf.get_from_oldest(0);
            for(size_t i=1; i<Config::FLATLINE_WIN; ++i){
                double v = flatline_buf.get_from_oldest(i);
                min_v = std::min(min_v, v); max_v = std::max(max_v, v);
            }
            if(Config::LSB_NOISE_FLOOR > 0.0001 && (max_v - min_v) < Config::LSB_NOISE_FLOOR) fault_mask |= FAULT_FLATLINE;
        }
        if(fault_mask != FAULT_NONE) { mode = SystemMode::HARDWARE_FAULT; p.mode = mode; p.fault_mask = fault_mask; p.fast_trip_actuation = true; return p; }
        if(delta > Config::PLASMA_SLEW_LIMIT) { mode = SystemMode::TRIPPED; p.mode = mode; p.fast_trip_actuation = true; return p; }
        
        double rcod, spread;
        substrate.process(raw, rcod, spread);
        cur_rcod = rcod; last_raw = raw; has_last = true;
        if(!substrate.ready()){ mode = SystemMode::WARMUP_SUBSTRATE; p.mode = mode; return p; }

        bool stable = (delta < Config::STARTUP_SLEW) && (rcod < flow_enter);
        if(stable) stability_streak++; else stability_streak = 0;
        
        double z = 0.0;
        if(baseline_buf.size() >= 10){
            double n = baseline_buf.size(), mean = b_sum/n, var = (b_sum_sq/n)-(mean*mean);
            z = (var > 0.000001) ? (raw - mean)/std::sqrt(var) : 0.0;
        }
        cur_z = z;
        if((mode == SystemMode::MONITORING || mode == SystemMode::WARMUP_BASELINE) && stability_streak >= Config::STABILITY_STREAK && std::abs(z) < 1.5){
            if(baseline_buf.full()){ double old = baseline_buf.get_from_oldest(0); b_sum -= old; b_sum_sq -= (old*old); }
            baseline_buf.push(raw); b_sum += raw; b_sum_sq += (raw*raw);
        }
        if(baseline_buf.full()){
            s_pos = std::max(0.0, s_pos + z - Config::CUSUM_K);
            s_neg = std::max(0.0, s_neg - z - Config::CUSUM_K);
            bool drift = (s_pos > cusum_h || s_neg > cusum_h);
            bool fracture = (rcod > shock_limit && spread > spread_limit);
            if(fracture){ if(++persistence >= Config::PERSISTENCE_ENTER) mode = SystemMode::ALARM_FRACTURE; }
            else if(drift) mode = SystemMode::PRE_ALARM_DRIFT;
            else if(stable && std::abs(z) < 1.0){ persistence = 0; s_pos *= 0.95; s_neg *= 0.95; mode = SystemMode::MONITORING; }
        } else { mode = (++baseline_ticks > Config::BASELINE_TIMEOUT) ? SystemMode::DEGRADED_NO_BASELINE : SystemMode::WARMUP_BASELINE; }
        p.mode = mode; p.fast_trip_actuation = (mode == SystemMode::TRIPPED || mode == SystemMode::HARDWARE_FAULT);
        p.supervisory_warning = (mode == SystemMode::ALARM_FRACTURE || mode == SystemMode::PRE_ALARM_DRIFT);
        return p;
    }
    void reset() { substrate.reset(); baseline_buf.reset(); flatline_buf.reset(); mode = SystemMode::INIT; fault_mask = FAULT_NONE; s_pos = 0; s_neg = 0; b_sum = 0; b_sum_sq = 0; stability_streak = 0; baseline_ticks = 0; persistence = 0; has_last = false; }
};

#endif
