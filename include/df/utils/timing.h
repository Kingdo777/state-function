//
// Created by kingdo on 2022/2/25.
//

#ifndef DataFunction_TIMING_H
#define DataFunction_TIMING_H

#include <chrono>
#include <string>
#include <df/utils/log.h>

#ifdef ENABLE_TRACE
#define TIMING_START(name) \
    const df::utils::TimePoint name = df::utils::Timing::startTimer();
#define TIMING_END(name) \
    df::utils::Timing::logEndTimer(#name, name);
#define TIMING_SUMMARY \
    df::utils::Timing::printTimerTotals();
#else
#define TIMING_START(name)
#define TIMING_END(name)
#define TIMING_SUMMARY
#endif

namespace df::utils
{
    typedef std::chrono::steady_clock::time_point TimePoint;

    extern TimePoint globalTimePoint;

    uint64_t getMillsTimestamp();

    class Timing
    {
    public:
        Timing() = default;

        static TimePoint startTimer();

        static void logEndTimer(const std::string& label,
                                const df::utils::TimePoint& begin);

        static void printTimerTotals();

    private:
        static TimePoint now();

        static long timeDiffMicro(const TimePoint& t1, const TimePoint& t2);
    };
}

#endif // DataFunction_TIMING_H
