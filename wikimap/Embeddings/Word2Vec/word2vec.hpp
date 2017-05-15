#pragma once

#include <vector>
#include <unordered_map>
#include <algorithm>
#include <tuple>
#include <random>

#include <omp.h>

#include "defs.hpp"
#include "corpus.hpp"
#include "model.hpp"
#include "utils.hpp"
#include "sigmoid.hpp"


namespace w2v {


template<class Word = std::string>
class Word2Vec {
public:
    typedef std::vector<Word> Sentence;

public:
    Word2Vec(int dimension = 100, int epochs = 1, double learning_rate = 0.025,
        int context_size = 5, bool dynamic_context = true,
        int negative_samples = 5, double subsampling_factor = 0.75,
        bool verbose = true);

    template<class Iterator>
    void learn_embeddings(Iterator begin, Iterator end);
    void learn_embeddings(const std::vector<Sentence>& sentences);

private:
    void reset();

    void init_model();
    void train_model();
    void normalize_model();

    template<class Iterator>
    void prepare_training_data(Iterator begin, Iterator end);
    void process_sentence(const Sentence& sentence);

    void train_on_sequence(
        const SequenceIterator& seq_start,
        const SequenceIterator& seq_end,
        double learning_rate);

    double get_learning_rate(Int words_seen, Int words_expected) const;
    double get_gradient_for_positive_sample(Token word, Token context) const;
    double get_gradient_for_negative_sample(Token word, Token context) const;
    int get_context_size() const;

private:
    static const int BATCH_SIZE = 50;

    const int dimension_;
    const int epochs_;
    const double starting_learning_rate_;
    const int context_size_;
    const bool dynamic_context_;
    const int negative_samples_;
    const double subsampling_factor_;
    const bool verbose_;

    Vocabulary<Word> vocab_;
    Corpus corpus_;
    Model model_;
};


template<class Word>
Word2Vec<Word>::Word2Vec(int dimension, int epochs, double learning_rate,
        int context_size, bool dynamic_context, int negative_samples,
        double subsampling_factor, bool verbose)
:   dimension_(dimension), epochs_(epochs), starting_learning_rate_(learning_rate),
    context_size_(context_size), dynamic_context_(dynamic_context),
    negative_samples_(negative_samples), verbose_(verbose),
    subsampling_factor_(subsampling_factor), vocab_(), corpus_(), model_()
{ }

template<class Word>
template<class Iterator>
void Word2Vec<Word>::learn_embeddings(Iterator begin, Iterator end) {
    reset();
    prepare_training_data(begin, end);
    init_model();
    train_model();
    normalize_model();
}

template<class Word>
void Word2Vec<Word>::learn_embeddings(const std::vector<Sentence>& sentences) {
    learn_embeddings(sentences.begin(), sentences.end());
}

template<class Word>
void Word2Vec<Word>::reset() {
    vocab_.reset();
    corpus_.reset();
    model_ = Model();
}

template<class Word>
template<class Iterator>
void Word2Vec<Word>::prepare_training_data(Iterator begin, Iterator end) {
    if (verbose_) { w2v::log("Preparing training data...\n"); }

    std::for_each(begin, end, [this] (const Sentence& s) {
        process_sentence(s);
    });
    vocab_.set_unigram_distribution(subsampling_factor_);
}

template<class Word>
void Word2Vec<Word>::process_sentence(const Sentence& sentence) {
    for (const auto& word : sentence) {
        vocab_.add(word);
        auto token = vocab_.get_token(word);
        corpus_.add_token(token);
    }
    corpus_.end_sequence();
}

template<class Word>
void Word2Vec<Word>::init_model() {
    if (verbose_) { w2v::log("Initializing model...\n"); }
    model_ = Model(vocab_.size(), dimension_);
}

template<class Word>
void Word2Vec<Word>::train_model() {
    if (verbose_) { w2v::log("Training model...\n"); }

    Int words_seen = 0;
    Int words_expected = corpus_.size() * epochs_;

    for (int epoch = 0; epoch < epochs_; ++epoch) {
        if (verbose_) {
            w2v::log("\rStarting epoch (%d/%d).\n", epoch + 1, epochs_);
            report_progress(words_seen, words_expected);
        }

        #pragma omp parallel for schedule(static, BATCH_SIZE)
        for (Int index = 0; index < corpus_.sequence_count(); ++index) {
            // only master thread reports progress
            if (omp_get_thread_num() == 0 && verbose_) {
                report_progress(words_seen, words_expected);
            }

            auto learning_rate = get_learning_rate(words_seen, words_expected);

            SequenceIterator seq_start, seq_end;
            std::tie(seq_start, seq_end) = corpus_.get_sequence(index);

            train_on_sequence(seq_start, seq_end, learning_rate);

            #pragma omp atomic
            words_seen += (seq_end - seq_start);
        }
    }

    if (verbose_) { w2v::log("\rProgress: 100.00%% \n"); }
}

template<class Word>
void Word2Vec<Word>::train_on_sequence(
        const SequenceIterator& seq_start,
        const SequenceIterator& seq_end,
        double learning_rate) {

    const auto seq_size = seq_end - seq_start;
    Embedding word_embedding_delta(dimension_, 0);

    for (int word_pos = 0; word_pos < seq_size; ++word_pos) {
        auto word = seq_start[word_pos];
        auto context_size = get_context_size();

        for (int offset = -context_size; offset <= context_size_; ++offset) {
            int context_pos = word_pos + offset;
            if (offset == 0 || context_pos < 0 || context_pos >= seq_size) {
                continue;
            }

            vec::fill_with_zeros(word_embedding_delta);

            auto context = seq_start[context_pos];
            auto gradient = get_gradient_for_positive_sample(word, context);
            gradient *= learning_rate;
            vec::add_to(
                word_embedding_delta,
                model_.context_embedding(context) * gradient);
            vec::add_to(
                model_.context_embedding(context),
                model_.word_embedding(word) * gradient);

            for (int j = 0; j < negative_samples_; ++j) {
                auto context = vocab_.sample(Random::get());
                if (word == context) { continue; }

                double gradient = compute_negative_gradient(word, context);
                gradient *= learning_rate;
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
void Word2Vec<Word>::normalize_model() {
    if (verbose_) { w2v::log("Normalizing model...\n"); }
    model_.normalize();
}

template<class Word>
inline double Word2Vec<Word>::get_learning_rate(
        Int words_seen,
        Int words_expected) const {

    double coef = std::max(1. - words_seen / (words_expected + 1.), 0.0001);
    return coef * starting_learning_rate_;
}

template<class Word>
inline double Word2Vec<Word>::get_gradient_for_positive_sample(
        Token word,
        Token context) const {

    auto product = vec::dot_product(
        model_.word_embedding(word),
        model_.context_embedding(context));
    return 1. - sigmoid(product);
}

template<class Word>
inline double Word2Vec<Word>::get_gradient_for_negative_sample(
        Token word,
        Token context) const {

    auto product = vec::dot_product(
        model_.word_embedding(word),
        model_.context_embedding(context));
    return sigmoid(-product) - 1.;
}

template<class Word>
inline int Word2Vec<Word>::get_context_size() const {
    static std::uniform_int_distribution<int> dist(1, context_size_);
    return dynamic_context_? dist(Random::get()) : context_size_;
}


}
