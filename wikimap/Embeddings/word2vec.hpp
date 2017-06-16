#pragma once

#include <vector>
#include <algorithm>
#include <tuple>
#include <random>
#include <stdexcept>

#include <omp.h>

#include "defs.hpp"
#include "model.hpp"
#include "utils.hpp"
#include "math.hpp"
#include "logging.hpp"
#include "vocab.hpp"
#include "parallel.hpp"


namespace emb {


template<class Word>
class Training;


struct W2VSettings {
    int dimension;
    int epochs;
    Float starting_learning_rate;
    int context_size;
    bool dynamic_context;
    int negative_samples;
    Float subsampling_factor;
    bool verbose;
};

template<class Word = std::string>
class Word2Vec {
public:
    typedef Word value_type;

    class iterator {
    public:
        typedef ptrdiff_t difference_type;
        typedef std::pair<Word, Embedding> value_type;
        typedef const value_type& reference;
        typedef const value_type* pointer;
        typedef std::input_iterator_tag iterator_category;

    public:
        iterator(
                const Word2Vec<Word>* parent,
                typename Vocab<Word>::const_iterator word_iterator)
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
            auto word = *word_iterator_;
            auto word_id = parent_->vocab_.get_id(word);
            auto embedding = static_cast<Embedding>(
                parent_->model_.word_embedding(word_id));
            return std::make_pair(word, embedding);
        }

        const Word2Vec<Word>* parent_;
        typename Vocab<Word>::const_iterator word_iterator_;
        mutable value_type value_;
    };

public:
    Word2Vec(
        int dimension = def::DIMENSION,
        int epochs = def::EPOCHS,
        Float learning_rate = def::LEARNING_RATE,
        int context_size = def::CONTEXT_SIZE,
        bool dynamic_context = def::DYNAMIC_CONTEXT,
        int negative_samples = def::NEGATIVE_SAMPLES,
        bool verbose = def::VERBOSE,
        Float subsampling_factor = def::SUMBSAMPLING_FACTOR);

    explicit Word2Vec(const W2VSettings& settings);

    iterator begin() const;
    iterator end() const;

    // Use this in a simple case, when you just want to put in some sentences
    // and get embeddings.
    //
    // Just call train once.
    //
    template<class Corpus>
    void train(const Corpus& corpus);

    // Use this when you want to split training into multiple stages.
    // Remember to do the following:
    //
    // 1. init_training
    // 2. train_some (possibly many times)
    // 3. finish_training

    template<class Corpus>
    void init_training(const Corpus& corpus);

    template<class Corpus>
    void train_some(const Corpus& corpus, Int total_expected_sentences);

    void finish_training();

    Embeddings<Word> get_embeddings() const;

private:
    template<class Corpus>
    void learn_vocab(const Corpus& corpus);

    void resize_model();
    void init_model();
    void set_unigram_distribution();

    void normalize_model();

public:
    W2VSettings settings;

private:
    Vocab<Word> vocab_;
    Model model_;
    Training<Word> training_;
};

template<class Word>
Word2Vec<Word>::Word2Vec(int dimension, int epochs, Float learning_rate,
            int context_size, bool dynamic_context, int negative_samples,
            bool verbose, Float subsampling_factor)

:       settings(), vocab_(), model_(), training_(settings, vocab_, model_) {

    settings.dimension = dimension;
    settings.epochs = epochs;
    settings.starting_learning_rate = learning_rate;
    settings.context_size = context_size;
    settings.dynamic_context = dynamic_context;
    settings.negative_samples = negative_samples;
    settings.subsampling_factor = subsampling_factor;
    settings.verbose = verbose;
}

template<class Word>
Word2Vec<Word>::Word2Vec(const W2VSettings& stgs)
:   settings(stgs), vocab_(), model_(), training_(settings, vocab_, model_)
{ }

template<class Word>
Embeddings<Word> Word2Vec<Word>::get_embeddings() const {
    Embeddings<Word> embeddings;
    for (const auto& word : vocab_) {
        embeddings[word] = static_cast<Embedding>(
            model_.word_embedding(vocab_.get_id(word)));
    }
    return embeddings;
}

