#pragma once

#include <vector>
#include <algorithm>
#include <tuple>
#include <random>

#include <omp.h>

#include "defs.hpp"
#include "corpus.hpp"
#include "model.hpp"
#include "utils.hpp"
#include "math.hpp"
#include "logging.hpp"


namespace w2v {


struct Settings {
    int dimension;
    int epochs;
    double starting_learning_rate;
    int context_size;
    bool dynamic_context;
    int negative_samples;
    double subsampling_factor;
    bool verbose;
};

template<class Word = std::string>
class Word2Vec {
public:
    typedef std::vector<Word> Sentence;

public:
    Word2Vec(
        int dimension = def::DIMENSION,
        int epochs = def::EPOCHS,
        double learning_rate = def::LEARNING_RATE,
        int context_size = def::CONTEXT_SIZE,
        bool dynamic_context = def::DYNAMIC_CONTEXT,
        int negative_samples = def::NEGATIVE_SAMPLES,
        bool verbose = def::VERBOSE,
        double subsampling_factor = def::SUMBSAMPLING_FACTOR);

    template<class Container>
    Embeddings<Word> learn_embeddings(const Container& sentences) const;

    template<class Iterator>
    Embeddings<Word> learn_embeddings(Iterator begin, Iterator end) const;

    Settings settings;

private:
    template<class Iterator>
    void process_training_data(
        Iterator begin,
        Iterator end,
        Vocabulary<Word>& vocab,
        Corpus& corpus) const;

    void process_sentence(
        const Sentence& sentence,
        Vocabulary<Word>& vocab,
        Corpus& corpus) const;
};

class Training {
public:
    Training(const Settings& settings, const Corpus& corpus, Model& model);

    void init_model();
    void train_model();
    void normalize_model();

private:
    void train_on_sequence(
        const SequenceIterator& seq_start,
        const SequenceIterator& seq_end,
        double learning_rate);

    double get_learning_rate(Int words_seen, Int words_expected) const;
    double get_gradient_for_positive_sample(Id word, Id context) const;
    double get_gradient_for_negative_sample(Id word, Id context) const;
    int get_context_size() const;

    static const int BATCH_SIZE = 50;

