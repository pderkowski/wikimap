#pragma once

#include <random>
#include <vector>
#include <functional>

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
    std::string get(
        std::initializer_list<std::string> names,
        const std::string& default_) const;

    int get(const std::string& arg_name, const int& default_) const;
    int get(
        std::initializer_list<std::string> names,
        const int& default_) const;

    double get(const std::string& arg_name, const double& default_) const;
    double get(
        std::initializer_list<std::string> arg_name,
        const double& default_) const;

    bool has(const std::string& arg_name) const { return arg_pos(arg_name) > 0; }
    bool has(std::initializer_list<std::string> names) const { return arg_pos(names) > 0; }

private:
    int arg_pos(const std::string& name) const;
    int arg_pos(std::initializer_list<std::string> names) const;

    template<class T>
    T do_get(
        const std::string& arg_name,
        const T& default_,
        std::function<T(const char*)> getter) const;

    template<class T>
    T do_get(
        std::initializer_list<std::string> names,
        const T& default_,
        std::function<T(const char*)> getter) const;

    int argc_;
    const char** argv_;
};


Args::Args(int argc, const char* argv[])
:   argc_(argc), argv_(argv)
{ }

std::string Args::get(
        const std::string& arg_name,
        const std::string& default_) const {

    return do_get<std::string>(arg_name, default_, [] (const char* arg) {
        return std::string(arg);
    });
}

std::string Args::get(
        std::initializer_list<std::string> names,
        const std::string& default_) const {

    return do_get<std::string>(names, default_, [] (const char* arg) {
        return std::string(arg);
    });
}

int Args::get(const std::string& arg_name, const int& default_) const {
    return do_get<int>(arg_name, default_, [] (const char* arg) {
        return std::stoi(arg);
    });
}

int Args::get(
        std::initializer_list<std::string> names,
        const int& default_) const {

    return do_get<int>(names, default_, [] (const char* arg) {
        return std::stoi(arg);
    });
}

double Args::get(const std::string& arg_name, const double& default_) const {
    return do_get<double>(arg_name, default_, [] (const char* arg) {
        return std::stof(arg);
    });
}

double Args::get(
        std::initializer_list<std::string> names,
        const double& default_) const {

    return do_get<double>(names, default_, [] (const char* arg) {
        return std::stof(arg);
    });
}


template<class T>
T Args::do_get(
        const std::string& arg_name,
        const T& default_,
        std::function<T(const char*)> getter) const {

    int pos = arg_pos(arg_name);
    if (pos > 0) {
        if (pos >= argc_ - 1) {
            logging::log("Argument missing for %s\n", arg_name.c_str());
            exit(1);
        }
        return getter(argv_[pos + 1]);
    } else {
        return default_;
    }
}

template<class T>
T Args::do_get(
        std::initializer_list<std::string> names,
        const T& default_,
        std::function<T(const char*)> getter) const {

    for (const auto& name : names) {
        if (has(name)) {
            return do_get(name, default_, getter);
        }
    }
    return default_;
}

int Args::arg_pos(const std::string& arg_name) const {
    for (int pos = 1; pos < argc_; ++pos) {
        if (arg_name == argv_[pos]) {
            return pos;
        }
    }
    return -1;
}

int Args::arg_pos(std::initializer_list<std::string> names) const {
    for (const auto& name : names) {
        int pos = arg_pos(name);
        if (pos > 0) {
            return pos;
        }
    }
    return -1;
}


} // namespace w2v
