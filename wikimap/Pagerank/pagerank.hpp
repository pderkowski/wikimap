#pragma once

#include <iostream>
#include <vector>
#include <utility>
#include <string>
#include <unordered_map>

class Pagerank {
public:
    Pagerank();

    void compute(std::istream& in, std::ostream& out);

public:
    int verbosity;
    bool sortOutput;

    double dampingFactor;
    double stopConvergence;
    int maxIterations;

private:
    void readData(std::istream& in);
    void writeResults(std::ostream& out) const;

    void initialize();
    double doIteration();
    double getConvergence(const std::vector<double>& old, const std::vector<double>& fresh) const;

    std::pair<int, int> getNodes(const std::string& line) const;
    void addNodeIfNotSeen(int node);
    void addEdge(int src, int dst);

    void printProgress(int readLines) const;

private:
    static std::string separator() {
        static std::string separator = "--------------------------------------------------------------------------------";
        return separator;
    }

    std::unordered_map<int, int> nodes2indices_;
    std::vector<int> indices2nodes_;
    std::vector<std::vector<int>> edges_;

    std::vector<double> ranks_;
};
