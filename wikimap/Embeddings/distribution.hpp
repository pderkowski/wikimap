#pragma once

#include <vector>

#include "math.hpp"


namespace emb {


class DiscreteDistribution {
public:
    DiscreteDistribution();
    explicit DiscreteDistribution(const std::vector<double>& weights);

    template<class Rng>
    size_t operator ()(Rng& rng) const;

private:
    void construct_tables(std::vector<double> weights);
    void scale(std::vector<double>& weights) const;

    size_t size_;

    // clumping both prob and alias together should help a little with memory locality
    std::vector<std::pair<Float, size_t>> prob_alias_;
};


DiscreteDistribution::DiscreteDistribution()
:   size_(0)
{ }

DiscreteDistribution::DiscreteDistribution(const std::vector<double>& weights)
:       size_(weights.size()) {

    construct_tables(weights);
}

template<class Rng>
inline size_t DiscreteDistribution::operator()(Rng& rng) const {
    size_t roll = rng() % size_;
    double toss = static_cast<double>(rng()) / rng.max();

    return (toss <= prob_alias_[roll].first)? roll : prob_alias_[roll].second;
}

void DiscreteDistribution::construct_tables(std::vector<double> weights) {
    prob_alias_ = decltype(prob_alias_)(weights.size());

    scale(weights);

    std::vector<size_t> small, large;
    for (size_t i = 0; i < weights.size(); ++i) {
        if (weights[i] < 1.) {
            small.push_back(i);
        } else {
            large.push_back(i);
        }
    }

    while (!small.empty() && !large.empty()) {
        auto l = small.back(); small.pop_back();
        auto g = large.back(); large.pop_back();

        prob_alias_[l].first = weights[l];
        prob_alias_[l].second = g;

        weights[g] = (weights[g] - 1.) + weights[l];

        if (weights[g] < 1.) {
            small.push_back(g);
        } else {
            large.push_back(g);
        }
    }

    while (!large.empty()) {
        auto g = large.back(); large.pop_back();

        prob_alias_[g].first = 1.;
    }

    while (!small.empty()) {
        auto l = small.back(); small.pop_back();

        prob_alias_[l].first = 1.;
    }
}

void DiscreteDistribution::scale(std::vector<double>& weights) const {
    double sum = math::kahan_sum(weights.begin(), weights.end());
    double factor = weights.size() / sum;

    for (auto& w : weights) {
        w *= factor;
    }
}


} // namespace emb