    const Settings& stg_;
    const Corpus& corpus_;
    Model& model_;
};


template<class Word>
Embeddings<Word> get_embeddings_from_model(
        const Vocabulary<Word>& vocab,
        const Model& model) {

    Embeddings<Word> embeddings;
    for (const auto& word : vocab) {
        embeddings[word] = static_cast<Embedding>(
            model.word_embedding(vocab.get_id(word)));
    }
    return embeddings;
}


template<class Word>
Word2Vec<Word>::Word2Vec(int dimension, int epochs, double learning_rate,
        int context_size, bool dynamic_context, int negative_samples,
        bool verbose, double subsampling_factor) {

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
template<class Container>
Embeddings<Word> Word2Vec<Word>::learn_embeddings(
        const Container& sentences) const {

    return learn_embeddings(sentences.begin(), sentences.end());
}

template<class Word>
template<class Iterator>
Embeddings<Word> Word2Vec<Word>::learn_embeddings(
        Iterator begin,
        Iterator end) const {

    Vocabulary<Word> vocab;
    Corpus corpus;
    process_training_data(begin, end, vocab, corpus);

    Model model(vocab.size(), settings.dimension);

    Training training(settings, corpus, model);
    training.init_model();
    training.train_model();
    training.normalize_model();

    return get_embeddings_from_model(vocab, model);
}

template<class Word>
template<class Iterator>
void Word2Vec<Word>::process_training_data(
        Iterator begin,
        Iterator end,
        Vocabulary<Word>& vocab,
        Corpus& corpus) const {

    if (settings.verbose) { logging::log("Preparing training data\n"); }

    std::for_each(begin, end, [this, &vocab, &corpus] (const Sentence& s) {
        process_sentence(s, vocab, corpus);
    });

    if (settings.verbose) {
        logging::log("- sentences: %lld\n", corpus.sequence_count());
        logging::log("- words: %lld\n", corpus.size());
        logging::log("- unique words: %lld\n", vocab.size());
    }

    corpus.set_unigram_distribution(settings.subsampling_factor);
}

template<class Word>
void Word2Vec<Word>::process_sentence(
        const Sentence& sentence,
        Vocabulary<Word>& vocab,
        Corpus& corpus) const {

    for (const auto& word : sentence) {
        vocab.add(word);
        auto id = vocab.get_id(word);
        corpus.add_token(id);
    }
    corpus.end_sequence();
}


Training::Training(const Settings& settings, const Corpus& corpus, Model& model)
:   stg_(settings), corpus_(corpus), model_(model)
{ }

void Training::init_model() {
    if (stg_.verbose) {
        logging::log("Initializing model\n");
        logging::log(
            "- model dimensions: [2 x %d x %d]\n",
            model_.rows(),
            model_.cols());
        logging::log("- estimated size: %dMB\n", model_.estimate_size_mb());
        model_.init();
    }
}

void Training::train_model() {
    if (stg_.verbose) { logging::log("Training model\n"); }

    Int words_seen = 0;
    Int words_expected = corpus_.size() * stg_.epochs;

    for (int epoch = 0; epoch < stg_.epochs; ++epoch) {
        if (stg_.verbose) {
            logging::inline_log(
                "- Starting epoch (%d/%d)\n",
                epoch + 1,
                stg_.epochs);
            logging::inline_log(
                "* Progress: %.2f%%  ",
                words_seen * 100. / words_expected);
        }

        #pragma omp parallel for schedule(dynamic, BATCH_SIZE)
        for (Int index = 0; index < corpus_.sequence_count(); ++index) {
            // only master thread reports progress
            if (    omp_get_thread_num() == 0
                    && stg_.verbose
                    && logging::time_since_last_log() > 0.1) {

                logging::inline_log(
                    "* Progress: %.2f%%  ",
                    words_seen * 100. / words_expected);
            }

            auto learning_rate = get_learning_rate(words_seen, words_expected);

            SequenceIterator seq_start, seq_end;
            std::tie(seq_start, seq_end) = corpus_.get_sequence(index);

            train_on_sequence(seq_start, seq_end, learning_rate);

            #pragma omp atomic
            words_seen += (seq_end - seq_start);
        }
    }

    if (stg_.verbose) { logging::inline_log("- Progress: 100.00%% \n"); }
}

void Training::normalize_model() {
    if (stg_.verbose) { logging::log("Normalizing model\n"); }
    model_.normalize();
}

void Training::train_on_sequence(
        const SequenceIterator& seq_start,
        const SequenceIterator& seq_end,
        double learning_rate) {

    const auto seq_size = seq_end - seq_start;
    if (seq_size < 2) { return; } // nothing to do

    Embedding word_embedding_delta(stg_.dimension, 0);

    for (int word_pos = 0; word_pos < seq_size; ++word_pos) {
        auto word = seq_start[word_pos];
        // context_size may be vary if -dynamic is on
        auto context_size = get_context_size();

        for (int offset = -context_size; offset <= context_size; ++offset) {
            int context_pos = word_pos + offset;
            if (offset == 0 || context_pos < 0 || context_pos >= seq_size) {
                continue;
            }

            vec::fill_with_zeros(word_embedding_delta);

            auto context = seq_start[context_pos];
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
                auto context = corpus_.sample();
                if (word == context) { continue; }

                double gradient =
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

inline double Training::get_learning_rate(
        Int words_seen,
        Int words_expected) const {

    double coef = std::max(1. - words_seen / (words_expected + 1.), 0.0001);
    return coef * stg_.starting_learning_rate;
}

inline double Training::get_gradient_for_positive_sample(
        Id word,
        Id context) const {

    auto product = vec::dot_product(
        model_.word_embedding(word),
        model_.context_embedding(context));
    return 1. - math::sigmoid(product);
}

inline double Training::get_gradient_for_negative_sample(
        Id word,
        Id context) const {

    auto product = vec::dot_product(
        model_.word_embedding(word),
        model_.context_embedding(context));
    return math::sigmoid(-product) - 1.;
}

inline int Training::get_context_size() const {
    static std::uniform_int_distribution<int> dist(1, stg_.context_size);
    return stg_.dynamic_context ? dist(Random::get()) : stg_.context_size;
}


} // namespace w2v
