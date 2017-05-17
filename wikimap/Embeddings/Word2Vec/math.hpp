#pragma once

#include <vector>
#include <cmath>
#include <algorithm>

#include <omp.h>


namespace w2v {

namespace math {


const double MAX_EXPONENT = 7.;
const int TABLE_SIZE = 100000;


std::vector<double> compute_sigmoid_table() {
    std::vector<double> table(TABLE_SIZE);

    // There are TABLE_SIZE buckets, covering the range from -MAX_EXPONENT to
    // MAX_EXPONENT, so each one of them has the following span:
    const double span = 2. * MAX_EXPONENT / TABLE_SIZE;

    #pragma omp parallel for schedule(static)
    for (int i = 0; i < TABLE_SIZE; ++i) {
        double exponent = -MAX_EXPONENT; // left end of the leftmost bucket
        exponent += i * span; // shift to the left end of the current bucket
        exponent += 0.5 * span; // take the middle point of the bucket

        // use one of two formulas for sigmoid depending on the sign of exponent
        if (exponent >= 0) {
            table[i] = 1. / (1. + exp(-exponent));
        } else {
            double z = exp(exponent);
            table[i] = z / (1. + z);
        }
    }

    return table;
}


double sigmoid(double x) {
    // Tabularized values of sigmoid.
    static const std::vector<double> sigmoid_table = compute_sigmoid_table();

    if (x >= MAX_EXPONENT) {
        return 1.; // close enough to real value
    } else if (x < -MAX_EXPONENT) {
        return 0.; // close enough to real value
    } else {
        double f = (x + MAX_EXPONENT) / (2. * MAX_EXPONENT); // this should be in [0, 1)
        int index = static_cast<int>(f * TABLE_SIZE);
        index = std::min<int>(sigmoid_table.size() - 1, index); // not sure if f couldn't end up rounded to 1
        return sigmoid_table[index];
    }
}


} // namespace math


} // namespace w2v