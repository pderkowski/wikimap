#include <iterator>
#include <algorithm>
#include <iostream>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "word2vec.hpp"
#include "node2vec.hpp"
#include "io.hpp"
#include "defs.hpp"

namespace py = pybind11;

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
    using emb::Word2Vec;
    using emb::Node2Vec;
    using emb::Embeddings;
    using emb::Id;
    using emb::Edge;

    py::module m("embeddings");
    m.def("word2vec", [] (
            const std::string& input_file,
            const std::string& output_file) {

        auto w2v = Word2Vec<>();
        auto text = emb::read(input_file);
        emb::MemoryCorpus<> corpus(text.begin(), text.end());
        w2v.train(corpus);
        auto embeddings = w2v.get_embeddings();
        embeddings.save(output_file);
    });
    m.attr("DEFAULT_DIMENSION") = emb::def::DIMENSION;
    m.attr("DEFAULT_EPOCH_COUNT") = emb::def::EPOCHS;
    m.attr("DEFAULT_CONTEXT_SIZE") = emb::def::CONTEXT_SIZE;
    m.attr("DEFAULT_BACKTRACK_PROBABILITY") = emb::def::BACKTRACK_PROBABILITY;
    m.attr("DEFAULT_WALKS_PER_NODE") = emb::def::WALKS_PER_NODE;
    m.attr("DEFAULT_WALK_LENGTH") = emb::def::WALK_LENGTH;
    m.attr("DEFAULT_DYNAMIC_WINDOW") = emb::def::DYNAMIC_CONTEXT;
    m.attr("DEFAULT_VERBOSE") = emb::def::VERBOSE;

    py::class_<Embeddings<Id>>(m, "Embeddings")
        .def(py::init<>())
        .def("__iter__", [] (const Embeddings<Id>& self) {
            return py::make_iterator(self.begin(), self.end());
        }, py::keep_alive<0, 1>())
        .def("__getitem__", [] (const Embeddings<Id>& self, py::handle handle) {
            try {
                auto word = handle.cast<Id>();
                return self[word];
            } catch (const std::out_of_range& e) {
                throw py::key_error();
            } catch (const py::cast_error& e) {
                throw py::key_error();
            }
        })
        .def("__contains__", [] (const Embeddings<Id>& self, py::handle h) {
            try {
                auto word = h.cast<Id>();
                return self.has(word);
            } catch (const py::cast_error& e) {
                throw py::key_error();
            }
        })
        .def("save", &Embeddings<Id>::save)
        .def("load", &Embeddings<Id>::load)
        .def("words", &Embeddings<Id>::words);

    py::class_<Word2Vec<Id>>(m, "Word2Vec")
        .def(py::init<int, int, double, int, bool, int, bool, double>(),
            py::arg("dimension") = emb::def::DIMENSION,
            py::arg("epochs") = emb::def::EPOCHS,
            py::arg("learning_rate") = emb::def::LEARNING_RATE,
            py::arg("context_size") = emb::def::CONTEXT_SIZE,
            py::arg("dynamic_context") = emb::def::DYNAMIC_CONTEXT,
            py::arg("negative_samples") = emb::def::NEGATIVE_SAMPLES,
            py::arg("verbose") = emb::def::VERBOSE,
            py::arg("subsampling_factor") = emb::def::SUMBSAMPLING_FACTOR)
        .def("train", [] (Word2Vec<Id>& self, py::iterable iterable) {
            py::iterator it = py::iter(iterable);
            auto adapted_it = casting_iterator<py::iterator, std::vector<Id>>(
                it,
                [] (const py::handle& handle) {
                    auto sentence = handle.cast<py::iterable>();
                    std::vector<Id> sequence;
                    std::transform(py::iter(sentence), py::iterator::sentinel(),
                        std::back_inserter(sequence), [] (const py::handle& h) {
                            return h.cast<Id>();
                        });
                    return sequence;
                });

            emb::MemoryCorpus<Id> corpus(adapted_it, decltype(adapted_it)());
            self.train(corpus);
            return self.get_embeddings();
        });

    py::class_<Node2Vec>(m, "Node2Vec")
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
        .def("train", [] (Node2Vec& self, py::iterable iterable) {
            py::iterator it = py::iter(iterable);
            auto adapted_it = casting_iterator<py::iterator, Edge>(
                it,
                [] (const py::handle& handle) {
                    auto edge = handle.cast<py::tuple>();
                    return Edge(edge[0].cast<Id>(), edge[1].cast<Id>());
                });
            self.train(adapted_it, decltype(adapted_it)());
            return self.get_embeddings();
        });

    return m.ptr();
}

