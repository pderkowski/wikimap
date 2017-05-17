#pragma once

#include <random>
#include <vector>

#include <omp.h>

#include "defs.hpp"
#include "logging.hpp"


namespace w2v {


// This class holds random number generators for each thread.
class Random {
public:
    typedef std::mt19937 Rng;

    Random();

    static Rng& get();

private:
    std::vector<Rng> rnds_;
};

Random::Random() {
    auto seed = std::random_device()();
    for (int i = 0; i < omp_get_max_threads(); ++i) {
        rnds_.push_back(Rng(seed + i));
    }
}

Random::Rng& Random::get() {
    static Random instance;
    return instance.rnds_[omp_get_thread_num()];
}


class Args {
public:
    Args(int argc, const char* argv[]);

    std::string get(const std::string& arg_name, const std::string& default_) const;
    int get(const std::string& arg_name, int default_) const;
    double get(const std::string& arg_name, double default_) const;

    bool has(const std::string& arg_name) const { return arg_pos(arg_name) > 0; }

private:
    int arg_pos(const std::string& name) const;

    int argc_;
    const char** argv_;
};


Args::Args(int argc, const char* argv[])
:   argc_(argc), argv_(argv)
{ }

std::string Args::get(
        const std::string& arg_name,
        const std::string& default_) const {

    int pos = arg_pos(arg_name);
    if (pos > 0) {
        if (pos >= argc_ - 1) {
            logging::log("Argument missing for %s\n", arg_name.c_str());
            exit(1);
        }
        return argv_[pos + 1];
    } else {
        return default_;
    }
}

int Args::get(const std::string& arg_name, int default_) const {
    int pos = arg_pos(arg_name);
    if (pos > 0) {
        if (pos >= argc_ - 1) {
            logging::log("Argument missing for %s\n", arg_name.c_str());
            exit(1);
        }
        return std::stoi(argv_[pos + 1]);
    } else {
        return default_;
    }
}

double Args::get(const std::string& arg_name, double default_) const {
    int pos = arg_pos(arg_name);
    if (pos > 0) {
        if (pos >= argc_ - 1) {
            logging::log("Argument missing for %s\n", arg_name.c_str());
            exit(1);
        }
        return std::stof(argv_[pos + 1]);
    } else {
        return default_;
    }
}

int Args::arg_pos(const std::string& arg_name) const {
    for (int pos = 1; pos < argc_; ++pos) {
        if (arg_name == argv_[pos]) {
            return pos;
        }
    }
    return -1;
}


} // namespace w2v
