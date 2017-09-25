#include <array>
#include <unordered_set>
#include <iterator>
#include <stdexcept>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "array.hpp"

namespace py = pybind11;


typedef std::pair<int, int> Edge;

template<class IteratorType, class TargetType>
class casting_iterator {
public:
    typedef TargetType value_type;
    typedef ptrdiff_t difference_type;
    typedef TargetType* pointer;
    typedef TargetType& reference;
    typedef std::input_iterator_tag iterator_category;

    typedef typename IteratorType::value_type source_type;

    casting_iterator()
    :   it_(), cast_()
    { }

    casting_iterator(
            IteratorType it,
            std::function<TargetType(const source_type&)> cast)

    :   it_(it), cast_(cast)
    { }

    casting_iterator(const casting_iterator& other)
    :   it_(other.it_), cast_(other.cast_)
    { }

    const value_type& operator*() const {
        *it_;
        value_ = cast_(*it_);
        return value_;
    }
    const value_type* operator->() const { value_ = cast_(*it_); return &value_; }

    casting_iterator& operator++() {
        ++it_;
        return *this;
    }

    casting_iterator operator++(int) {
        casting_iterator tmp = *this;
        ++*this;
        return tmp;
    }

    bool operator ==(const casting_iterator& other) { return it_ == other.it_; }
    bool operator !=(const casting_iterator& other) { return !(*this == other); }

private:
    IteratorType it_;
    std::function<TargetType(const source_type&)> cast_;
    mutable value_type value_;
};



Edge PyTupleToEdge(const py::handle& handle) {
    auto tuple = py::reinterpret_borrow<py::tuple>(handle);
    return Edge(tuple[0].cast<int>(), tuple[1].cast<int>());
}

// py::tuple EdgeToPyTuple(const Edge& edge) {
//     return py::make_tuple(edge[0], edge[1]);
// }

class EdgeArrayExt {
private:
    Array<Edge> array_;

public:
    typedef Array<Edge>::const_iterator const_iterator;

public:
    explicit EdgeArrayExt();

    void populate(py::iterable iterable);

    void append(const Edge& edge);
    void extend(py::iterable iterable);

    void save(const std::string& path);
    void load(const std::string& path);

    void sortByColumn(int column);
    void filterByNodes(py::iterable iterable);
    void filterColumnByNodes(py::iterable iterable, int column);
    void inverseEdges();
    void shuffle();

    int size();

    const_iterator begin() const;
    const_iterator end() const;
};

EdgeArrayExt::EdgeArrayExt()
: array_()
{ }

void EdgeArrayExt::populate(py::iterable iterable) {
    py::iterator it = py::iter(iterable);
    auto adapted_it = casting_iterator<py::iterator, Edge>(it, PyTupleToEdge);
    array_.assign(adapted_it, decltype(adapted_it)());
}

void EdgeArrayExt::append(const Edge& edge) {
    array_.append(edge);
}

void EdgeArrayExt::extend(py::iterable iterable) {
    py::iterator it = py::iter(iterable);
    auto adapted_it = casting_iterator<py::iterator, Edge>(it, PyTupleToEdge);
    array_.extend(adapted_it, decltype(adapted_it)());
}

EdgeArrayExt::const_iterator EdgeArrayExt::begin() const {
    return array_.begin();
}

EdgeArrayExt::const_iterator EdgeArrayExt::end() const {
    return array_.end();
}

void EdgeArrayExt::sortByColumn(int column) {
    if (column == 0) {
        array_.sort([] (const Edge& e1, const Edge& e2) {
            return e1.first < e2.first;
        });
    } else if (column == 1) {
        array_.sort([] (const Edge& e1, const Edge& e2) {
            return e1.second < e2.second;
        });
    } else {
        throw std::runtime_error("Invalid column number (must 0 or 1).");
    }
}

void EdgeArrayExt::filterByNodes(py::iterable iterable) {
    py::iterator it = py::iter(iterable);
    auto adapted_it = casting_iterator<py::iterator, int>(
        it,
        [] (const py::handle& handle) {
            return handle.cast<int>();
        });

    std::unordered_set<int> allowed(adapted_it, decltype(adapted_it)());
    array_.filter([&allowed] (const Edge& e) {
        return allowed.find(e.first) != allowed.end()
            && allowed.find(e.second) != allowed.end();
    });
}

void EdgeArrayExt::filterColumnByNodes(py::iterable iterable, int column) {
    py::iterator it = py::iter(iterable);
    auto adapted_it = casting_iterator<py::iterator, int>(
        it,
        [] (const py::handle& handle) {
            return handle.cast<int>();
        });

    std::unordered_set<int> allowed(adapted_it, decltype(adapted_it)());

    if (column == 0) {
        array_.filter([&allowed] (const Edge& e) {
            return allowed.find(e.first) != allowed.end();
        });
    } else if (column == 1) {
        array_.filter([&allowed] (const Edge& e) {
            return allowed.find(e.second) != allowed.end();
        });
    } else {
        throw std::runtime_error("Invalid column number (must 0 or 1).");
    }
}

void EdgeArrayExt::inverseEdges() {
    array_.for_each([] (Edge& e) {
        std::swap(e.first, e.second);
    });
}

void EdgeArrayExt::shuffle() {
    array_.shuffle();
}

int EdgeArrayExt::size() {
    return array_.size();
}

void EdgeArrayExt::save(const std::string& path) {
    array_.save(path);
}

void EdgeArrayExt::load(const std::string& path) {
    array_.load(path);
}

PYBIND11_PLUGIN(edgearrayext)
{
    py::module m("edgearrayext");
    py::class_<EdgeArrayExt>(m, "EdgeArrayExt")
        .def(py::init<>())
        .def("populate", &EdgeArrayExt::populate)
        .def("append", &EdgeArrayExt::append)
        .def("extend", &EdgeArrayExt::extend)
        .def("__iter__", [] (const EdgeArrayExt& self) {
            return py::make_iterator(self.begin(), self.end());
        }, py::keep_alive<0, 1>())
        .def("sortByColumn", &EdgeArrayExt::sortByColumn)
        .def("filterByNodes", &EdgeArrayExt::filterByNodes)
        .def("filterColumnByNodes", &EdgeArrayExt::filterColumnByNodes)
        .def("inverseEdges", &EdgeArrayExt::inverseEdges)
        .def("shuffle", &EdgeArrayExt::shuffle)
        .def("size", &EdgeArrayExt::size)
        .def("save", &EdgeArrayExt::save)
        .def("load", &EdgeArrayExt::load);

    return m.ptr();
}