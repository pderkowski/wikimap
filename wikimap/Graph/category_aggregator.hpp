#pragma once


#include <omp.h>

#include "category_graph.hpp"


class CategoryAggregator {
public:
    CategoryAggregator(
        const std::vector<CatPageLink>& cat_page_links,
        const std::vector<CatCatLink>& cat_cat_links);

    std::unordered_map<Category, std::vector<Page>> aggregate(
        int max_depth) const;

private:
    void report_construction() const;
    void report_aggregation(long long processed) const;

    CategoryGraph graph_;
};


CategoryAggregator::CategoryAggregator(
        const std::vector<CatPageLink>& cat_page_links,
        const std::vector<CatCatLink>& cat_cat_links) {

    std::cerr << "Constructing graph...\n";

    long long changes = 0;
    for (const auto& cat_page : cat_page_links) {
        if (changes % 1000000 == 0) {
            report_construction();
        }
        graph_.add_page(cat_page.first, cat_page.second);

        ++changes;
    }

    for (const auto& cat_cat : cat_cat_links) {
        if (changes % 1000000 == 0) {
            report_construction();
        }
        graph_.add_link(cat_cat.first, cat_cat.second);

        ++changes;
    }

    report_construction();

    std::cerr << "Finished graph construction.\n";
}

std::unordered_map<Category, std::vector<Page>> CategoryAggregator::aggregate(
        int max_depth) const {

    std::unordered_map<Category, std::vector<Page>> res;

    std::cerr << "Aggregating categories...\n";

    auto categories = graph_.get_categories();
    for (auto cat : categories) {
        res[cat] = std::vector<Page>();
    }

    #pragma omp parallel for schedule(dynamic)
    for (long long processed = 0; processed < categories.size(); ++processed) {
        if (processed % 100000 == 0) {
            report_aggregation(processed);
        }

        auto near_cats = graph_.get_near_categories(
            categories[processed],
            max_depth);

        std::unordered_set<Page> unique_pages;
        for (const auto& near_cat : near_cats) {
            const auto& pages = graph_.get_pages(near_cat);
            unique_pages.insert(pages.begin(), pages.end());
        }

        res.at(categories[processed]).assign(
            unique_pages.begin(),
            unique_pages.end());
    }

    report_aggregation(categories.size());

    std::cerr << "Finished aggregating categories.\n";

    return res;
}

void CategoryAggregator::report_construction() const {
    std::cerr << "Graph has: " << graph_.node_count() << " nodes, "
        << graph_.edge_count() << " edges.\n";
}

void CategoryAggregator::report_aggregation(long long processed) const {
    std::cerr << "Processed " << processed << " of "
        << graph_.node_count() << " nodes.\n";
}
