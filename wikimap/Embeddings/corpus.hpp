#pragma once

#include <vector>
#include <unordered_map>
#include <random>
#include <cmath>

#include "defs.hpp"
#include "utils.hpp"
#include "logging.hpp"


namespace w2v {


template<class Word>
class Vocabulary {
private:
    std::unordered_map<Word, Id> word2id_;
    std::vector<Word> id2word_;

public:
    typedef typename decltype(id2word_)::iterator iterator;
    typedef typename decltype(id2word_)::const_iterator const_iterator;

public:
    void add(const Word& word);

    Id get_id(const Word& word) const { return word2id_.at(word); }
    Word get_word(Id id) const { return id2word_[id]; }

    Int size() const { return id2word_.size(); }

    const_iterator begin() const { return id2word_.begin(); }
    iterator begin() { return id2word_.begin(); }

    const_iterator end() const { return id2word_.end(); }
    iterator end() { return id2word_.end(); }
};

template<class Word>
void Vocabulary<Word>::add(const Word& word) {
    if (word2id_.find(word) == word2id_.end()) {
        Id new_id = id2word_.size();
        word2id_[word] = new_id;
        id2word_.push_back(word);
    }
}


// This class represents the training data, where words are replaced with unique
// ids. Ids are assigned by Vocabulary. The data is conceptually partitioned
// into sequences. A sequence is a sentence with ids instead of words. Since all
// sequences are stored in one big vector, the boundaries between them are kept
// in separators vector. Corpus is built by adding tokens at the end of it and
// marking the end of a sequence. IT IS IMPORTANT THAT TOKEN IDS COME FROM
// VOCABULARY BECAUSE THEY HAVE TO BE SEQUENTIAL, that is, the argument to
// add_token must either have been seen before, or must be an increment of the
// highest value already in the corpus.
//
// The class also keeps counts of seen tokens, which allows for sampling.
// You have to manually call set_unigram_distribution before sampling.
class Corpus {
public:
    Corpus();

    void add_token(Id token_id);
    void end_sequence() { separators_.push_back(token_ids_.size()); }

    Int size() const { return token_ids_.size(); }

    Int sequence_count() const { return separators_.size() - 1; }
    Int token_occurence_count(Id token_id) const { return id2count_[token_id]; }

    SequenceRange get_sequence(Int index) const;

    // sampling
    void set_unigram_distribution(double subsampling_factor);
    Id sample() const { return unigrams_(Random::get()); }

private:
    Sequence token_ids_;
    std::vector<Int> separators_;
    std::vector<Int> id2count_;
    // The reason this is mutable is that its operator () is surprisingly
    // not const. This may be because some distributions supposedly have state
    // (normal distribution?). If discrete_distribution is also state dependend
    // this needs to be changed.
    mutable std::discrete_distribution<Id> unigrams_;
};


Corpus::Corpus()
: separators_({ 0 })
{ }

void Corpus::add_token(Id token_id) {
    token_ids_.push_back(token_id);
    if (static_cast<size_t>(token_id) < id2count_.size()) {
        ++id2count_[token_id];
    } else if (static_cast<size_t>(token_id) == id2count_.size()) {
        id2count_.push_back(1);
    } else {
        logging::log("Trying to insert nonsequential token id to corpus!");
        exit(1);
    }
}

SequenceRange Corpus::get_sequence(Int index) const {
    auto start = separators_[index];
    auto end = separators_[index + 1];
    return SequenceRange(token_ids_.begin() + start, token_ids_.begin() + end);
}

void Corpus::set_unigram_distribution(double subsampling_factor) {
    std::vector<double> weights(id2count_.size());

    #pragma omp parallel for schedule(static)
    for (size_t i = 0; i < id2count_.size(); ++i) {
        weights[i] = pow(id2count_[i], subsampling_factor);
    }

    unigrams_ = decltype(unigrams_)(weights.begin(), weights.end());
}


}
