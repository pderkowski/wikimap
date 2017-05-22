#pragma once

#include <vector>
#include <limits>

#include "defs.hpp"

namespace emb {


template<int N>
struct StrongInt {
public:
    StrongInt()
    :   StrongInt(0)
    { }

    explicit StrongInt(int val)
    :   val(val)
    { }

    operator int() const { return val; }

    int val;
};

template<class Node>
class Graph {
private:
    typedef StrongInt<0> InternalNode;
    typedef StrongInt<1> InternalEdge;

    struct NodeData {
        std::vector<InternalEdge> outgoing;
        std::vector<InternalEdge> incoming;
    };

    struct EdgeData {
        EdgeData(InternalNode from, InternalNode to);

        InternalNode from;
        InternalNode to;
    };

public:
    void add_node(Node node);
    void add_edge(Node from, Node to);

    bool has_node(Node node) const;

    size_t get_out_deg(Node node) const;
    size_t get_in_deg(Node node) const;

    bool has_neighbor(Node node) const;

    template<class Rng>
    Node get_random_neighbor(Node node, Rng& rng) const;

    size_t node_count() const { return node_data_.size(); }
    size_t edge_count() const { return edge_data_.size(); }

    std::vector<Node> get_nodes() const { return int2ext_; }

private:
    NodeData& get_node(Node node);
    const NodeData& get_node(Node node) const;

    std::unordered_map<Node, InternalNode> ext2int_;
    std::vector<Node> int2ext_;
    std::vector<NodeData> node_data_;
    std::vector<EdgeData> edge_data_;
};

template<class Node>
const typename Graph<Node>::NodeData& Graph<Node>::get_node(Node node) const {
    return node_data_[ext2int_.at(node)];
}

template<class Node>
typename Graph<Node>::NodeData& Graph<Node>::get_node(Node node) {
    return node_data_[ext2int_.at(node)];
}

template<class Node>
inline size_t Graph<Node>::get_out_deg(Node node) const {
    return get_node(node).outgoing.size();
}

template<class Node>
inline size_t Graph<Node>::get_in_deg(Node node) const {
    return get_node(node).incoming.size();
}

template<class Node>
inline bool Graph<Node>::has_neighbor(Node node) const {
    return get_node(node).outgoing.size() > 0;
}

template<class Node>
template<class Rng>
inline Node Graph<Node>::get_random_neighbor(Node node, Rng& rng) const {
    auto int_random_edge = get_node(node).outgoing[rng() % get_out_deg(node)];
    const auto& random_edge = edge_data_[int_random_edge];
    return int2ext_[random_edge.to];
}

template<class Node>
Graph<Node>::EdgeData::EdgeData(InternalNode from, InternalNode to)
:   from(from), to(to)
{ }

template<class Node>
inline bool Graph<Node>::has_node(Node node) const {
    return ext2int_.find(node) != ext2int_.end();
}

template<class Node>
inline void Graph<Node>::add_node(Node node) {
    InternalNode int_node{static_cast<int>(ext2int_.size())};
    ext2int_[node] = int_node;
    int2ext_.push_back(node);
    node_data_.push_back(NodeData());
}

template<class Node>
inline void Graph<Node>::add_edge(Node from, Node to) {
    if (!has_node(from)) {
        add_node(from);
    }
    if (!has_node(to)) {
        add_node(to);
    }
    InternalEdge edge{static_cast<int>(edge_data_.size())};
    edge_data_.push_back(EdgeData(ext2int_.at(from), ext2int_.at(to)));
    get_node(from).outgoing.push_back(edge);
    get_node(to).incoming.push_back(edge);
}


} // namespace emb
