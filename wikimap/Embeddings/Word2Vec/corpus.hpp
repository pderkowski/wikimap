#pragma once

#include <vector>
#include <unordered_map>
#include <random>
#include <cmath>

#include "defs.hpp"


namespace w2v {


template<class Word>
class Vocabulary {
public:
    void add(const Word& word);
    void reset();

    void set_unigram_distribution(double subsampling_factor);

    template<class Rng>
    Token sample(Rng& rng) const { return unigrams_(rng); }

    Token get_token(const Word& word) const { return word2token_.at(word); }
    Int size() const { return token2word_.size(); }

private:
    std::unordered_map<Word, Token> word2token_;
    std::vector<Word> token2word_;
    std::vector<Int> token2count_;
    std::discrete_distribution<Token> unigrams_;
};

template<class Word>
void Vocabulary<Word>::add(const Word& word) {
    if (word2token_.find(word) == word2token_.end()) {
        Token new_token = token2word_.size();
        word2token_[word] = new_token;
        token2word_.push_back(word);
        token2count_.push_back(1);
    } else {
        Token token = word2token_.at(word);
        ++token2count_[token];
    }
}

template<class Word>
void Vocabulary<Word>::reset() {
    word2token_.clear();
    token2word_.clear();
    token2count_.clear();
    unigrams_ = decltype(unigrams_)();
}

template<class Word>
void Vocabulary<Word>::set_unigram_distribution(double subsampling_factor) {
    std::vector<double> weights(token2count_.size());

    #pragma omp parallel for schedule(static)
    for (Int i = 0; i < token2count_.size(); ++i) {
        weights[i] = pow(token2count_[i], subsampling_factor);
    }

    unigrams_ = decltype(unigrams_)(weights.begin(), weights.end());
}


class Corpus {
public:
    Corpus();

    void reset();

    void add_token(Token token) { tokens_.push_back(token); }
    void end_sequence() { separators_.push_back(tokens_.size()); }

    Int size() const { return tokens_.size(); }
    Int sequence_count() const { return separators_.size() - 1; }
    SequenceRange get_sequence(Int index) const;

private:
    Sequence tokens_;
    std::vector<Int> separators_;
};


Corpus::Corpus()
: separators_({ 0 })
{ }

void Corpus::reset() {
    tokens_.clear();
    separators_ = { 0 };
}

SequenceRange Corpus::get_sequence(Int index) const {
    auto start = separators_[index];
    auto end = separators_[index + 1];
    return SequenceRange(tokens_.begin() + start, tokens_.begin() + end);
}


}
