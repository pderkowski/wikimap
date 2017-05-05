#include "random.h"
#include <omp.h>

ThreadRandom ThreadRandom::instance_;


ThreadRandom::ThreadRandom() {
    seed(time(NULL));
}

TRnd& ThreadRandom::get() {
    return instance_.rnds_[omp_get_thread_num()];
}

void ThreadRandom::seed(int seed) {
    instance_.rnds_.Clr();
    for (int i = 0; i < omp_get_max_threads(); ++i) {
        instance_.rnds_.Add(TRnd(seed + i));
    }
}
