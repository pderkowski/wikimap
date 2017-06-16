#include <iterator>
#include <algorithm>
#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "word2vec.hpp"
#include "node2vec.hpp"
#include "io.hpp"


namespace py = pybind11;

namespace std {

template<>
struct hash<py::object> {
    typedef py::object argument_type;
    typedef size_t result_type;

    result_type operator()(const argument_type& obj) const {
        static std::hash<result_type> cpp_hash;
        py::object hash_fun = obj.attr("__hash__");
        py::object hash_value = hash_fun();
        // python hash value is signed int, so we hash it to unsigned
        return cpp_hash(hash_value.cast<long long>());
    }
};

bool operator ==(const py::object& lhs, const py::object& rhs) {
    py::object eq_fun;
    if (py::hasattr(lhs, "__eq__")) {
        eq_fun = py::getattr(lhs, "__eq__");
        return eq_fun(rhs).cast<bool>();
    } else {
        eq_fun = py::getattr(lhs, "__cmp__");
        return (eq_fun(rhs).cast<int>() == 0);
    }
}


}

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


PYBIND11_PLUGIN(embeddings) {
    py::module m("embeddings");
    m.def("word2vec", [] (
            const std::string& input_file,
            const std::string& output_file) {

        auto w2v = emb::Word2Vec<>();
        auto text = emb::read(input_file);
        emb::MemoryCorpus<> corpus(text.begin(), text.end());
        w2v.train(corpus);
        auto embeddings = w2v.get_embeddings();
        emb::write(embeddings, output_file);
    });

    typedef emb::Word2Vec<py::object> Word2Vec;

    py::class_<Word2Vec>(m, "Word2Vec")
        .def(py::init<int, int, double, int, bool, int, bool, double>(),
            py::arg("dimension") = emb::def::DIMENSION,
            py::arg("epochs") = emb::def::EPOCHS,
            py::arg("learning_rate") = emb::def::LEARNING_RATE,
            py::arg("context_size") = emb::def::CONTEXT_SIZE,
            py::arg("dynamic_context") = emb::def::DYNAMIC_CONTEXT,
            py::arg("negative_samples") = emb::def::NEGATIVE_SAMPLES,
            py::arg("verbose") = emb::def::VERBOSE,
            py::arg("subsampling_factor") = emb::def::SUMBSAMPLING_FACTOR)
        .def("train", [] (Word2Vec& self, py::iterable iterable) {
            py::iterator it = py::iter(iterable);
            auto adapted_it = casting_iterator<py::iterator, std::vector<py::object>>(
                it,
                [] (const py::handle& handle) {
                    auto sentence = handle.cast<py::iterable>();
                    std::vector<py::object> sequence;
                    std::transform(py::iter(sentence), py::iterator::sentinel(),
                        std::back_inserter(sequence), [] (const py::handle& h) {
                            return h.cast<py::object>();
                        });
                    return sequence;
                });

            emb::MemoryCorpus<py::object> corpus(
                adapted_it,
                decltype(adapted_it)());

            self.train(corpus);
        })
        .def("__iter__", [] (const Word2Vec& self) {
            return py::make_iterator(self.begin(), self.end());
        }, py::keep_alive<0, 1>());

    py::class_<emb::Node2Vec>(m, "Node2Vec")
        .def(py::init<double, int, int, int, int, double, int, bool, int, bool, double>(),
            py::arg("backtrack_probability") = emb::def::BACKTRACK_PROBABILITY,
            py::arg("walk_length") = emb::def::WALK_LENGTH,
            py::arg("walks_per_node") = emb::def::WALKS_PER_NODE,
            py::arg("dimension") = emb::def::DIMENSION,
            py::arg("epochs") = emb::def::EPOCHS,
            py::arg("learning_rate") = emb::def::LEARNING_RATE,
            py::arg("context_size") = emb::def::CONTEXT_SIZE,
            py::arg("dynamic_context") = emb::def::DYNAMIC_CONTEXT,
            py::arg("negative_samples") = emb::def::NEGATIVE_SAMPLES,
            py::arg("verbose") = emb::def::VERBOSE,
            py::arg("subsampling_factor") = emb::def::SUMBSAMPLING_FACTOR)
        .def("train", [] (emb::Node2Vec& self, py::iterable iterable) {
            py::iterator it = py::iter(iterable);
            auto adapted_it = casting_iterator<py::iterator, emb::Edge>(
                it,
                [] (const py::handle& handle) {
                    auto edge = handle.cast<py::tuple>();
                    return emb::Edge(
                        edge[0].cast<emb::Id>(),
                        edge[1].cast<emb::Id>());
                });
            self.train(adapted_it, decltype(adapted_it)());
        })
        .def("__iter__", [] (const emb::Node2Vec& self) {
            return py::make_iterator(self.begin(), self.end());
        }, py::keep_alive<0, 1>());

    return m.ptr();
}

