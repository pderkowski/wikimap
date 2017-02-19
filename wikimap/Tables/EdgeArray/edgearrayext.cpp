#include "array.hpp"
#include <array>
#include <unordered_set>
#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>
#include <boost/iterator/transform_iterator.hpp>

namespace py = boost::python;

typedef std::array<int, 2> Edge;

Edge PyTupleToEdge(py::tuple tuple) {
    return Edge{py::extract<int>(tuple[0]), py::extract<int>(tuple[1])};
}

py::tuple EdgeToPyTuple(const Edge& edge) {
    return py::make_tuple(edge[0], edge[1]);
}

py::str EdgeToPyStr(const Edge& edge) {
    std::string res(std::to_string(edge[0]));
    res += " ";
    res += std::to_string(edge[1]);
    res += "\n";
    return py::str(res);
}

class EdgeArrayExt {
private:
    Array<Edge> array_;

public:
    typedef decltype(boost::make_transform_iterator(array_.begin(), EdgeToPyTuple)) iterator;
    typedef decltype(boost::make_transform_iterator(array_.begin(), EdgeToPyStr)) strIterator;

public:
    explicit EdgeArrayExt();

    void populate(py::object iterator);

    void save(py::str path);
    void load(py::str path);

    void sortByColumn(int column);
    void filterByNodes(py::object iterable);
    void inverseEdges();
    void shuffle();

    int size();

    iterator begin();
    iterator end();

    strIterator strBegin();
    strIterator strEnd();
};

EdgeArrayExt::EdgeArrayExt()
: array_()
{ }

void EdgeArrayExt::populate(py::object iterator) {
    py::stl_input_iterator<py::tuple> pybegin(iterator), pyend;
    auto begin = boost::make_transform_iterator(pybegin, PyTupleToEdge);
    auto end = boost::make_transform_iterator(pyend, PyTupleToEdge);
    array_.assign(begin, end);
}

EdgeArrayExt::iterator EdgeArrayExt::begin() {
    return boost::make_transform_iterator(array_.begin(), EdgeToPyTuple);
}

EdgeArrayExt::iterator EdgeArrayExt::end() {
    return boost::make_transform_iterator(array_.end(), EdgeToPyTuple);
}

EdgeArrayExt::strIterator EdgeArrayExt::strBegin() {
    return boost::make_transform_iterator(array_.begin(), EdgeToPyStr);
}

EdgeArrayExt::strIterator EdgeArrayExt::strEnd() {
    return boost::make_transform_iterator(array_.end(), EdgeToPyStr);
}

void EdgeArrayExt::sortByColumn(int column) {
    array_.sort([column] (const Edge& e1, const Edge& e2) {
        return e1[column] < e2[column];
    });
}

void EdgeArrayExt::filterByNodes(py::object iterable) {
    auto begin = py::stl_input_iterator<int>(iterable);
    auto end = py::stl_input_iterator<int>();

    std::unordered_set<int> allowed(begin, end);
    array_.filter([&allowed] (const Edge& e) {
        return allowed.find(e[0]) != allowed.end() && allowed.find(e[1]) != allowed.end();
    });
}

void EdgeArrayExt::inverseEdges() {
    array_.for_each([] (Edge& e) {
        std::swap(e[0], e[1]);
    });
}

void EdgeArrayExt::shuffle() {
    array_.shuffle();
}

int EdgeArrayExt::size() {
    return array_.size();
}

void EdgeArrayExt::save(py::str path) {
    array_.save(py::extract<std::string>(path));
}

void EdgeArrayExt::load(py::str path) {
    array_.load(py::extract<std::string>(path));
}

BOOST_PYTHON_MODULE(edgearrayext)
{
    py::class_<EdgeArrayExt>("EdgeArrayExt")
        .def("populate", &EdgeArrayExt::populate)
        .def("__iter__", py::iterator<EdgeArrayExt>())
        .def("iterStrings", py::range(&EdgeArrayExt::strBegin, &EdgeArrayExt::strEnd))
        .def("sortByColumn", &EdgeArrayExt::sortByColumn)
        .def("filterByNodes", &EdgeArrayExt::filterByNodes)
        .def("inverseEdges", &EdgeArrayExt::inverseEdges)
        .def("shuffle", &EdgeArrayExt::shuffle)
        .def("size", &EdgeArrayExt::size)
        .def("save", &EdgeArrayExt::save)
        .def("load", &EdgeArrayExt::load);
}