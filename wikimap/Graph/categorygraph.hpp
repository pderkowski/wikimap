#include <unordered_map>
#include <vector>
#include <iostream>
#include "Snap.h"

class CategoryGraph {
public:
    CategoryGraph();

    void addEdge(const std::string& from, const std::string& to);
    void addData(const std::string& at, int what);

    std::vector<std::string> getNearbyNodes(const std::string& node, int maxDist) const;
    std::vector<int> getData(const std::string& node) const;
    std::vector<std::string> getNodes() const;

    void stats() const;

    static CategoryGraph fromStream(std::istream& in, int verbosity);

private:
    void addNodeIfNotExists(const std::string& node);

    std::unordered_map<std::string, int> name2idx_;
    std::vector<std::string> idx2name_;
    TPt<TNodeNet<TIntV>> graph_;
    mutable TBreathFS<TPt<TNodeNet<TIntV>>> bfs_;
};