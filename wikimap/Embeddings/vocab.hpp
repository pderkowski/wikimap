#pragma once

#include <unordered_map>
#include <vector>

#include "defs.hpp"
#include "distribution.hpp"

namespace emb {


template<class Word>
class Vocab {
private:
    std::unordered_map<Word, Id> word2id_;
    std::vector<Word> id2word_;
    std::vector<Int> id2count_;
    DiscreteDistribution unigrams_;

public:
    typedef typename decltype(id2word_)::iterator iterator;
    typedef typename decltype(id2word_)::const_iterator const_iterator;

public:
    Vocab();

    void add(const Word& word, Int count);

    Id get_id(const Word& word) const { return word2id_.at(word); }
    Word get_word(Id id) const { return id2word_[id]; }

    Int size() const { return id2word_.size(); }

    const_iterator begin() const { return id2word_.begin(); }
    iterator begin() { return id2word_.begin(); }

    const_iterator end() const { return id2word_.end(); }
    iterator end() { return id2word_.end(); }

    // sampling
    void init_sampling(double subsampling_factor);

    template<class Rng>
    Id sample(Rng& rng) const { return unigrams_(rng); }

};

template<class Word>
Vocab<Word>::Vocab() {
    word2id_.max_load_factor(0.5);
    word2id_.reserve(1000000);
}

template<class Word>
inline void Vocab<Word>::add(const Word& word, Int count) {
    auto res = word2id_.insert(std::make_pair(word, id2word_.size()));

    // an element was actually inserted
    if (res.second == true) {
        id2word_.push_back(word);
        id2count_.push_back(count);
    }
}

template<class Word>
void Vocab<Word>::init_sampling(double subsampling_factor) {
    std::vector<double> weights(id2count_.size());

    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < id2count_.size(); ++i) {
        weights[i] = pow(id2count_[i], subsampling_factor);
    }

    unigrams_ = decltype(unigrams_)(weights);
}

} // namespace emb