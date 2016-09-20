#include "catch.hpp"
#include "pagerank.hpp"
#include <sstream>
#include <map>

std::map<int, double> readResults(std::istream& in) {
    std::map<int, double> res;

    std::string line;
    while (std::getline(in, line)) {
        int spacePos = line.find(' ');
        int node = stoi(line.substr(0, spacePos));
        double rank = stod(line.substr(spacePos+1, std::string::npos));
        res[node] = rank;
    }

    return res;
}

TEST_CASE("Pagerank simple tests.", "[pagerank]") {
    Pagerank pr;
    pr.verbosity = 0;

    std::stringstream input, output;

    SECTION("") {
        // 1 -> 2 -> 3
        // ^         |
        // '---------'

        input << "1 2\n";
        input << "2 3\n";
        input << "3 1\n";

        pr.compute(input, output);

        auto results = readResults(output);

        REQUIRE(results[1] == Approx(1./3).epsilon(0.0001));
        REQUIRE(results[2] == Approx(1./3).epsilon(0.0001));
        REQUIRE(results[3] == Approx(1./3).epsilon(0.0001));
    }

    SECTION("") {
        // 1 -> 2 -> 3
        // ^    ^    |
        // '----'----'

        pr.dampingFactor = 0.7;

        input << "1 2\n";
        input << "2 3\n";
        input << "3 1\n";
        input << "3 2\n";

        pr.compute(input, output);

        auto results = readResults(output);

        REQUIRE(results[1] == Approx(0.2314).epsilon(0.0001));
        REQUIRE(results[2] == Approx(0.3933).epsilon(0.0001));
        REQUIRE(results[3] == Approx(0.3753).epsilon(0.0001));
    }

    SECTION("") {
        // 1 <-> 2 <-> 3

        pr.dampingFactor = 0.7;

        input << "1 2\n";
        input << "2 3\n";
        input << "3 2\n";
        input << "2 1\n";

        pr.compute(input, output);

        auto results = readResults(output);

        REQUIRE(results[1] == Approx(0.2647).epsilon(0.0001));
        REQUIRE(results[2] == Approx(0.4706).epsilon(0.0001));
        REQUIRE(results[3] == Approx(0.2647).epsilon(0.0001));
    }

}

