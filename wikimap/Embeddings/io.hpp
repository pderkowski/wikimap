#pragma once

#include <cstddef>
#include <vector>
#include <fstream>

#include "defs.hpp"
#include "utils.hpp"


namespace w2v {

namespace io {

const int MAX_WORD_SIZE = 100;
const int MAX_SENTENCE_SIZE = 1000;


std::ifstream::pos_type estimate_file_size_mb(const std::string& fname)
{
    std::ifstream in(fname.c_str(), std::ifstream::ate | std::ifstream::binary);
    auto fsize =in.tellg();
    return fsize / 1000000;
}

bool read_newline(FILE* in) {
    while (true) {
        int c = getc(in);
        if (c == '\n') {
            return true;
        } else if (!isspace(c)) {
            ungetc(c, in);
            return false;
        } // else: whitespace, keep looking
    }
}

void skip_chars_over_limit(FILE* in) {
    int c;
    while (isalnum(c = getc(in)))
        ;

    ungetc(c, in);
}

int read_word(FILE* in, std::string& word) {
    static char buffer[MAX_WORD_SIZE + 1];
    static std::string fmt = " %" + std::to_string(MAX_WORD_SIZE) + "s";

    int ret = fscanf(in, fmt.c_str(), buffer);
    if (ret == 1) {
        word = buffer;
        skip_chars_over_limit(in);
    }
    return ret;
}

int read_sentence(FILE* in, std::vector<std::string>& sentence) {
    sentence.clear();
    std::string word;

    for (int words = 0; words < MAX_SENTENCE_SIZE; ++words) {
        // if there is a newline next in stream, end sentence
        if (read_newline(in)) {
            return 1;
        } else {
            // otherwise read word
            int rw = read_word(in, word);
            if (rw == 1) {
                // if there was a word, add it to the sentence
                sentence.push_back(word);
            } else if (rw == -1) {
                // otherwise it must have been the end of input
                // if there are already words in the sentence, return it (next one will fail)
                if (sentence.size() > 0) {
                    return 1;
                } else {
                    // no words in the sentence and EOF seen - nothing to return and nothing more to see
                    return EOF;
                }
            }// else: rw == 0 should not happen ?
        }
    }
    // maximum number of words reached
    return 1;
}


} // namespace io


class TextInput {
public:
    class iterator;

    TextInput(const std::string& fname) {
        in_ = (fname == "stdin")? stdin : fopen(fname.c_str(), "r");
        if (in_ == NULL) {
            logging::log("Could not open `%s`\n", fname.c_str());
            exit(1);
        }
    }

    iterator begin() const { return iterator(in_); }
    iterator end() const { return iterator(); }

    class iterator {
    public:
        typedef std::vector<std::string> value_type;
        typedef ptrdiff_t difference_type;
        typedef std::vector<std::string>* pointer;
        typedef std::vector<std::string>& reference;
        typedef std::input_iterator_tag iterator_category;

        iterator()
        :   in_(NULL)
        { }

        iterator(FILE* in)
        :   in_(in)
        { ++*this; }

        iterator(const iterator& other)
        :   in_(other.in_), value_(other.value_)
        { }

        const value_type& operator*() const { return value_; }
        const value_type* operator->() const { return &value_; }

        iterator& operator++() {
            if (in_ && io::read_sentence(in_, value_) == EOF) {
                in_ = NULL;
            }
            return *this;
        }

        iterator operator++(int) {
            iterator tmp = *this;
            ++*this;
            return tmp;
        }

        friend bool operator ==(const iterator& lhs, const iterator& rhs);
        friend bool operator !=(const iterator& lhs, const iterator& rhs);

    private:
        FILE* in_;
        value_type value_;
    };

private:
    FILE* in_;
};

bool operator ==(const TextInput::iterator& lhs, const TextInput::iterator& rhs) {
    return lhs.in_ == rhs.in_;
}

bool operator !=(const TextInput::iterator& lhs, const TextInput::iterator& rhs) {
    return !(lhs == rhs);
}


TextInput read(const std::string& fname, bool verbose = def::VERBOSE) {
    if (verbose) {
        std::string message("Reading data from `" + fname + "`\n");
        logging::log(message.c_str());
        logging::log("- max word size: %d\n", io::MAX_WORD_SIZE);
        logging::log("- max sentence size: %d\n", io::MAX_SENTENCE_SIZE);
    }
    return TextInput(fname);
}

void write(
        const Embeddings<std::string>& embeddings,
        const std::string& fname,
        bool binary = def::BINARY,
        bool verbose = def::VERBOSE) {

    if (verbose) {
        std::string message("Writing embeddings to `" + fname + "`\n");
        logging::log(message.c_str());
    }

    FILE* out = (fname == "stdout")? stdout : fopen(fname.c_str(), "w");
    if (out == NULL) {
        logging::log("Could not open `%s`\n", fname.c_str());
        exit(1);
    }

    size_t dimension;
    if (!embeddings.empty()) {
        dimension = embeddings.begin()->second.size();

        fprintf(out, "%lu %lu\n", embeddings.size(), dimension);

        for (const auto& word_embedding : embeddings) {
            const auto& word = word_embedding.first;
            const auto& embedding = word_embedding.second;

            fprintf(out, "%s ", word.c_str());
            if (binary) {
                typedef Embedding::value_type value_type;
                fwrite(embedding.data(), sizeof(value_type), dimension, out);
            } else {
                for (size_t i = 0; i < dimension; ++i) {
                    fprintf(out, "%f ", embedding[i]);
                }
            }
            fprintf(out, "\n");
        }
    } else {
        dimension = 0;
        fprintf(out, "0 0\n");
    }

    if (verbose) {
        logging::log("- saved %d embeddings\n", embeddings.size());
        if (binary) {
            logging::log("- binary format\n");
        } else {
            logging::log("- text format\n");
        }
        logging::log("- file size %dMB\n", io::estimate_file_size_mb(fname));
    }
}


} // namespace w2v
