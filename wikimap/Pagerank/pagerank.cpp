#include <unordered_map>
#include <vector>
#include <iostream>
#include <algorithm>
#include <string>
#include <limits>
#include <iomanip>
#include <cstdio>
#include <cstdlib>
#include <tuple>
#include "pagerank.hpp"

Pagerank::Pagerank()
:   verbosity(1),
    sortOutput(true),
    dampingFactor(0.85),
    stopConvergence(1e-7),
    maxIterations(200),
    nodes2indices_(), indices2nodes_(), edges_()
{ }

void Pagerank::readData(std::istream& in) {
    if (verbosity >= 1) std::cerr << "Reading data." << std::endl;

    std::string line;
    for (int lineNo = 0; std::getline(in, line); ++lineNo) {
        if (lineNo % 1000000 == 0) printProgress(lineNo);

        int src, dst;
        std::tie(src, dst) = getNodes(line);

        addNodeIfNotSeen(src);
        addNodeIfNotSeen(dst);

        addEdge(src, dst);
    }

    if (verbosity >= 1) std::cerr << "Finished reading data." << std::endl;
}

void Pagerank::addEdge(int src, int dst) {
    auto srcIdx = nodes2indices_.at(src);
    auto dstIdx = nodes2indices_.at(dst);

    edges_[srcIdx].push_back(dstIdx);
}

void Pagerank::printProgress(int readLines) const {
    if (verbosity >= 1) std::cerr << "\33[2K\r" << "Read " << readLines << " lines, seen " << nodes2indices_.size() << " nodes.\n" << std::flush;
}

std::pair<int, int> Pagerank::getNodes(const std::string& line) const {
    int spacePos = line.find(' ');
    int src = stoi(line.substr(0, spacePos));
    int dst = stoi(line.substr(spacePos+1, std::string::npos));
    return std::make_pair(src, dst);
}

void Pagerank::addNodeIfNotSeen(int node) {
    if (nodes2indices_.find(node) == nodes2indices_.end()) {
        nodes2indices_[node] = indices2nodes_.size();
        indices2nodes_.push_back(node);
        edges_.push_back(std::vector<int>{});
    }
}

void Pagerank::initialize() {
    if (verbosity >= 1) std::cerr << "Initializing weights." << std::endl;
    int nodesNo = nodes2indices_.size();
    ranks_ = std::vector<double>(nodesNo, 1./nodesNo);
    if (verbosity >= 1) std::cerr << separator() << "\n";
}

double Pagerank::getConvergence(const std::vector<double>& old, const std::vector<double>& fresh) const {
    double maxCoef = 0.;
    for (int i = 0; i < old.size(); ++i) {
        double c;
        if (old[i] != 0.) {
            c = fabs(fresh[i] / old[i] - 1.);
        } else if (fresh[i] == 0.) {
            c = 0.;
        } else {
            c = std::numeric_limits<double>::max();
        }

        maxCoef = std::max(maxCoef, c);
    }
    return maxCoef;
}

double Pagerank::doIteration() {
    auto newRanks = std::vector<double>(ranks_.size(), (1 - dampingFactor) / ranks_.size());

    for (int n = 0; n < edges_.size(); ++n) {
        for (int e = 0; e < edges_[n].size(); ++e) {
            newRanks[edges_[n][e]] += dampingFactor * ranks_[n] / edges_[n].size();
        }
    }

    if (verbosity >= 2) {
        std::cerr << "New ranks:\n";
        for (int i = 0; i < newRanks.size(); ++i) {
            std::cerr << indices2nodes_[i] << " " << newRanks[i] << "\n";
        }
    }

    double coef = getConvergence(ranks_, newRanks);

    ranks_ = std::move(newRanks);
    return coef;
}

void Pagerank::compute(std::istream& in, std::ostream& out) {
    readData(in);

    if (verbosity >= 1) std::cerr << "COMPUTING PAGERANK" << std::endl;
    if (verbosity >= 1) std::cerr << "Stop condition: convergence coefficient less than " << stopConvergence << " or " << maxIterations << " iterations." << std::endl;

    initialize();

    for (int iteration = 0; ; ++iteration) {
        double convergence = doIteration();

        if (verbosity >= 1) std::cerr << "Iteration " << std::setw(3) << iteration << ": " << std::flush;
        if (verbosity >= 1) std::cerr << "convergence: " << std::setprecision(3) << convergence << std::endl;

        if (convergence < stopConvergence) {
            if (verbosity >= 1) std::cerr << "Reached convergence, stopping." << std::endl;
            break;
        } else if (iteration >= maxIterations) {
            if (verbosity >= 1) std::cerr << "Reached maximum number of iterations, stopping." << std::endl;
            break;
        }
    }
    if (verbosity >= 1) std::cerr << separator() << "\n";

    writeResults(out);
}

void Pagerank::writeResults(std::ostream& out) const {
    out.precision(std::numeric_limits<double>::max_digits10);

    std::vector<int> order(indices2nodes_.size());
    for (int i = 0; i < order.size(); ++i) {
        order[i] = i;
    }

    if (sortOutput) {
        std::sort(order.begin(), order.end(), [this] (int lhs, int rhs) {
            return ranks_[lhs] > ranks_[rhs];
        });
    }

    for (int i = 0; i < order.size(); ++i) {
        out << indices2nodes_[order[i]] << " " << ranks_[order[i]] << "\n";
    }
}
