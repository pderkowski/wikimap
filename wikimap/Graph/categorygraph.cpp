#include "Snap.h"
#include "categorygraph.hpp"
#include <iostream>
#include <sstream>
#include <memory>
#include <algorithm>

void split(const std::string &s, char delim, std::vector<std::string> &elems) {
    std::stringstream ss;
    ss.str(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
        elems.push_back(item);
    }
}

std::vector<std::string> split(const std::string &s, char delim = ' ') {
    std::vector<std::string> elems;
    split(s, delim, elems);
    return elems;
}

class Command {
public:
    virtual ~Command() { }

    virtual void execute(CategoryGraph& g) = 0;

    static std::unique_ptr<Command> fromString(const std::string& line);
};

class EdgeCommand : public Command {
public:
    EdgeCommand(const std::string& from, const std::string& to)
    : from_(from), to_(to)
    { }

    void execute(CategoryGraph& g) {
        g.addEdge(from_, to_);
    }

private:
    std::string from_;
    std::string to_;
};

class DataCommand : public Command {
public:
    DataCommand(const std::string& at, int what)
    : at_(at), what_(what)
    { }

    void execute(CategoryGraph& g) {
        g.addData(at_, what_);
    }

private:
    std::string at_;
    int what_;
};

std::unique_ptr<Command> Command::fromString(const std::string& line) {
    auto tokens = split(line);
    if (tokens[0] == "e") {
        return std::unique_ptr<Command>(new EdgeCommand(tokens[1], tokens[2]));
    } else if (tokens[0] == "d") {
        return std::unique_ptr<Command>(new DataCommand(tokens[1], std::stoi(tokens[2])));
    } else {
        throw std::runtime_error("Invalid command line: " + line);
    }
}

CategoryGraph::CategoryGraph()
: name2idx_(), idx2name_(), graph_(TNodeNet<TIntV>::New()), bfs_(graph_)
{ }

void CategoryGraph::addEdge(const std::string& from, const std::string& to) {
    addNodeIfNotExists(from);
    addNodeIfNotExists(to);
    graph_->AddEdge(name2idx_.at(from), name2idx_.at(to));
}

void CategoryGraph::addData(const std::string& at, int what) {
    addNodeIfNotExists(at);
    graph_->GetNDat(name2idx_.at(at)).Add(what);
}

void CategoryGraph::addNodeIfNotExists(const std::string& node) {
    if (name2idx_.find(node) == name2idx_.end()) {
        idx2name_.push_back(node);
        int id = idx2name_.size() - 1;
        name2idx_[node] = id;
        graph_->AddNode(id);
    }
}

void CategoryGraph::stats() const {
    std::cerr << "Graph has " << graph_->GetNodes() << " nodes and " << graph_->GetEdges() << " edges." << std::endl;
}

std::vector<std::string> CategoryGraph::getNearbyNodes(const std::string& node, int maxDist) const {
    bfs_.DoBfs(name2idx_.at(node), true, false, -1, maxDist);
    TIntV nearby;
    bfs_.GetVisitedNIdV(nearby);
    std::vector<std::string> res;
    for (auto it = nearby.BegI(); it != nearby.EndI(); it++) {
        res.push_back(idx2name_.at(*it));
    }
    return res;
}

std::vector<int> CategoryGraph::getData(const std::string& node) const {
    const auto& data = graph_->GetNDat(name2idx_.at(node));
    return std::vector<int>(data.BegI(), data.EndI());
}

std::vector<std::string> CategoryGraph::getNodes() const {
    std::vector<std::string> res;
    for (auto it = graph_->BegNI(); it != graph_->EndNI(); it++) {
        res.push_back(idx2name_.at(it.GetId()));
    }
    return res;
}

CategoryGraph CategoryGraph::fromStream(std::istream& in, int verbosity = 0) {
    CategoryGraph cg;

    if (verbosity >= 1) std::cerr << "Starting graph construction." << std::endl;

    std::string line;
    for (int lineNo = 0; std::getline(in, line); ++lineNo) {
        if (lineNo % 1000000 == 0) {
            std::cerr << "Read " << lineNo << " lines. ";
            cg.stats();
        }

        auto command = Command::fromString(line);
        command->execute(cg);
    }

    if (verbosity >= 1) {
        std::cerr << "Finished graph construction.";
        cg.stats();
    }

    return cg;
}