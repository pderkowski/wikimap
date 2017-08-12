#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <iterator>

#include "category_aggregator.hpp"
#include "graph.hpp"
#include "algorithms.hpp"


namespace py = pybind11;

PYBIND11_PLUGIN(graph) {
    py::module m("graph");

    m.def("aggregate", [] (
            py::iterable cat_page_links,
            py::iterable cat_cat_links,
            int max_depth) {

        std::vector<CatPageLink> cat_page_links_v;
        std::transform(
            cat_page_links.begin(),
            cat_page_links.end(),
            std::back_inserter(cat_page_links_v),
            [] (const py::handle& handle) {
                return handle.cast<CatPageLink>();
            });

        std::vector<CatPageLink> cat_cat_links_v;
        std::transform(
            cat_cat_links.begin(),
            cat_cat_links.end(),
            std::back_inserter(cat_cat_links_v),
            [] (const py::handle& handle) {
                return handle.cast<CatCatLink>();
            });

        CategoryAggregator aggregator(cat_page_links_v, cat_cat_links_v);
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
