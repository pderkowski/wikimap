#pragma once

#include <vector>
#include <unordered_map>
#include <functional>

#include <omp.h>

#include "defs.hpp"
#include "logging.hpp"


namespace emb {


namespace parallel {


template<class Word>
class CountingUnit {
private:
    std::vector<std::vector<Word>> inputs_;
    std::unordered_map<Word, Int> counts_;

public:
    typedef typename decltype(counts_)::const_iterator const_iterator;

public:
    CountingUnit();

    void add(const Word& w);
    void count();

    const_iterator begin() const { return counts_.begin(); }
    const_iterator end() const { return counts_.end(); }

    size_t size() const { return counts_.size(); }
};

template<class Word>
CountingUnit<Word>::CountingUnit()
:       inputs_(omp_get_max_threads()) {

    counts_.reserve(3000000);
    for (int i = 0; i < inputs_.size(); ++i) {
        inputs_[i].reserve(100000);
    }
}

template<class Word>
inline void CountingUnit<Word>::add(const Word& w) {
    inputs_[omp_get_thread_num()].push_back(w);
}

template<class Word>
void CountingUnit<Word>::count() {
    for (auto& input : inputs_) {
        for (const auto& w : input) {
            ++counts_[w];
        }
        input.clear();
    }
}



template<class Corpus>
class WordCount {
public:
    class const_iterator;
    typedef typename Corpus::word_type word_type;

public:
    explicit WordCount(const Corpus& corpus);

    const_iterator begin() const {
        return const_iterator(units_.begin(), units_.end());
    }
    const_iterator end() const {
        return const_iterator(units_.end(), units_.end());
    }

private:
    void count_words(const Corpus& corpus);
    void count_words_in_batch();
    void dispatch_word(const word_type& word);

private:
    typedef std::vector<CountingUnit<word_type>> UnitContainer;
    typedef typename UnitContainer::const_iterator BigIterator;
    typedef typename CountingUnit<word_type>::const_iterator SmallIterator;

    UnitContainer units_;

public:
    class const_iterator {
    public:
        typedef ptrdiff_t difference_type;
        typedef typename SmallIterator::value_type value_type;
        typedef typename SmallIterator::reference reference;
        typedef typename SmallIterator::pointer pointer;
        typedef std::forward_iterator_tag iterator_category;

    public:
        const_iterator(BigIterator big_it_start, BigIterator big_it_end)
        :   big_it_(big_it_start),
            big_it_end_(big_it_end),
            small_it_(get_small_it()),
            small_it_end_(get_small_it_end())
        { }

        const_iterator()
        :   big_it_(), big_it_end_(), small_it_(), small_it_end_()
        { }

        const_iterator& operator++() {
            ++small_it_;
            if (small_it_ == small_it_end_) {
                ++big_it_;
                small_it_ = get_small_it();
                small_it_end_ = get_small_it_end();
            }
            return *this;
        }

        const_iterator operator++(int) {
            auto self = *this;
            ++*this;
            return self;
        }

        reference operator*() const { return *small_it_; }
        pointer operator->() const { return &(*small_it_); }

        friend bool operator==(
                const const_iterator& lhs,
                const const_iterator& rhs) {

            return lhs.big_it_ == rhs.big_it_
                && lhs.big_it_end_ == rhs.big_it_end_
                && lhs.small_it_ == rhs.small_it_
                && lhs.small_it_end_ == rhs.small_it_end_;
        }

        friend bool operator!=(
                const const_iterator& lhs,
                const const_iterator& rhs) {

            return !(lhs == rhs);
        }

    private:
        SmallIterator get_small_it() {
            return (big_it_ == big_it_end_)? SmallIterator() : big_it_->begin();
        }

        SmallIterator get_small_it_end() {
            return (big_it_ == big_it_end_)? SmallIterator() : big_it_->end();
        }

    private:
        BigIterator big_it_;
        BigIterator big_it_end_;
        SmallIterator small_it_;
        SmallIterator small_it_end_;
    };
};

template<class Corpus>
WordCount<Corpus>::WordCount(const Corpus& corpus)
:       units_(omp_get_max_threads()) {

    count_words(corpus);
}

template<class Corpus>
void WordCount<Corpus>::count_words(const Corpus& corpus) {
    const Int max_batch_size = 1000;

    for (Int i = 0; i < corpus.sentence_count(); i += max_batch_size) {
        logging::inline_log(
            "* progress: %6.2f%%",
            100.0 * static_cast<double>(i) / corpus.sentence_count());

        auto batch_size = std::min(
            max_batch_size,
            corpus.sentence_count() - i);

        #pragma omp parallel for schedule(dynamic, 1)
        for (Int j = 0; j < batch_size; ++j) {
            for (const auto& word : corpus.get_sentence(i + j)) {
                dispatch_word(word);
            }
        }

        count_words_in_batch();
    }

    logging::inline_log("- progress: 100.00%%\n");
}

template<class Corpus>
void WordCount<Corpus>::count_words_in_batch() {
    #pragma omp parallel for schedule(static, 1)
    for (int j = 0; j < units_.size(); ++j) {
        units_[j].count();
    }
}

template<class Corpus>
inline void WordCount<Corpus>::dispatch_word(const word_type& word) {
    static std::hash<word_type> s_hash;

    auto hash_hash = s_hash(word) >> 16;
    units_[hash_hash % units_.size()].add(word);
}


} // parallel


} // namespace emb