template<class Word>
template<class Corpus>
void Word2Vec<Word>::train(const Corpus& corpus) {
    init_training(corpus);
    train_some(corpus, corpus.sentence_count());
    finish_training();
}

template<class Word>
typename Word2Vec<Word>::iterator Word2Vec<Word>::begin() const {
    return iterator(this, vocab_.begin());
}

template<class Word>
typename Word2Vec<Word>::iterator Word2Vec<Word>::end() const {
    return iterator(this, vocab_.end());
}

template<class Word>
template<class Corpus>
void Word2Vec<Word>::init_training(const Corpus& corpus) {
    learn_vocab(corpus);
    resize_model();
    init_model();
    set_unigram_distribution();
}

template<class Word>
template<class Corpus>
void Word2Vec<Word>::train_some(
        const Corpus& corpus,
        Int total_expected_sentences) {

    if (settings.verbose) {
        logging::log("Starting new training session\n");
        logging::log("- corpus size (sentences): %lld\n", corpus.sentence_count());
        logging::log("- epochs: %d\n", settings.epochs);
    }
    training_.train(corpus, settings.epochs * total_expected_sentences);
}

template<class Word>
void Word2Vec<Word>::finish_training() {
    normalize_model();
}

template<class Word>
template<class Corpus>
void Word2Vec<Word>::learn_vocab(const Corpus& corpus) {
    if (settings.verbose) {
        logging::log("Learning vocabulary\n");
        logging::log("- sentences in corpus: %lld\n", corpus.sentence_count());
    }

    auto word_counts = parallel::WordCount<Corpus>(corpus);

    for (const auto& w_c : word_counts) {
        vocab_.add(w_c.first, w_c.second);
    }

    if (settings.verbose) {
        logging::log("- words in vocab: %lld\n", vocab_.size());
    }
}


template<class Word>
void Word2Vec<Word>::resize_model() {
    Int rows = vocab_.size();
    Int cols = settings.dimension;

    if (settings.verbose) {
        logging::log("Allocating model\n");
        logging::log("- model dimensions: [2 x %d x %d]\n", rows, cols);
        logging::log("- estimated size: %dMB\n", model_.estimate_size_mb(
            rows,
            cols));
    }

    try {
        model_.resize(rows, cols);
    } catch (const std::bad_alloc& e) {
        logging::log("ERROR: not enough memory for model allocation.");
        exit(1);
    }
}


template<class Word>
void Word2Vec<Word>::init_model() {
    if (settings.verbose) { logging::log("Initializing model\n"); }
    model_.init();
}

template<class Word>
void Word2Vec<Word>::set_unigram_distribution() {
    if (settings.verbose) { logging::log("Setting unigram distribution\n"); }
    vocab_.init_sampling(settings.subsampling_factor);
}

template<class Word>
void Word2Vec<Word>::normalize_model() {
    if (settings.verbose) { logging::log("Normalizing model\n"); }
    model_.normalize();
}

template<class Word>
class Training {
public:
    Training(
        const W2VSettings& settings,
        const Vocab<Word>& vocab,
        Model& model);

    template<class Corpus>
    void train(const Corpus& corpus, Int expected_sentences);

private:
    template<class Sentence>
    void train_on_sequence(const Sentence& sentence, Float learning_rate);

    Float get_learning_rate(Int expected_sentences) const;
    Float get_progress_rate(Int expected_sentences) const;

    Float get_gradient_for_positive_sample(Id word, Id context) const;
    Float get_gradient_for_negative_sample(Id word, Id context) const;

    int get_context_size() const;

    static const int BATCH_SIZE = 100;
    static constexpr const char* progress_str =
        "* Progress: %6.2f%%    Learning rate: %10.8f%%";

    const W2VSettings& stg_;
    const Vocab<Word>& vocab_;
    Model& model_;

    // This is a member, to keep its value between possible multiple calls to
    // train()
    Int processed_sentences_;
};

template<class Word>
Training<Word>::Training(
        const W2VSettings& settings,
        const Vocab<Word>& vocab,
        Model& model)
