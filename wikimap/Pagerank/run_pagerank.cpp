#include "pagerank.hpp"
#include <iostream>
#include <string>

int main(int argc, const char* argv[]) {
    if (argc != 2) {
        std::cerr << "Invalid number of arguments!\n";
        return 1;
    } else {
        Pagerank pr;
        pr.verbosity = std::stoi(argv[1]);
        pr.compute(std::cin, std::cout);
    }

    return 0;
}