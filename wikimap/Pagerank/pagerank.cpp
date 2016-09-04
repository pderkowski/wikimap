#include <unordered_map>
#include <vector>
#include <iostream>
#include <unordered_set>
#include <iterator>
#include <fstream>
#include <algorithm>
#include <string>
#include <limits>
#include <iomanip>
#include <map>
#include <boost/python.hpp>
#include <cstdio>
#include <cstdlib>

class TempFile {
public:
    TempFile()
    : name_(std::tmpnam(nullptr))
    { }

    ~TempFile() {
        std::remove(name_.c_str());
    }

    std::string name() const {
        return name_;
    }

private:
    std::string name_;
};

using namespace std;

unordered_map<int, int> nodes2indices;
vector<int> edges;
vector<int> edgesPerNode;
int edgesNo = -1;
vector<double> ranks;
vector<int> indices2nodes;

string separator = "--------------------------------------------------------------------------------";

void getIndices(istream& in) {

    cout << "Collecting nodes." << endl;
    unordered_set<int> nodes;

    edgesNo = 0;
    string line;
    while (getline(in, line)) {
        if (edgesNo % 1000000 == 0) {
            cout << "\33[2K\r" << "Read " << edgesNo << " lines." << flush;
        }

        int spacePos = line.find(' ');
        int src = stoi(line.substr(0, spacePos));
        int dest = stoi(line.substr(spacePos+1, string::npos));

        nodes.insert(src);
        nodes.insert(dest);

        ++edgesNo;
    }
    cout << "\33[2K\r" << "Seen " << nodes.size() << " nodes and " << edgesNo << " edges." << endl;

    vector<int> sortedNodes(nodes.begin(), nodes.end());
    nodes.clear();

    cout << "Sorting nodes." << endl;
    sort(sortedNodes.begin(), sortedNodes.end());

    cout << "Computing indices." << endl;

    nodes2indices.reserve(sortedNodes.size());
    indices2nodes.resize(sortedNodes.size());
    int index = 0;
    for (auto n : sortedNodes) {
        nodes2indices[n] = index;
        indices2nodes[index] = n;
        ++index;
    }
    sortedNodes.clear();
    cout << separator << "\n";
}

void getEdges(istream& in) {
    edgesPerNode = vector<int>(nodes2indices.size());
    edgesPerNode.shrink_to_fit();

    if (edgesNo > 0) {
        edges.resize(edgesNo);
    }
    edgesPerNode.shrink_to_fit();

    cout << "Collecting edges from input." << endl;
    int i = 0;
    string line;
    while (getline(in, line)) {
        if (i % 1000000 == 0) {
            cout << "\33[2K\r" << "Read " << i << " lines." << flush;
        }

        int spacePos = line.find(' ');
        int src = stoi(line.substr(0, spacePos));
        int dest = stoi(line.substr(spacePos+1, string::npos));

        int srcId = nodes2indices[src];
        int destId = nodes2indices[dest];

        ++edgesPerNode[srcId];

        edges[i] = destId;
        ++i;
    }
    cout << "\33[2K\r" << "Read " << i << " lines." << endl;
    cout << separator << "\n";
}

void initializePagerank() {
    cout << "Initializing weights." << endl;
    int nodes = nodes2indices.size();
    ranks = vector<double>(nodes, 1./nodes);
    cout << separator << "\n";
}

double getConvergence(const vector<double>& old, const vector<double>& fresh) {
    double maxCoef = 0.;
    for (int i = 0; i < old.size(); ++i) {
        double c;
        if (old[i] != 0.) {
            c = abs(fresh[i] / old[i] - 1.);
        } else if (fresh[i] == 0.) {
            c = 0.;
        } else {
            c = numeric_limits<double>::max();
        }

        maxCoef = max(maxCoef, c);
    }
    return maxCoef;
}

double doPagerankIteration(double dampingFactor=0.85) {
    auto newRanks = vector<double>(ranks.size(), (1 - dampingFactor) / ranks.size());

    int edge = 0;
    for (int node = 0; node < edgesPerNode.size(); ++node) {
        for (int e = 0; e < edgesPerNode[node]; ++e) {
            newRanks[edges[edge]] += dampingFactor * ranks[node] / edgesPerNode[node];
            ++edge;
        }
    }
    double coef = getConvergence(ranks, newRanks);

    ranks = move(newRanks);
    return coef;
}

int guardedIncrement(int i, int max, const string& errorMessage) {
    if (i < max) {
        return i + 1;
    } else {
        cout << errorMessage << endl;
        exit(1);
    }
}

void computePagerank() {
    double stopConvergence = 1e-7;
    int maxIterations = 200;

    cout << "COMPUTING PAGERANK" << endl;
    cout << "Stop condition: convergence coefficient less than " << stopConvergence << " or " << maxIterations << " iterations." << endl;

    initializePagerank();

    for (int i = 0; ; ++i) {
        cout << "Iteration " << setw(3) << i << ": " << flush;

        double convergence = doPagerankIteration();
        cout << "convergence: " << setprecision(3) << convergence << endl;

        if (convergence < stopConvergence) {
            cout << "Reached convergence, stopping." << endl;
            break;
        } else if (i >= maxIterations) {
            cout << "Reached maximum number of iterations, stopping." << endl;
            break;
        }
    }
    cout << separator << "\n";
}

void readData(const string& fileName) {
    ifstream input(fileName);

    if (input) {
        getIndices(input);
        input.clear();
        input.seekg(0, ios::beg);
        getEdges(input);
    } else {
        cout << "Couldn't open file: " << fileName << endl;
        exit(1);
    }
}

void save(const string& fileName) {
    ofstream output(fileName);

    if (output) {
        for (int i = 0; i < ranks.size(); ++i) {
            output << indices2nodes[i] << " " << ranks[i] << "\n";
        }

        cout << "Saved to " << fileName << endl;
    } else {
       cout << "Couldn't open file: " << fileName << endl;
       exit(1);
    }
}

void executeSort(const std::string& input, const std::string& output) {
    std::string command = "sort -k 2 -g -r -o " + output + " " + input;
    system(command.c_str());
}

void pagerank(const std::string& input, const std::string& output) {
    locale::global(locale(""));

    TempFile tmp;

    readData(input);
    computePagerank();
    save(tmp.name());

    executeSort(tmp.name(), output);
}

namespace py = boost::python;

BOOST_PYTHON_MODULE(libpagerank) {
    py::def("pagerank", pagerank);
}