:   stg_(settings), vocab_(vocab), model_(model), processed_sentences_(0)
{ }

template<class Word>
template<class Corpus>
void Training<Word>::train(const Corpus& corpus, Int expected_sentences) {
    for (int epoch = 0; epoch < stg_.epochs; ++epoch) {
        #pragma omp parallel for schedule(dynamic, BATCH_SIZE)
        for (Int index = 0; index < corpus.sentence_count(); ++index) {
            auto learning_rate = get_learning_rate(expected_sentences);

            // only master thread reports progress
            if (    omp_get_thread_num() == 0
                    && stg_.verbose
                    && logging::time_since_last_log() > 0.1) {

                auto progress_rate = get_progress_rate(expected_sentences);
                logging::inline_log(progress_str, progress_rate, learning_rate);
            }

            train_on_sequence(corpus.get_sentence(index), learning_rate);

            #pragma omp atomic
            processed_sentences_ += 1;
        }
    }

    if (stg_.verbose) {
        auto learning_rate = get_learning_rate(expected_sentences);
        logging::inline_log(progress_str, 100., learning_rate);
        logging::newline();
    }
}

template<class Word>
template<class Sentence>
void Training<Word>::train_on_sequence(
        const Sentence& sentence,
        Float learning_rate) {

    auto start = sentence.begin();
    auto end = sentence.end();

    const auto size = end - start;
    if (size < 2) { return; } // nothing to do

    Embedding word_embedding_delta(stg_.dimension, 0);

    for (int word_pos = 0; word_pos < size; ++word_pos) {
        auto word = vocab_.get_id(start[word_pos]);
        // context_size may be vary if -dynamic is on
        auto context_size = get_context_size();

        for (int offset = -context_size; offset <= context_size; ++offset) {
            int context_pos = word_pos + offset;
            if (offset == 0 || context_pos < 0 || context_pos >= size) {
                continue;
            }

            vec::fill_with_zeros(word_embedding_delta);

            auto context = vocab_.get_id(start[context_pos]);
            auto gradient =
                get_gradient_for_positive_sample(word, context)
                * learning_rate;

            vec::add_to(
                word_embedding_delta,
                model_.context_embedding(context) * gradient);
            vec::add_to(
                model_.context_embedding(context),
                model_.word_embedding(word) * gradient);

            for (int j = 0; j < stg_.negative_samples; ++j) {
                auto context = vocab_.sample(Random::global_rng());

                if (word == context) { continue; }

                Float gradient =
                    get_gradient_for_negative_sample(word, context)
                    * learning_rate;

                vec::add_to(
                    word_embedding_delta,
                    model_.context_embedding(context) * gradient);
                vec::add_to(
                    model_.context_embedding(context),
                    model_.word_embedding(word) * gradient);
            }

            vec::add_to(model_.word_embedding(word), word_embedding_delta);
        }
    }
}

template<class Word>
inline Float Training<Word>::get_learning_rate(Int expected_sentences) const {
    Float coef = std::max(
        1.0f - processed_sentences_ / (expected_sentences + 1.0f),
        0.0001f);
    return coef * stg_.starting_learning_rate;
}

template<class Word>
inline Float Training<Word>::get_progress_rate(Int expected_sentences) const {
    return processed_sentences_ * 100.0 / expected_sentences;
}

template<class Word>
inline Float Training<Word>::get_gradient_for_positive_sample(
        Id word,
        Id context) const {

    auto product = vec::dot_product(
        model_.word_embedding(word),
        model_.context_embedding(context));
    return 1.0f - math::sigmoid(product);
}

template<class Word>
inline Float Training<Word>::get_gradient_for_negative_sample(
        Id word,
        Id context) const {

    auto product = vec::dot_product(
        model_.word_embedding(word),
        model_.context_embedding(context));
    return math::sigmoid(-product) - 1.0f;
}

template<class Word>
inline int Training<Word>::get_context_size() const {
    static std::uniform_int_distribution<int> dist(1, stg_.context_size);
    return stg_.dynamic_context ?
        dist(Random::global_rng())
        : stg_.context_size;
}


} // namespace emb
