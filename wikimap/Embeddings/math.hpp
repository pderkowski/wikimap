#pragma once

#include <vector>
#include <cmath>
#include <algorithm>

#include <omp.h>

#include "defs.hpp"

namespace emb {

namespace math {


const Float MAX_EXPONENT = 6.0f;
const int TABLE_SIZE = 10000;


std::vector<Float> compute_sigmoid_table() {
    std::vector<Float> table(TABLE_SIZE);

    // There are TABLE_SIZE buckets, covering the range from -MAX_EXPONENT to
    // MAX_EXPONENT, so each one of them has the following span:
    const double span = 2.0 * MAX_EXPONENT / TABLE_SIZE;

    #pragma omp parallel for schedule(static)
    for (int i = 0; i < TABLE_SIZE; ++i) {
        double exponent = -MAX_EXPONENT; // left end of the leftmost bucket
        exponent += i * span; // shift to the left end of the current bucket
        exponent += 0.5 * span; // take the middle point of the bucket

        // use one of two formulas for sigmoid depending on the sign of exponent
        if (exponent >= 0.0) {
            table[i] = 1.0 / (1.0 + exp(-exponent));
        } else {
            double z = exp(exponent);
            table[i] = z / (1.0 + z);
        }
    }

    return table;
}

// Tabularized values of sigmoid.
std::vector<Float> sigmoid_table = compute_sigmoid_table();

inline Float sigmoid(Float x) {
    if (x >= MAX_EXPONENT) {
        return 1.0f; // close enough to real value
    } else if (x < -MAX_EXPONENT) {
        return 0.0f; // close enough to real value
    } else {
        Float f = (x + MAX_EXPONENT) / (2.0f * MAX_EXPONENT); // this should be in [0, 1)
        int index = static_cast<int>(f * TABLE_SIZE);
        index = std::min<int>(sigmoid_table.size() - 1, index); // not sure if f couldn't end up rounded to 1
        return sigmoid_table[index];
    }
}


template <class Iter>
double kahan_sum(Iter begin, Iter end) {
    double result = 0.;

    double c = 0.;
    for(;begin != end; ++begin) {
        double y = *begin - c;
        double t = result + y;
        c = (t - result) - y;
        result = t;
    }
    return result;
}


} // namespace math


} // namespace emb