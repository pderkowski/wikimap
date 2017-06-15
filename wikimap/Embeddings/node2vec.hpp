#pragma once

#include <vector>

#include "defs.hpp"
#include "word2vec.hpp"
#include "Graph/graph.hpp"
#include "vector_ops.hpp"
#include "utils.hpp"
#include "corpus.hpp"


namespace emb {


struct N2VSettings {
    Float backtrack_probability;
    int walk_length;
    int walks_per_node;
    int dimension;
    int epochs;
    Float starting_learning_rate;
    int context_size;
    bool dynamic_context;
    int negative_samples;
    Float subsampling_factor;
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
    Node2Vec(
        Float backtrack_probability = def::BACKTRACK_PROBABILITY,
        int walk_length = def::WALK_LENGTH,
        int walks_per_node = def::WALKS_PER_NODE,
        int dimension = def::DIMENSION,
        int epochs = def::EPOCHS,
        Float learning_rate = def::LEARNING_RATE,
        int context_size = def::CONTEXT_SIZE,
        bool dynamic_context = def::DYNAMIC_CONTEXT,
        int negative_samples = def::NEGATIVE_SAMPLES,
        bool verbose = def::VERBOSE,
        Float subsampling_factor = def::SUMBSAMPLING_FACTOR);

    template<class Container>
    Embeddings<Id> learn_embeddings(const Container& edges) const;

    template<class Iterator>
    Embeddings<Id> learn_embeddings(Iterator begin, Iterator end) const;

    N2VSettings settings;

private:
    static const int BATCH_SIZE = 1000;

    template<class Iterator>
    Graph<Id> read_graph(Iterator begin, Iterator end) const;
};


class WalkGenerator {
public:
    typedef std::vector<Id> Walk;
    typedef std::pair<Id, bool> OptionalNode;

    WalkGenerator(const Graph<Id>& graph, const N2VSettings& settings);

    Walk generate(Int index, Int seed) const;

private:
    OptionalNode select_next_node(const Walk& walk) const;

    const Graph<Id>& graph_;
    N2VSettings settings_;
    mutable Random random_;
};


Node2Vec::Node2Vec(Float backtrack_probability, int walk_length,
        int walks_per_node, int dimension, int epochs, Float learning_rate,
        int context_size, bool dynamic_context, int negative_samples,
        bool verbose, Float subsampling_factor) {

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

    auto graph = read_graph(begin, end);
    auto walk_count = graph.node_count() * settings.walks_per_node;
    WalkGenerator generator(graph, settings);
    GeneratingCorpus<Id> corpus([&generator] (Int index, Int seed) {
        return generator.generate(index, seed);
    }, walk_count);
    w2v.train(corpus);

    return w2v.get_embeddings();
}

template<class Iterator>
Graph<Id> Node2Vec::read_graph(Iterator begin, Iterator end) const {
    Graph<Id> graph;

    if (settings.verbose) { logging::log("Reading graph\n"); }

    std::for_each(begin, end, [this, &graph] (const Edge& e) {
        graph.checked_add_edge(e.first, e.second);
    });

    if (settings.verbose) {
        logging::log("- nodes: %lld\n", graph.node_count());
        logging::log("- edges: %lld\n", graph.edge_count());
    }

    return graph;
}


WalkGenerator::WalkGenerator(
        const Graph<Id>& graph,
        const N2VSettings& settings)
:   graph_(graph), settings_(settings)
{ }

WalkGenerator::Walk WalkGenerator::generate(Int index, Int seed) const {
    random_.seed(seed);

    Id start = graph_.get_nodes()[index % graph_.node_count()];
    Walk walk;

    if (settings_.walk_length > 0) {
        walk.push_back(start);
    }

    while (walk.size() < static_cast<size_t>(settings_.walk_length)) {
        auto optional_next = select_next_node(walk);
        if (optional_next.second) {
            walk.push_back(optional_next.first);
        } else {
            break;
        }
    }

    return walk;
}

WalkGenerator::OptionalNode WalkGenerator::select_next_node(
        const Walk& walk) const {

    static std::uniform_real_distribution<> dist;
    auto& rng = random_.rng();

    if (walk.size() == 1) {
        auto last = walk[0];
        if (graph_.has_neighbor(last)) {
            return std::make_pair(
                graph_.get_random_neighbor(last, rng),
                true);
        } else {
            return std::make_pair(-1, false);
        }
    } else {
        auto last = walk[walk.size() - 1];
        auto last_last = walk[walk.size() - 2];

        auto sample = dist(rng);
        if (sample >= settings_.backtrack_probability) {
            if (graph_.has_neighbor(last)) {
                return std::make_pair(
                    graph_.get_random_neighbor(last, rng),
                    true);
            } else {
                return std::make_pair(-1, false);
            }
        } else {
            if (graph_.has_neighbor(last_last)) {
                return std::make_pair(
                    graph_.get_random_neighbor(last_last, rng),
                    true);
            } else {
                return std::make_pair(-1, false);
            }
        }
    }
}


} // namespace emb
