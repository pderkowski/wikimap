#include <string>
#include <vector>
#include <iostream>
#include <stdexcept>
#include <algorithm>
#include <iterator>
#include "Python.h"

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "records.hpp"
#include "parser.hpp"

namespace py = pybind11;

py::str toPython(const std::string& s) {
    const char* c_s = s.c_str();
    const size_t s_size = s.size();
    const char* primaryEncoding = "utf8";
    const char* secondaryEncoding = "cp1252";
    const char* errors = "strict";

    py::handle converted = PyUnicode_Decode(c_s, s_size, primaryEncoding, errors);
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

    return py::reinterpret_steal<py::str>(converted);
}

py::tuple toPython(const PageRecord& r) {
    return py::make_tuple(r.id, r.ns, toPython(r.title));
}

py::tuple toPython(const LinksRecord& r) {
    return py::make_tuple(r.from, r.ns, toPython(r.title), r.from_ns);
}

py::tuple toPython(const CategoryRecord& r) {
    return py::make_tuple(r.id, toPython(r.title));
}

py::tuple toPython(const CategoryLinksRecord& r) {
    return py::make_tuple(r.from, toPython(r.to));
}

template<class T>
py::list toPython(const std::vector<T>& values) {
    py::list res;

    for (const auto& v : values) {
        res.append(toPython(v));
    }

    return res;
}

py::list getPageRecords(py::bytes bytes) {
    auto s = static_cast<std::string>(bytes);
    auto records = parse<PageRecord>(s);
    decltype(records) filtered;
    std::copy_if(records.begin(), records.end(), std::back_inserter(filtered),
        [] (const decltype(records)::value_type& r) {
            return r.ns == 0 || r.ns == 14;
        });

    return toPython(filtered);
}

py::list getLinksRecords(py::bytes bytes) {
    auto s = static_cast<std::string>(bytes);
    auto records = parse<LinksRecord>(s);
    decltype(records) filtered;
    std::copy_if(records.begin(), records.end(), std::back_inserter(filtered),
        [] (const decltype(records)::value_type& r) {
            return r.ns == 0 && r.from_ns == 0;
        });

    return toPython(filtered);
}

py::list getCategoryRecords(py::bytes bytes) {
    auto s = static_cast<std::string>(bytes);
    return toPython(parse<CategoryRecord>(s));
}

py::list getCategoryLinksRecords(py::bytes bytes) {
    auto s = static_cast<std::string>(bytes);
    return toPython(parse<CategoryLinksRecord>(s));
}

const auto& getPagePropertiesRecords = getCategoryLinksRecords;
const auto& getRedirectsRecords = getPageRecords;

PYBIND11_PLUGIN(sqltools)
{
    py::module m("sqltools");
    m.def("getPageRecords", getPageRecords);
    m.def("getLinksRecords", getLinksRecords);
    m.def("getCategoryRecords", getCategoryRecords);
    m.def("getCategoryLinksRecords", getCategoryLinksRecords);
    m.def("getPagePropertiesRecords", getPagePropertiesRecords);
    m.def("getRedirectsRecords", getRedirectsRecords);

    return m.ptr();
}