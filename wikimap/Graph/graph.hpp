#pragma once

#include <vector>
#include <type_traits>
#include <queue>
#include <algorithm>

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

typedef StrongInt<0> InternalNode;
typedef StrongInt<1> InternalEdge;

template<class Data>
struct InternalNodeData {
    typedef Data& reference_type;
    typedef const Data& const_reference_type;

    std::vector<InternalEdge> outbound;
    std::vector<InternalEdge> inbound;

    Data data;
};

template<>
struct InternalNodeData<void> {
    typedef void reference_type;
    typedef void const_reference_type;

    std::vector<InternalEdge> outbound;
    std::vector<InternalEdge> inbound;
};

struct InternalEdgeData {
    InternalEdgeData(InternalNode from, InternalNode to);

    InternalNode from;
    InternalNode to;
};

InternalEdgeData::InternalEdgeData(InternalNode from, InternalNode to)
:   from(from), to(to)
{ }

template<class Node, class NodeData = void>
class Graph {
public:
    typedef Node node_type;

private:
    typedef InternalNodeData<NodeData> IND;
    typedef InternalEdgeData IED;

public:
    void add_node(const Node& node);

    void add_edge(const Node& from, const Node& to);
    void checked_add_edge(const Node& from, const Node& to);

    bool has_node(const Node& node) const;

    size_t get_out_deg(const Node& node) const;
    size_t get_in_deg(const Node& node) const;

    bool has_neighbor(const Node& node) const;

    template<class Rng>
    const Node& get_random_neighbor(const Node& node, Rng& rng) const;

    size_t node_count() const { return node_data_.size(); }
    size_t edge_count() const { return edge_data_.size(); }

    const std::vector<Node>& get_nodes() const { return int2ext_; }

    typename IND::const_reference_type get_data(const Node& node) const;
    typename IND::reference_type get_data(const Node& node);

private:
    IND& get_node(const Node& node);
    const IND& get_node(const Node& node) const;

    std::unordered_map<Node, InternalNode> ext2int_;
    std::vector<Node> int2ext_;
    std::vector<IND> node_data_;
    std::vector<IED> edge_data_;

public:
    // accessors for algorithms operating on a graph
    // int stands for 'internal', because this methods use internal
    // representation for nodes, which is integers from 0 to node_count() - 1
    const IND& get_node_int(InternalNode node) const;
    typename IND::const_reference_type get_data_int(InternalNode node) const;
    size_t get_out_deg_int(InternalNode node) const;
    size_t get_in_deg_int(InternalNode node) const;
    const Node& get_ext(InternalNode node) const { return int2ext_[node]; }
    InternalNode get_int(const Node& node) const { return ext2int_.at(node); }
    const IED& get_in_edge_int(InternalNode node, int edge_no) const;
    const IED& get_out_edge_int(InternalNode node, int edge_no) const;
};

template<class Node, class NodeData>
const InternalNodeData<NodeData>& Graph<Node, NodeData>::get_node(
        const Node& node) const {

    return node_data_[ext2int_.at(node)];
}

template<class Node, class NodeData>
InternalNodeData<NodeData>& Graph<Node, NodeData>::get_node(const Node& node) {
    return node_data_[ext2int_.at(node)];
}

template<class Node, class NodeData>
inline size_t Graph<Node, NodeData>::get_out_deg(const Node& node) const {
    return get_node(node).outbound.size();
}

template<class Node, class NodeData>
inline size_t Graph<Node, NodeData>::get_in_deg(const Node& node) const {
    return get_node(node).inbound.size();
}

template<class Node, class NodeData>
inline bool Graph<Node, NodeData>::has_neighbor(const Node& node) const {
    return get_node(node).outbound.size() > 0;
}

template<class Node, class NodeData>
template<class Rng>
inline const Node& Graph<Node, NodeData>::get_random_neighbor(
        const Node& node,
        Rng& rng) const {

    auto int_random_edge = get_node(node).outbound[rng() % get_out_deg(node)];
    const auto& random_edge = edge_data_[int_random_edge];
    return int2ext_[random_edge.to];
}

template<class Node, class NodeData>
inline bool Graph<Node, NodeData>::has_node(const Node& node) const {
    return ext2int_.find(node) != ext2int_.end();
}

template<class Node, class NodeData>
inline void Graph<Node, NodeData>::add_node(const Node& node) {
    InternalNode int_node{static_cast<int>(ext2int_.size())};
    ext2int_[node] = int_node;
    int2ext_.push_back(node);
    node_data_.push_back(InternalNodeData<NodeData>());
}

template<class Node, class NodeData>
inline void Graph<Node, NodeData>::add_edge(const Node& from, const Node& to) {
    InternalEdge edge{static_cast<int>(edge_data_.size())};
    edge_data_.push_back(InternalEdgeData(ext2int_.at(from), ext2int_.at(to)));
    get_node(from).outbound.push_back(edge);
    get_node(to).inbound.push_back(edge);
}

template<class Node, class NodeData>
inline void Graph<Node, NodeData>::checked_add_edge(
        const Node& from,
        const Node& to) {

    if (!has_node(from)) {
        add_node(from);
    }
    if (!has_node(to)) {
        add_node(to);
    }
    add_edge(from, to);
}

template<class Node, class NodeData>
inline typename InternalNodeData<NodeData>::const_reference_type
Graph<Node, NodeData>::get_data(const Node& node) const {
    static_assert(
        !std::is_void<typename IND::const_reference_type>::value,
        "Can't call Graph::get_data, if NodeData = void.");
    return get_node(node).data;
}

template<class Node, class NodeData>
inline typename InternalNodeData<NodeData>::reference_type
Graph<Node, NodeData>::get_data(const Node& node) {
    static_assert(
        !std::is_void<typename IND::reference_type>::value,
        "Can't call Graph::get_data, if NodeData = void.");
    return get_node(node).data;
}

template<class Node, class NodeData>
inline const InternalNodeData<NodeData>& Graph<Node, NodeData>::get_node_int(
        InternalNode node) const {

    return node_data_[node];
}

template<class Node, class NodeData>
inline typename InternalNodeData<NodeData>::const_reference_type
Graph<Node, NodeData>::get_data_int(InternalNode node) const {
    static_assert(
        !std::is_void<typename IND::const_reference_type>::value,
        "Can't call Graph::get_data, if NodeData = void.");
    return node_data_[node].data;
}

template<class Node, class NodeData>
inline size_t Graph<Node, NodeData>::get_out_deg_int(InternalNode node) const {
    return node_data_[node].outbound.size();
}

template<class Node, class NodeData>
inline size_t Graph<Node, NodeData>::get_in_deg_int(InternalNode node) const {
    return node_data_[node].inbound.size();
}

template<class Node, class NodeData>
inline const InternalEdgeData& Graph<Node, NodeData>::get_in_edge_int(
        InternalNode node, int edge_no) const {

    auto edge = node_data_[node].inbound[edge_no];
    return edge_data_[edge];
}

template<class Node, class NodeData>
inline const InternalEdgeData& Graph<Node, NodeData>::get_out_edge_int(
        InternalNode node, int edge_no) const {

    auto edge = node_data_[node].outbound[edge_no];
    return edge_data_[edge];
}