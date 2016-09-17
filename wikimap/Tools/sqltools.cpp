#include <string>
#include <vector>
#include <iostream>
#include <stdexcept>
#include <boost/python.hpp>
#include <algorithm>
#include <iterator>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include "Python.h"
#include "records.hpp"
#include "parser.hpp"

namespace py = boost::python;

template<typename T>
inline
std::vector<T> to_std_vector(const py::list& iterable) {
    return std::vector<T>(py::stl_input_iterator<T>(iterable), py::stl_input_iterator<T>());
}

py::object toPython(const std::string& s) {
    const char* c_s = s.c_str();
    const size_t s_size = s.size();
    const char* primaryEncoding = "utf8";
    const char* secondaryEncoding = "cp1252";
    const char* errors = "strict";

    auto converted = PyUnicode_Decode(c_s, s_size, primaryEncoding, errors);
    PyErr_Clear();

    if (!converted) {
        std::cerr << "Invalid utf8 encoding for: " << s << ", falling back to cp1252.\n";
        converted = PyUnicode_Decode(c_s, s_size, secondaryEncoding, errors);
        PyErr_Clear();

        if (converted) {
            std::cerr << "Succesfully decoded as cp1252.\n";
        } else {
            std::cerr << "Invalid cp1252 encoding, returning the incomplete utf8 version.\n";
            converted = PyUnicode_Decode(c_s, s_size, primaryEncoding, "ignore");
            PyErr_Clear();
        }
    }

    return py::object(py::handle<>(converted));
}

py::tuple toPython(const PageRecord& r) {
    return py::make_tuple(r.id, r.ns, toPython(r.title));
}

py::tuple toPython(const LinksRecord& r) {
    return py::make_tuple(r.from, r.ns, toPython(r.title), r.from_ns);
}

template<class T>
py::list toPython(const std::vector<T>& values) {
    py::list res;

    for (const auto& v : values) {
        res.append(toPython(v));
    }

    return res;
}

py::list getPageRecords(const std::string& s, const py::list& acceptedNamespaces) {
    auto accept = to_std_vector<INTEGER>(acceptedNamespaces);
    auto records = parse<PageRecord>(s);
    decltype(records) filtered;
    std::copy_if(records.begin(), records.end(), std::back_inserter(filtered),
        [&accept] (const decltype(records)::value_type& r) {
            return std::find(accept.begin(), accept.end(), r.ns) != accept.end();
        });

    return toPython(filtered);
}

py::list getLinksRecords(const std::string& s, const py::list& acceptedNamespaces) {
    auto accept = to_std_vector<INTEGER>(acceptedNamespaces);
    auto records = parse<LinksRecord>(s);
    decltype(records) filtered;
    std::copy_if(records.begin(), records.end(), std::back_inserter(filtered),
        [&accept] (const decltype(records)::value_type& r) {
            return std::find(accept.begin(), accept.end(), r.ns) != accept.end()
                && std::find(accept.begin(), accept.end(), r.from_ns) != accept.end();
        });

    return toPython(filtered);
}


BOOST_PYTHON_MODULE(libsqltools)
{
    py::def("getPageRecords", getPageRecords);
    py::def("getLinksRecords", getLinksRecords);
}