#pragma once

#include "graph.hpp"
#include "algorithms.hpp"


typedef std::string Category;
typedef std::vector<std::string> Categories;
typedef std::vector<int> Pages;


class CategoryGraph {
public:
    void add_link(const Category& sub_cat, const Category& super_cat);
    void add_page(const Category& cat, int page_id);

    size_t node_count() const { return graph_.node_count(); }
    size_t edge_count() const { return graph_.edge_count(); }

    const Pages& get_pages(const Category& cat) const;
    const Categories& get_categories() const;

    Categories get_near_categories(const Category& cat, int max_distance) const;

private:
    Graph<Category, Pages> graph_;
};


inline void CategoryGraph::add_link(
        const Category& sub_cat,
        const Category& super_cat) {

    graph_.checked_add_edge(sub_cat, super_cat);
}

inline void CategoryGraph::add_page(const Category& cat, int page_id) {
    if (!graph_.has_node(cat)) {
        graph_.add_node(cat);
    }
    graph_.get_data(cat).push_back(page_id);
}

inline const Pages& CategoryGraph::get_pages(const Category& cat) const {
    return graph_.get_data(cat);
}

inline const Categories& CategoryGraph::get_categories() const {
    return graph_.get_nodes();
}

Categories CategoryGraph::get_near_categories(
        const Category& cat,
        int max_distance) const {

    GraphSearch<decltype(graph_)> search(graph_);
    search.bfs(cat, max_distance);
    return search.reached_nodes();
}
