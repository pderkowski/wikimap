#pragma once

#include <vector>
#include <vector>
#include <functional>

#include "defs.hpp"


namespace emb {


template<class Word = std::string>
class MemoryCorpus {
public:
    typedef Word word_type;

public:
    MemoryCorpus();

    template<class Iterator>
    MemoryCorpus(Iterator begin, Iterator end);

    template<class Container>
    void add_sentence(const Container& container);

    template<class Iterator>
    void add_sentence(Iterator begin, Iterator end);

    Int token_count() const { return tokens_.size(); }
    Int sentence_count() const { return separators_.size() - 1; }

    SentenceSpan<Word> get_sentence(Int index) const;

private:
    std::vector<Word> tokens_;
    std::vector<Int> separators_;
};

template<class Word>
MemoryCorpus<Word>::MemoryCorpus()
:   separators_({ 0 })
{ }

template<class Word>
template<class Iterator>
MemoryCorpus<Word>::MemoryCorpus(Iterator begin, Iterator end)
:       separators_({ 0 }) {

    for (auto current = begin; current != end; ++current) {
        add_sentence(*current);
    }
}

template<class Word>
template<class Container>
inline void MemoryCorpus<Word>::add_sentence(const Container& container) {
    add_sentence(container.begin(), container.end());
}

template<class Word>
template<class Iterator>
inline void MemoryCorpus<Word>::add_sentence(Iterator begin, Iterator end) {
    tokens_.insert(tokens_.end(), begin, end);
    separators_.push_back(tokens_.size());
}

template<class Word>
inline SentenceSpan<Word> MemoryCorpus<Word>::get_sentence(Int index) const {
    auto start = separators_[index];
    auto end = separators_[index + 1];
    return SentenceSpan<Word>(tokens_.begin() + start, tokens_.begin() + end);
}


template<class Word = std::string>
class GeneratingCorpus {
public:
    typedef Word word_type;

public:
    GeneratingCorpus(
        std::function<Sentence<Word>(Int, Int)> generator,
        Int sentence_count);

    Int sentence_count() const { return sentence_count_; }

    Sentence<Word> get_sentence(Int index) const;

private:
    std::function<Sentence<Word>(Int, Int)> generator_;
    Int sentence_count_;
    std::vector<Int> seeds_;
};


template<class Word>
GeneratingCorpus<Word>::GeneratingCorpus(
            std::function<Sentence<Word>(Int, Int)> generator,
            Int sentence_count)
:       generator_(generator), sentence_count_(sentence_count) {

    seeds_.resize(sentence_count);

    for (auto& seed : seeds_) {
        seed = Random::global_rng()();
    }
}

template<class Word>
inline Sentence<Word> GeneratingCorpus<Word>::get_sentence(Int index) const {
    return generator_(index, seeds_[index]);
}


} // namespace emb
