#include <iterator>
#include <algorithm>
#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "word2vec.hpp"
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
    :   it_(),cast_()
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


PYBIND11_PLUGIN(word2vec) {
    py::module m("word2vec");
    m.def("word2vec", [] (
            const std::string& input_file,
            const std::string& output_file) {

        auto word2vec = w2v::Word2Vec<>();
        auto text_input = w2v::read(input_file);
        auto embeddings = word2vec.learn_embeddings(text_input);
        w2v::write(embeddings, output_file);
    });

    typedef w2v::Word2Vec<py::object> Word2Vec;

    py::class_<Word2Vec>(m, "Word2Vec")
        .def(py::init<int, int, double, int, bool, int, bool, double>(),
            py::arg("dimension") = w2v::def::DIMENSION,
            py::arg("epochs") = w2v::def::EPOCHS,
            py::arg("learning_rate") = w2v::def::LEARNING_RATE,
            py::arg("context_size") = w2v::def::CONTEXT_SIZE,
            py::arg("dynamic_context") = w2v::def::DYNAMIC_CONTEXT,
            py::arg("negative_samples") = w2v::def::NEGATIVE_SAMPLES,
            py::arg("verbose") = w2v::def::VERBOSE,
            py::arg("subsampling_factor") = w2v::def::SUMBSAMPLING_FACTOR)
        .def("learn_embeddings", [] (
                const Word2Vec& self,
                py::iterable iterable) {

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
            return self.learn_embeddings(adapted_it, decltype(adapted_it)());
        });

    return m.ptr();
}

