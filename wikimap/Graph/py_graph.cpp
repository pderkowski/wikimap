#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "category_aggregator.hpp"
#include "graph.hpp"
#include "algorithms.hpp"


namespace py = pybind11;

PYBIND11_PLUGIN(graph) {
    py::module m("graph");

    m.def("aggregate", [] (
            const std::vector<std::pair<Category, Page>>& cat_page_links,
            const std::vector<std::pair<Category, Category>>& cat_cat_links,
            int max_depth) {

        CategoryAggregator aggregator(cat_page_links, cat_cat_links);
        return aggregator.aggregate(max_depth);
    });

    m.def("pagerank", [] (py::iterable links) {
        typedef std::pair<Page, Page> Link;
        // const std::vector<std::pair<Page, Page>>& links)
        Graph<Page> graph;
        for (const auto& link_handle : links) {
            auto link = link_handle.cast<Link>();
            graph.checked_add_edge(link.first, link.second);
        }

        Pagerank<decltype(graph)> pagerank(graph);
        pagerank.compute();
        return pagerank.sorted_by_decreasing_ranks();
    });

    return m.ptr();
}
