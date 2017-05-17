#pragma once

#include <cstdarg>
#include <cstdio>
#include <ctime>


namespace w2v {

namespace logging {


inline void clear_line() {
    fprintf(stderr, "\r");
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
    fflush(stdout);
}

inline void inline_log(const char* format, ...) {
    clear_line();
    log_prefix();
    va_list arglist;
    va_start(arglist, format);
    vfprintf(stderr, format, arglist);
    va_end(arglist);
    fflush(stdout);
}


} // namespace logging

} // namespace w2v