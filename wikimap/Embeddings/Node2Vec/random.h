#ifndef RANDOM_H
#define RANDOM_H

#include "Snap.h"

class ThreadRandom {
public:
    ThreadRandom();

    static TRnd& get();
    static void seed(int seed);

private:
    static ThreadRandom instance_;

    TVec<TRnd> rnds_;
};

#endif // RANDOM_H