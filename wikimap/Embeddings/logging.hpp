#pragma once

#include <cstdarg>
#include <cstdio>
#include <ctime>


namespace emb {

namespace logging {


clock_t last_log = 0;

inline void clear_line() {
    fprintf(stderr, "\r");
}

inline void newline() {
    fprintf(stderr, "\n");
    fflush(stderr);
    last_log = std::clock();
}

inline void log_prefix() {
    static char time_buf[100];
    time_t rawtime;
    time(&rawtime);
    strftime(time_buf, sizeof(time_buf), "%H:%M:%S", localtime(&rawtime));
    fprintf(stderr, "[word2vec](%s): ", time_buf);
}

inline void log(const char* format, ...) {
    log_prefix();
    va_list arglist;
    va_start(arglist, format);
    vfprintf(stderr, format, arglist);
    va_end(arglist);
    fflush(stderr);
    last_log = std::clock();
}

inline void inline_log(const char* format, ...) {
    clear_line();
    log_prefix();
    va_list arglist;
    va_start(arglist, format);
    vfprintf(stderr, format, arglist);
    va_end(arglist);
    fflush(stderr);
    last_log = std::clock();
}



//simple, not necessarily accurate
inline double time_since_last_log() {
    clock_t now = std::clock();
    double elapsed_secs = static_cast<double>(now - last_log) / CLOCKS_PER_SEC;
    return elapsed_secs;
}


} // namespace logging

} // namespace emb