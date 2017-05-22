#pragma once

#include <vector>

#include "defs.hpp"
#include "word2vec.hpp"
#include "graph.hpp"
#include "vector_ops.hpp"
#include "utils.hpp"


namespace emb {


struct N2VSettings {
    double backtrack_probability;
    int walk_length;
    int walks_per_node;
    int dimension;
    int epochs;
    double starting_learning_rate;
    int context_size;
    bool dynamic_context;
    int negative_samples;
    double subsampling_factor;
    bool verbose;

    operator W2VSettings() const {
        W2VSettings res;
        res.dimension = dimension;
        res.epochs = epochs;
        res.starting_learning_rate = starting_learning_rate;
        res.context_size = context_size;
        res.dynamic_context = dynamic_context;
        res.negative_samples = negative_samples;
        res.subsampling_factor = subsampling_factor;
        res.verbose = verbose;
        return res;
    }
};


class Node2Vec {
public:
    typedef std::vector<std::vector<Id>> RandomWalks;

public:
    Node2Vec(
        double backtrack_probability = def::BACKTRACK_PROBABILITY,
        int walk_length = def::WALK_LENGTH,
        int walks_per_node = def::WALKS_PER_NODE,
        int dimension = def::DIMENSION,
        int epochs = def::EPOCHS,
        double learning_rate = def::LEARNING_RATE,
        int context_size = def::CONTEXT_SIZE,
        bool dynamic_context = def::DYNAMIC_CONTEXT,
        int negative_samples = def::NEGATIVE_SAMPLES,
        bool verbose = def::VERBOSE,
        double subsampling_factor = def::SUMBSAMPLING_FACTOR);

    template<class Container>
    Embeddings<Id> learn_embeddings(const Container& edges) const;

    template<class Iterator>
    Embeddings<Id> learn_embeddings(Iterator begin, Iterator end) const;

    N2VSettings settings;

private:
    static const int BATCH_SIZE = 1000;

    template<class Iterator>
    Graph<Id> read_graph(Iterator begin, Iterator end) const;

    RandomWalks generate_random_walks(const Graph<Id>& graph) const;
    void shuffle_walks(RandomWalks& walks) const;
};

class WalkGenerator {
public:
    typedef Random::Rng Rng;
    typedef std::vector<Id> Walk;
    typedef std::pair<Id, bool> OptionalNode;

    WalkGenerator(const Graph<Id>& graph, const N2VSettings& settings);

    Walk generate(Id start, Rng& rng) const;

private:
    OptionalNode select_next_node(const Walk& walk, Rng& rng) const;

