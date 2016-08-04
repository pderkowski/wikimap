#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>
#include <boost/python/suite/indexing/vector_indexing_suite.hpp>
#include "zoom.hpp"
#include "bounds.hpp"

namespace py = boost::python;

typedef std::vector<Point> PointList;

template<typename T>
inline
std::vector<T> to_std_vector(const py::list& iterable) {
    return std::vector<T>(py::stl_input_iterator<T>(iterable), py::stl_input_iterator<T>());
}

class ZoomWrapper {
public:
    ZoomWrapper(const py::list& points, int pointsPerTile)
    : zoom_(std::make_shared<Zoom>(to_std_vector<Point>(points), pointsPerTile))
    { }

    PointList getPoints(const Bounds& bounds, int zoomLevel) const {
        return zoom_->getPoints(bounds, zoomLevel);
    }

private:
    std::shared_ptr<Zoom> zoom_;
};


BOOST_PYTHON_MODULE(libzoompy) {
    py::class_<PointList>("PointList")
        .def(py::vector_indexing_suite<PointList>());

    py::class_<ZoomWrapper, boost::noncopyable>("Zoom", py::init<const py::list&, int>())
        .def("getPoints", &ZoomWrapper::getPoints);

    py::class_<Point>("Point", py::init<double, double>())
        .def_readwrite("x", &Point::x)
        .def_readwrite("y", &Point::y);

    py::class_<Bounds>("Bounds", py::init<const Point&, const Point&>());
}