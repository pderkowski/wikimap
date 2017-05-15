#pragma once

#include <cstdarg>
#include <cstdio>
#include <random>
#include <vector>

#include <omp.h>

#include "defs.hpp"


namespace w2v {


inline void log(const char *format, ...) {
    va_list arglist;
    va_start(arglist, format);
    vprintf(format, arglist);
    va_end(arglist);
    fflush(stdout);
}

inline void report_progress(Int seen, Int expected) {
    w2v::log("\rProgress: %.2lf%% ", seen*100. / expected);
}


// This class holds random number generators for each thread.
class Random {
public:
    typedef std::mt19937 Rng;

    Random();

    static Rng& get();

private:
    std::vector<Rng> rnds_;
};

Random::Random() {
    auto seed = std::random_device()();
    for (int i = 0; i < omp_get_max_threads(); ++i) {
        rnds_.push_back(Rng(seed + i));
    }
}

Random::Rng& Random::get() {
    static Random instance;
    return instance.rnds_[omp_get_thread_num()];
}


}