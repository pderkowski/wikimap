#pragma once

#include <random>
#include <vector>
#include <functional>

#include <omp.h>

#include "defs.hpp"
#include "logging.hpp"


namespace emb {

// This class holds random number generators for each thread.
class Random {
public:
    typedef std::mt19937 Rng;

    Random();

    static Rng& global_rng();
    Rng& rng();

    void seed(Int seed);

private:
    std::vector<Rng> rngs_;
};


Random::Random() {
    auto seed = std::random_device()();
    for (int i = 0; i < omp_get_max_threads(); ++i) {
        rngs_.push_back(Rng(seed + i));
    }
}

inline Random::Rng& Random::global_rng() {
    static Random instance;
    return instance.rng();
}

inline Random::Rng& Random::rng() {
    return rngs_[omp_get_thread_num()];
}

inline void Random::seed(Int s) {
    rng().seed(s);
}


class Args {
public:
    typedef std::string Name;
    typedef std::initializer_list<Name> Names;

    Args(int argc, const char* argv[]);

    std::string get_string(const Name& arg_name, std::string def = "") const;
    std::string get_string(Names names, std::string def = "") const;

    int get_int(const Name& arg_name, int def = 0) const;
    int get_int(Names names, int def = 0) const;

    Float get_float(const Name& arg_name, Float def = 0.) const;
    Float get_float(Names names, Float def = 0.) const;

    bool has(const Name& arg_name) const { return arg_pos(arg_name) > 0; }
    bool has(Names names) const { return arg_pos(names) > 0; }

private:
    int arg_pos(const Name& name) const;
    int arg_pos(Names names) const;

    template<class T>
    T do_get(
        const Name& arg_name,
        T def,
        std::function<T(const char*)> getter) const;

    template<class T>
    T do_get(
        Names names,
        T def,
        std::function<T(const char*)> getter) const;

    int argc_;
    const char** argv_;
};


Args::Args(int argc, const char* argv[])
:   argc_(argc), argv_(argv)
{ }

std::string Args::get_string(const Name& arg_name, std::string def) const {
    return do_get<std::string>(arg_name, def, [] (const char* arg) {
        return std::string(arg);
    });
}

std::string Args::get_string(Names names, std::string def) const {
    return do_get<std::string>(names, def, [] (const char* arg) {
        return std::string(arg);
    });
}

int Args::get_int(const Name& arg_name, int def) const {
    return do_get<int>(arg_name, def, [] (const char* arg) {
        return std::stoi(arg);
    });
}

int Args::get_int(Names names, int def) const {
    return do_get<int>(names, def, [] (const char* arg) {
        return std::stoi(arg);
    });
}

Float Args::get_float(const Name& arg_name, Float def) const {
    return do_get<Float>(arg_name, def, [] (const char* arg) {
        return std::stof(arg);
    });
}

Float Args::get_float(Names names, Float def) const {
    return do_get<Float>(names, def, [] (const char* arg) {
        return std::stof(arg);
    });
}


template<class T>
T Args::do_get(
        const Name& arg_name,
        T def,
        std::function<T(const char*)> getter) const {

    int pos = arg_pos(arg_name);
    if (pos > 0) {
        if (pos >= argc_ - 1) {
            logging::log("Argument missing for %s\n", arg_name.c_str());
            exit(1);
        }
        return getter(argv_[pos + 1]);
    } else {
        return def;
    }
}

template<class T>
T Args::do_get(
        Names names,
        T def,
        std::function<T(const char*)> getter) const {

    for (const auto& name : names) {
        if (has(name)) {
            return do_get(name, def, getter);
        }
    }
    return def;
}

int Args::arg_pos(const Name& arg_name) const {
    for (int pos = 1; pos < argc_; ++pos) {
        if (arg_name == argv_[pos]) {
            return pos;
        }
    }
    return -1;
}

int Args::arg_pos(Names names) const {
    for (const auto& name : names) {
        int pos = arg_pos(name);
        if (pos > 0) {
            return pos;
        }
    }
    return -1;
}



} // namespace emb
