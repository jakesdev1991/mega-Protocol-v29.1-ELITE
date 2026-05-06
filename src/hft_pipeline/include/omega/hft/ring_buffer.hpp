#pragma once

#include <array>
#include <atomic>
#include <cstddef>

namespace omega::hft {

template <typename T, std::size_t Size>
class SpscRingBuffer {
public:
    static_assert(Size >= 2, "ring buffer requires at least two slots");

    bool push(const T& item) noexcept {
        const std::size_t h = head_.load(std::memory_order_relaxed);
        const std::size_t next = increment(h);
        if (next == tail_.load(std::memory_order_acquire)) {
            return false;
        }
        buffer_[h] = item;
        head_.store(next, std::memory_order_release);
        return true;
    }

    bool pop(T& item) noexcept {
        const std::size_t t = tail_.load(std::memory_order_relaxed);
        if (t == head_.load(std::memory_order_acquire)) {
            return false;
        }
        item = buffer_[t];
        tail_.store(increment(t), std::memory_order_release);
        return true;
    }

    bool empty() const noexcept {
        return tail_.load(std::memory_order_acquire) == head_.load(std::memory_order_acquire);
    }

private:
    static constexpr std::size_t increment(std::size_t value) noexcept {
        return (value + 1U) % Size;
    }

    alignas(64) std::atomic<std::size_t> head_{0};
    alignas(64) std::atomic<std::size_t> tail_{0};
    alignas(64) std::array<T, Size> buffer_{};
};

} // namespace omega::hft
