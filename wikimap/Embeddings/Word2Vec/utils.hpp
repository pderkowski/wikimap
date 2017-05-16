#pragma once

#include <cstdarg>
#include <cstdio>
#include <random>
#include <vector>
#include <iterator>

#include <omp.h>

#include "defs.hpp"


namespace w2v {


inline void log(const char *format, ...) {
    va_list arglist;
    va_start(arglist, format);
    vprintf(format, arglist);
    va_end(arglist);
    fflush(stdout);
}

inline void report_progress(Int seen, Int expected) {
    w2v::log("\rProgress: %.2lf%% ", seen*100. / expected);
}


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
            log("Argument missing for %s\n", arg_name.c_str());
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
            log("Argument missing for %s\n", arg_name.c_str());
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
            log("Argument missing for %s\n", arg_name.c_str());
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


template<class Container>
void tokenize(const std::string& str, Container& tokens,
              const std::string& delimiters = " ", bool trimEmpty = true)
{
    std::string::size_type pos, lastPos = 0, length = str.length();

    using value_type = typename Container::value_type;
    using size_type  = typename Container::size_type;

    while(lastPos < length + 1)
    {
        pos = str.find_first_of(delimiters, lastPos);
        if(pos == std::string::npos) {
            pos = length;
        }

        if(pos != lastPos || !trimEmpty)
            tokens.push_back(value_type(str.data()+lastPos,
               (size_type)pos-lastPos));

        lastPos = pos + 1;
    }
}


class Text {
public:
    typedef std::vector<std::string> Sentence;
    typedef std::istream_iterator<Sentence> iterator;

    Text(std::istream& input);

    iterator begin() const;
    iterator end() const;

private:
    Text(const Text&) = delete;
    Text operator = (const Text&) = delete;

    std::istream& input_;
};


Text::Text(std::istream& input)
:   input_(input)
{ }

Text::iterator Text::begin() const {
    return iterator(input_);
}

Text::iterator Text::end() const {
    return iterator();
}



}

namespace std {


std::istream& operator >> (std::istream& input, w2v::Text::Sentence& sentence) {
    std::string line;
    std::getline(input, line);
    sentence.clear();
    w2v::tokenize(line, sentence);
    return input;
}


}