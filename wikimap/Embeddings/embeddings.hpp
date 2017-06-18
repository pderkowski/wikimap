#pragma once

#include <vector>
#include <unordered_map>

#include "io.hpp"
#include "defs.hpp"
#include "logging.hpp"


namespace emb {


template<class Word>
class Embeddings {
public:
    typedef Word value_type;
    typedef std::unordered_map<Word, Id> WordMap;
    typedef typename std::unordered_map<Word, Id>::const_iterator WordIterator;

    class iterator {
    public:
        typedef ptrdiff_t difference_type;
        typedef std::pair<Word, Embedding> value_type;
        typedef const value_type& reference;
        typedef const value_type* pointer;
        typedef std::input_iterator_tag iterator_category;

    public:
        iterator(const Embeddings<Word>* parent, WordIterator word_iterator)
        :   parent_(parent), word_iterator_(word_iterator)
        { }

        iterator()
        :   parent_(nullptr), word_iterator_()
        { }

        iterator& operator++() {
            ++word_iterator_;
            return *this;
        }

        iterator operator++(int) {
            auto self = *this;
            ++*this;
            return self;
        }

        reference operator*() const {
            value_ = get_value();
            return value_;
        }
        pointer operator->() const {
            value_ = get_value();
            return &value_;
        }

        friend bool operator==(const iterator& lhs, const iterator& rhs) {
            return lhs.parent_ == rhs.parent_
                && lhs.word_iterator_ == rhs.word_iterator_;
        }

        friend bool operator!=(const iterator& lhs, const iterator& rhs) {
            return !(lhs == rhs);
        }

    private:
        value_type get_value() const {
            auto word = word_iterator_->first;
            auto index = word_iterator_->second;
            auto embedding = parent_->get(index);
            return std::make_pair(word, embedding);
        }

        const Embeddings<Word>* parent_;
        WordIterator word_iterator_;
        mutable value_type value_;
    };

public:
    explicit Embeddings() : dimension_(0) { }
    Embeddings(
        const WordMap& word_map,
        const std::vector<Float>& word_embeddings,
        int dimension);

    iterator begin() const { return iterator(this, word_map_.begin()); }
    iterator end() const { return iterator(this, word_map_.end()); }

    void save(const std::string& fname) const;
    void load(const std::string& fname);

    Embedding operator[](const Word& word) const;
    bool has(const Word& word) const;

    std::vector<Word> words() const;

private:
    Embedding get(Int index) const;

    std::unordered_map<Word, Id> word_map_;
    std::vector<Float> word_embeddings_;
    int dimension_;
};

template<class Word>
Embeddings<Word>::Embeddings(
        const std::unordered_map<Word, Id>& word2id,
        const std::vector<Float>& word_embeddings,
        int dimension)
:   word_map_(word2id), word_embeddings_(word_embeddings), dimension_(dimension)
{ }


template<class Word>
inline Embedding Embeddings<Word>::operator[](const Word& word) const {
    return get(word_map_.at(word));
}

template<class Word>
inline Embedding Embeddings<Word>::get(Int index) const {
    return Embedding(
        word_embeddings_.begin() + index * dimension_,
        word_embeddings_.begin() + (index + 1) * dimension_);
}

template<class Word>
bool Embeddings<Word>::has(const Word& word) const {
    return word_map_.find(word) != word_map_.end();
}

template<class Word>
void Embeddings<Word>::save(const std::string& fname) const {
    std::string message("Writing embeddings to `" + fname + "`\n");
    logging::log(message.c_str());

    auto* out = io::open_out_file(fname);

    io::write_header(word_map_.size(), dimension_, out);

    for (const auto& word_embedding : *this) {
        io::write_word(word_embedding.first, out);
        io::write_embedding(word_embedding.second, out);
    }

    logging::log("- saved %lu embeddings\n", word_map_.size());
    logging::log("- file size %dMB\n", io::estimate_file_size_mb(fname));

    io::close_file(out);
}

bool print_it(const std::string& w) {
    return false;
}

bool print_it(Id w) {
    return w == 205135;
}

template<class Word>
void Embeddings<Word>::load(const std::string& fname) {
    std::string message("Loading embeddings from `" + fname + "`\n");
    logging::log(message.c_str());

    auto* in = io::open_in_file(fname);

    size_t size;
    int dimension;
    io::read_header(in, size, dimension);

    dimension_ = dimension;
    word_embeddings_.resize(size * dimension);

    Word word;
    Embedding embedding;
    for (size_t index = 0; index < size; ++index) {
        io::read_word(in, word);
        word_map_[word] = index;

        io::read_embedding(in, dimension, embedding);
        std::copy(
            embedding.begin(),
            embedding.end(),
            word_embeddings_.begin() + index * dimension_);
    }

    logging::log("- loaded %lu embeddings\n", size);

    io::close_file(in);
}

template<class Word>
std::vector<Word> Embeddings<Word>::words() const {
    std::vector<Word> words;
    words.reserve(word_map_.size());
    for (const auto& w_i : word_map_) {
        words.push_back(w_i.first);
    }
    return words;
}


} // namespace emb
