#pragma once

#include <iomanip>
#include <utility>

#include <omp.h>

#include "graph.hpp"


template<class Graph>
class GraphSearch {
public:
    typedef typename Graph::node_type node_type;

    explicit GraphSearch(const Graph& graph);

    void bfs(const node_type& start, int max_distance);

    std::vector<node_type> reached_nodes() const;
    int distance(const node_type& node) const;

private:
    void reset();

    const Graph& graph_;
    std::vector<int> distances_;
    std::vector<InternalNode> nodes_in_max_distance_;
};

template<class Graph>
GraphSearch<Graph>::GraphSearch(const Graph& graph)
:   graph_(graph)
{ }

template<class Graph>
void GraphSearch<Graph>::bfs(const node_type& start, int max_distance) {
    reset();

    auto start_node = graph_.get_int(start);
    distances_[start_node] = 0;
    nodes_in_max_distance_.push_back(start_node);

    std::queue<decltype(start_node)> bfs_queue;
    bfs_queue.push(start_node);

    while (!bfs_queue.empty()) {
        auto current_node = bfs_queue.front();
        bfs_queue.pop();

        auto current_dist = distances_[current_node];

        if (current_dist >= max_distance) {
            break;
        } else {
            for (int e = 0; e < graph_.get_out_deg_int(current_node); ++e) {
                auto next_node = graph_.get_out_edge_int(current_node, e).to;

                if (distances_[next_node] == -1) {
                    distances_[next_node] = current_dist + 1;
                    nodes_in_max_distance_.push_back(next_node);
                    bfs_queue.push(next_node);
                }
            }
        }
    }
}

template<class Graph>
inline std::vector<typename GraphSearch<Graph>::node_type>
GraphSearch<Graph>::reached_nodes() const {
    std::vector<node_type> res(nodes_in_max_distance_.size());

    std::transform(
        nodes_in_max_distance_.begin(),
        nodes_in_max_distance_.end(),
        res.begin(),
        [this] (typename decltype(nodes_in_max_distance_)::value_type node) {
            return graph_.get_ext(node);
        });

    return res;
}

template<class Graph>
inline int GraphSearch<Graph>::distance(const node_type& node) const {
    return distances_[graph_.get_int(node)];
}

template<class Graph>
inline void GraphSearch<Graph>::reset() {
    distances_.assign(graph_.node_count(), -1);
    nodes_in_max_distance_.clear();
}


template<class Graph>
class Pagerank {
public:
    typedef typename Graph::node_type node_type;

    explicit Pagerank(
        const Graph& graph,
        bool verbose = true,
        double convergence_condition = 1e-7,
        int max_iterations = 200,
        double damping_factor = 0.85);

    void compute();

    std::vector<std::pair<typename Graph::node_type, double>>
    sorted_by_decreasing_ranks() const;

private:
    void initialize();
    double do_iteration();
    double compute_convergence(
        const std::vector<double>& old,
        const std::vector<double>& fresh) const;

private:
    const Graph& graph_;
    std::vector<double> ranks_;

public:
    bool verbose;
    double convergence_condition;
    int max_iterations;
    double damping_factor;
};

template<class Graph>
Pagerank<Graph>::Pagerank(const Graph& graph, bool verbose,
            double convergence_condition, int max_iterations,
            double damping_factor)
:       graph_(graph), verbose(verbose),
        convergence_condition(convergence_condition),
        max_iterations(max_iterations), damping_factor(damping_factor)
{ }

template<class Graph>
void Pagerank<Graph>::compute() {
    if (verbose) {
        std::cerr << "COMPUTING PAGERANK\n";
    }
    if (verbose) {
        std::cerr << "Iterating until relative change less than "
            << convergence_condition << " or max " << max_iterations
            << " iterations.\n";
    }

    initialize();

    for (int iteration = 0; ; ++iteration) {
        double convergence = do_iteration();

        if (verbose) {
            std::cerr << "Iteration " << std::setw(3) << iteration << ": ";
        }
        if (verbose) {
            std::cerr << "relative change: " << std::setprecision(3)
                << convergence << "\n";
        }

        if (convergence < convergence_condition) {
            if (verbose) {
                std::cerr << "Reached convergence, stopping.\n";
            }
            break;
        } else if (iteration >= max_iterations) {
            if (verbose) {
                std::cerr << "Reached maximum number of iterations, stopping."
                    << std::endl;
            }
            break;
        }
    }
}

template<class Graph>
std::vector<std::pair<typename Graph::node_type, double>>
Pagerank<Graph>::sorted_by_decreasing_ranks() const {
    typedef std::pair<typename Graph::node_type, double> Pair;

    std::vector<Pair> res(ranks_.size());

    for (int i = 0; i < ranks_.size(); ++i) {
        res[i] = std::make_pair(graph_.get_ext(InternalNode(i)), ranks_[i]);
    }

    std::sort(res.begin(), res.end(), [] (const Pair& lhs, const Pair& rhs) {
        return lhs.second > rhs.second;
    });

    return res;
}

template<class Graph>
void Pagerank<Graph>::initialize() {
    int nodes = graph_.node_count();
    ranks_.assign(nodes, 1. / nodes);
}

template<class Graph>
double Pagerank<Graph>::do_iteration() {
    decltype(ranks_) new_ranks(ranks_.size(), 0.);

    double sink_mass = 0.;

    #pragma omp parallel for schedule(dynamic)
    for (int n = 0; n < graph_.node_count(); ++n) {
        if (graph_.get_out_deg_int(InternalNode(n)) == 0) {
            #pragma omp atomic
            sink_mass += damping_factor * ranks_[n];
        }

        for (int e = 0; e < graph_.get_in_deg_int(InternalNode(n)); ++e) {
            const auto& edge = graph_.get_in_edge_int(InternalNode(n), e);

            new_ranks[n] +=
                damping_factor
                * ranks_[edge.from]
                / graph_.get_out_deg_int(edge.from);
        }
    }

    // it is possible that adding damping at the end is better numerically
    double damping = (1. - damping_factor + sink_mass) / ranks_.size();
    #pragma omp parallel for schedule(static)
    for (int i = 0; i < new_ranks.size(); ++i) {
        new_ranks[i] += damping;
    }

    double convergence = compute_convergence(ranks_, new_ranks);

    ranks_ = std::move(new_ranks);

    return convergence;
}

template<class Graph>
double Pagerank<Graph>::compute_convergence(
        const std::vector<double>& old,
        const std::vector<double>& fresh) const {

    double worst_conv = 0.;

    #pragma omp parallel for reduction(max: worst_conv)
    for (int i = 0; i < old.size(); ++i) {
        // should be ok, because of damping old shouldn't ever be 0
        double conv = fabs(fresh[i] / old[i] - 1.);

        if (conv > worst_conv) {
            worst_conv = conv;
        }
    }

    return worst_conv;
}
