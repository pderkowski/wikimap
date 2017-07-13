#pragma once

#include <vector>
#include <vector>
#include <functional>

#include "defs.hpp"


namespace emb {


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


class FileCorpus {
public:
    typedef std::string word_type;


    class iterator {
    public:
        explicit iterator(
            const FileCorpus* corpus = nullptr,
            size_t start_pos = std::numeric_limits<size_t>::max(),
            size_t end_pos = std::numeric_limits<size_t>::max());

        bool operator ==(const iterator& other) const;
        bool operator !=(const iterator& other) const;

        const word_type& operator *() const { return value_; }
        iterator& operator ++();

    private:
        const FileCorpus* corpus_;
        size_t pos_;
        size_t end_pos_;
        word_type value_;
    };


    class SentenceSpan {
    public:
        SentenceSpan(size_t size, const iterator& begin)
        :   size_(size), begin_(begin)
        { }

        iterator begin() const { return begin_; }
        iterator end() const { return iterator(); }

        size_t size() const { return size_; }

    private:
        size_t size_;
        iterator begin_;
    };


    explicit FileCorpus(const std::string& fname);

    Int word_count() const { return word_count_; }
    Int sentence_count() const { return sentence_bounds_.size(); }

    SentenceSpan get_sentence(Int index) const;

private:
    void scan_sentences();
    std::pair<size_t, int> scan_sentence(size_t pos) const;
    size_t scan_word(size_t pos) const;

    // std::vector<std::string> read_sentence(size_t pos) const;
    size_t read_word(size_t pos, std::string& word) const;

private:
    io::MmappedFile file_;
    Int word_count_;
    std::vector<std::pair<size_t, size_t>> sentence_bounds_;
    std::vector<size_t> sentence_sizes_;
};

FileCorpus::FileCorpus(const std::string& fname)
:       file_(fname), word_count_(0) {

    scan_sentences();
}

inline void FileCorpus::scan_sentences() {
    sentence_bounds_.clear();

    size_t start_pos = 0;
    size_t end_pos;
    int words_in_sentence;
    while (start_pos < file_.size) {
        std::tie(end_pos, words_in_sentence) = scan_sentence(start_pos);
        sentence_bounds_.emplace_back(start_pos, end_pos);
        sentence_sizes_.emplace_back(words_in_sentence);
        word_count_ += words_in_sentence;
        start_pos = end_pos + 1;
    }
}

inline std::pair<size_t, int> FileCorpus::scan_sentence(size_t pos) const {
    pos = scan_word(pos);
    int words = 1;

    for (   ;
            pos < file_.size
                && (words < io::MAX_SENTENCE_SIZE
                && file_.data[pos] != '\n');
            ++words) {

        pos = scan_word(++pos);
    }

    return std::make_pair(pos, words);
}

inline size_t FileCorpus::scan_word(size_t pos) const {
    while (pos < file_.size) {
        const char c = file_.data[pos];
        if ((c == ' ') | (c == '\n') | (c == '\t')) {
            break;
        }
        ++pos;
    }
    return pos;
}

inline size_t FileCorpus::read_word(size_t start_pos, std::string& word) const {
    auto end_pos = scan_word(start_pos);
    word.assign(
        file_.data + start_pos,
        std::min<size_t>(end_pos - start_pos, io::MAX_WORD_SIZE));
    return end_pos;
}

inline FileCorpus::SentenceSpan FileCorpus::get_sentence(Int index) const {
    auto bounds = sentence_bounds_[index];
    return SentenceSpan(
        sentence_sizes_[index],
        iterator(this, bounds.first, bounds.second));
}

FileCorpus::iterator::iterator(
            const FileCorpus* corpus,
            size_t start_pos,
            size_t end_pos)
:       corpus_(corpus), pos_(start_pos), end_pos_(end_pos) {
    ++(*this);
}

inline bool FileCorpus::iterator::operator ==(const iterator& other) const {
    return pos_ == other.pos_;
}

inline bool FileCorpus::iterator::operator !=(const iterator& other) const {
    return pos_ != other.pos_;
}

inline FileCorpus::iterator& FileCorpus::iterator::operator ++() {
    if (pos_ < end_pos_) {
        pos_ = corpus_->read_word(pos_, value_) + 1;
    } else {
        pos_ = std::numeric_limits<size_t>::max();
    }
    return *this;
}


} // namespace emb
