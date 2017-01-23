#include "categorygraph.hpp"
#include <iostream>
#include <unordered_set>

// the only argument is depth: the number of levels in category hierarchy to aggregate
int main(int argc, const char* argv[]) {
    if (argc != 2) {
        std::cerr << "Invalid number of arguments!\n";
        return 1;
    } else {
        int depth = std::stoi(argv[1]);

        auto cg = CategoryGraph::fromStream(std::cin, 1);
        auto nodes = cg.getNodes();
        for (const auto& n : nodes) {
            auto nearbyNodes = cg.getNearbyNodes(n, depth);

            std::unordered_set<int> uniquePages;
            for (const auto& near : nearbyNodes) {
                const auto& pages = cg.getData(near);
                uniquePages.insert(pages.begin(), pages.end());
            }

            std::cout << n << " ";
            for (auto p : uniquePages) {
                std::cout << p << " ";
            }
            std::cout << "\n";
        }
        return 0;
    }
}