    const Graph<Id>& graph_;
    N2VSettings settings_;
};

WalkGenerator::WalkGenerator(
        const Graph<Id>& graph,
        const N2VSettings& settings)
:   graph_(graph), settings_(settings)
{ }

WalkGenerator::Walk WalkGenerator::generate(Id start, Rng& rng) const {
    Walk walk;

    if (settings_.walk_length > 0) {
        walk.push_back(start);
    }

    while (walk.size() < static_cast<size_t>(settings_.walk_length)) {
        auto optional_next = select_next_node(walk, rng);
        if (optional_next.second) {
            walk.push_back(optional_next.first);
        } else {
            break;
        }
    }

    return walk;
}

WalkGenerator::OptionalNode WalkGenerator::select_next_node(
        const Walk& walk,
        Rng& rng) const {

    static std::uniform_real_distribution<> dist;

    if (walk.size() == 1) {
        auto last = walk[0];
        if (graph_.has_neighbor(last)) {
            return std::make_pair(graph_.get_random_neighbor(last, rng), true);
        } else {
            return std::make_pair(-1, false);
        }
    } else {
        auto last = walk[walk.size() - 1];
        auto last_last = walk[walk.size() - 2];

        auto sample = dist(rng);
        if (sample >= settings_.backtrack_probability) {
            if (graph_.has_neighbor(last)) {
                return std::make_pair(graph_.get_random_neighbor(last, rng), true);
            } else {
                return std::make_pair(-1, false);
            }
        } else {
            if (graph_.has_neighbor(last_last)) {
                return std::make_pair(graph_.get_random_neighbor(last_last, rng), true);
            } else {
                return std::make_pair(-1, false);
            }
        }
    }
}


Node2Vec::Node2Vec(double backtrack_probability, int walk_length,
        int walks_per_node, int dimension, int epochs, double learning_rate,
        int context_size, bool dynamic_context, int negative_samples,
        bool verbose, double subsampling_factor) {

    settings.backtrack_probability = backtrack_probability;
    settings.walk_length = walk_length;
    settings.walks_per_node = walks_per_node;
    settings.dimension = dimension;
    settings.epochs = epochs;
    settings.starting_learning_rate = learning_rate;
    settings.context_size = context_size;
    settings.dynamic_context = dynamic_context;
    settings.negative_samples = negative_samples;
    settings.verbose = verbose;
    settings.subsampling_factor = subsampling_factor;
}

template<class Container>
Embeddings<Id> Node2Vec::learn_embeddings(const Container& edges) const {
    return learn_embeddings(edges.begin(), edges.end());
}

template<class Iterator>
Embeddings<Id> Node2Vec::learn_embeddings(
        Iterator begin,
        Iterator end) const {

    Word2Vec<Id> w2v(settings);
    Vocabulary<Id> vocab;
    Corpus corpus;

    {
        RandomWalks walks;
        {
            auto graph = read_graph(begin, end);
            walks = generate_random_walks(graph);
            // destroy graph to preserve memory
        }
        shuffle_walks(walks);

        std::tie(vocab, corpus) = w2v.prepare_training_data(
            walks.begin(),
            walks.end());
        // destroy walks to preserve memory
    }

    return w2v.learn_embeddings(vocab, corpus);
}

template<class Iterator>
Graph<Id> Node2Vec::read_graph(Iterator begin, Iterator end) const {
    Graph<Id> graph;

    if (settings.verbose) { logging::log("Reading graph\n"); }

    std::for_each(begin, end, [this, &graph] (const Edge& e) {
        graph.add_edge(e.first, e.second);
    });

    if (settings.verbose) {
        logging::log("- nodes: %lld\n", graph.node_count());
        logging::log("- edges: %lld\n", graph.edge_count());
    }

    return graph;
}

Node2Vec::RandomWalks Node2Vec::generate_random_walks(
        const Graph<Id>& graph) const {

    Int walks_expected = graph.node_count() * settings.walks_per_node;

    RandomWalks walks(walks_expected);
    WalkGenerator generator(graph, settings);

    if (settings.verbose) {
        logging::log("Generating random walks\n");
        logging::log("- walks per node: %d\n", settings.walks_per_node);
        logging::log("- max walk length: %d\n", settings.walk_length);
        logging::log("* Progress: 0.00%%  ");
    }

    auto nodes = graph.get_nodes();

    #pragma omp parallel for schedule(dynamic, BATCH_SIZE)
    for (Int index = 0; index < walks_expected; ++index) {
        // only master thread reports progress
        if (    omp_get_thread_num() == 0
                && settings.verbose
                && logging::time_since_last_log() > 0.1) {

            logging::inline_log(
                "* Progress: %.2f%%  ",
                index * 100. / walks_expected);
        }

        auto start = nodes[index / settings.walks_per_node];
        walks[index] = generator.generate(start, Random::get());
    }

    if (settings.verbose) { logging::inline_log("- Progress: 100.00%% \n"); }

    return walks;
}

void Node2Vec::shuffle_walks(RandomWalks& walks) const {
    if (settings.verbose) {
        logging::log("Shuffling walks\n");
    }

    vec::shuffle(walks);
}


} // namespace emb
