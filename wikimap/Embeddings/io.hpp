#pragma once

#include <sys/stat.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>

#include <cstddef>
#include <vector>
#include <fstream>

#include "defs.hpp"
#include "utils.hpp"


namespace emb {

namespace io {


const int MAX_WORD_SIZE = 100;
const int MAX_SENTENCE_SIZE = 1000;


inline size_t get_file_size(const std::string& fname) {
    struct stat st;
    stat(fname.c_str(), &st);
    return st.st_size;
}

inline size_t get_file_size_mb(const std::string& fname) {
    return get_file_size(fname) / 1000000;
}

inline FILE* open_out_file(const std::string& fname) {
    FILE* out = fopen(fname.c_str(), "w");
    if (out == NULL) {
        logging::log("Could not open `%s`\n", fname.c_str());
        exit(1);
    }
    return out;
}

inline FILE* open_in_file(const std::string& fname) {
    FILE* in = fopen(fname.c_str(), "r");
    if (in == NULL) {
        logging::log("Could not open `%s`\n", fname.c_str());
        exit(1);
    }
    return in;
}

inline void close_file(FILE* out) {
    fclose(out);
}

inline void write_header(size_t size, int dimension, FILE* out) {
    fprintf(out, "%lu %d\n", size, dimension);
}

inline void read_header(FILE* in, size_t& size, int& dimension) {
    fscanf(in, "%lu %d\n", &size, &dimension);
}

inline void write_word(const std::string& word, FILE* out) {
    fprintf(out, "%s ", word.c_str());
}

inline void write_word(Id word, FILE* out) {
    fprintf(out, "%d ", word);
}

inline void read_word(FILE* in, std::string& word) {
    static char buf[MAX_WORD_SIZE + 1];
    fscanf(in, "%s", buf);
    fgetc(in); // skip EXACTLY ONE space
    word = buf;
}

inline void read_word(FILE* in, Id& word) {
    fscanf(in, "%d", &word);
    fgetc(in); // skip EXACTLY ONE space
}

inline void read_embedding(FILE* in, int dimension, Embedding& embedding) {
    embedding.clear();
    embedding.resize(dimension);
    auto value_size = sizeof(Embedding::value_type);
    fread((void*)embedding.data(), value_size, dimension, in);
}

inline void write_embedding(const Embedding& embedding, FILE* out) {
    auto value_size = sizeof(Embedding::value_type);
    fwrite((void*)embedding.data(), value_size, embedding.size(), out);
    fprintf(out, "\n");
}

class MmappedFile {
public:
    MmappedFile(const std::string& fname)
    :   fd_(open(fname.c_str(), O_RDONLY, 0)),
        size(get_file_size(fname)),
        data((char*)mmap(NULL, size, PROT_READ, MAP_PRIVATE | MAP_POPULATE, fd_, 0))
    { }

    ~MmappedFile() {
        munmap(data, size);
        close(fd_);
    }

private:
    int fd_;

public:
    size_t size;
    char* data;
};


} // namespace io


} // namespace emb
