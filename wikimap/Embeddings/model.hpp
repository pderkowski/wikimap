#pragma once

#include <random>
#include <memory>

#include <omp.h>

#include "defs.hpp"
#include "utils.hpp"
#include "vector_ops.hpp"


namespace emb {


class View;

class ConstView {
public:
    ConstView(const Float* data, Int size, Float multiplier);
    ConstView(const Float* data, Int size);
    ConstView(const View& view);

    Float operator [] (Int index) const { return data_[index] * multiplier_; }

    Int size() const { return size_; }

    friend ConstView operator * (Float multiplier, const ConstView& v);
    friend ConstView operator * (const ConstView& v, Float multiplier);
    friend class View;

    explicit operator Embedding () const;

private:
    const Float* data_;
    Int size_;

    Float multiplier_;
};

class View {
public:
    View(Float* data, Int size);

    Float& operator [] (Int index) { return data_[index]; }
    const Float& operator [] (Int index) const { return data_[index]; }

    Int size() const { return size_; }

    friend ConstView operator * (Float multiplier, const View& v);
    friend ConstView operator * (const View& v, Float multiplier);
    friend class ConstView;

    explicit operator Embedding () const;

private:
    Float* data_;
    Int size_;
};

ConstView::ConstView(const Float* data, Int size, Float multiplier)
:   data_(data), size_(size), multiplier_(multiplier)
{ }

ConstView::ConstView(const Float* data, Int size)
:   ConstView(data, size, 1.)
{ }

ConstView::ConstView(const View& view)
:   ConstView(view.data_, view.size_)
{ }

ConstView::operator Embedding () const {
    Embedding res(size_);
    for (Int i = 0; i < size_; ++i) {
        res[i] = (*this)[i];
    }
    return res;
}

View::View(Float* data, Int size)
:   data_(data), size_(size)
{ }

View::operator Embedding () const {
    Embedding res(size_);
    for (Int i = 0; i < size_; ++i) {
        res[i] = (*this)[i];
    }
    return res;
}

inline ConstView operator * (Float multiplier, const View& v) {
    return ConstView(v.data_, v.size_, multiplier);
}

inline ConstView operator * (const View& v, Float multiplier) {
    return ConstView(v.data_, v.size_, multiplier);
}

inline ConstView operator * (Float multiplier, const ConstView& v) {
    return v * multiplier;
}

inline ConstView operator * (const ConstView& v, Float multiplier) {
    ConstView copy(v);
    copy.multiplier_ *= multiplier;
    return copy;
}


class Model {
public:
    Model();

    void resize(Int rows, Int cols);
    void init();
    void normalize();

    View word_embedding(Int index);
    ConstView word_embedding(Int index) const;

    View context_embedding(Int index);
    ConstView context_embedding(Int index) const;

    Int rows() const { return rows_; }
    Int cols() const { return cols_; }

    Int estimate_size_mb(Int rows, Int cols) const;

    void free_context_embeddings();

    std::vector<Float> copy_word_embeddings() const;

private:
    void init_word_embeddings();
    void init_context_embeddings();

    View get_row(Int index, Float* matrix);
    ConstView get_row(Int index, const Float* matrix) const;

    Int rows_;
    Int cols_;
    Int size_;

    std::unique_ptr<Float[]> word_embeddings_;
    std::unique_ptr<Float[]> context_embeddings_;
};

Model::Model()
:   rows_(0), cols_(0), size_(0),
    word_embeddings_(nullptr), context_embeddings_(nullptr)
{ }

void Model::resize(Int rows, Int cols) {
    rows_ = rows;
    cols_ = cols;
    size_ = rows * cols;
    word_embeddings_.reset(new Float[size_]);
    context_embeddings_.reset(new Float[size_]);
}

void Model::init() {
    init_word_embeddings();
    init_context_embeddings();
}

void Model::normalize() {
    #pragma omp parallel for schedule(static)
    for (Int i = 0; i < rows_; ++i) {
        vec::normalize(word_embedding(i));
        vec::normalize(context_embedding(i));
    }
}

Int Model::estimate_size_mb(Int rows, Int cols) const {
    return 2L * rows * cols * sizeof(Float) / 1000000;
}

inline View Model::word_embedding(Int index) {
    return get_row(index, word_embeddings_.get());
}

inline ConstView Model::word_embedding(Int index) const {
    return get_row(index, word_embeddings_.get());
}

inline View Model::context_embedding(Int index) {
    return get_row(index, context_embeddings_.get());
}

inline ConstView Model::context_embedding(Int index) const {
    return get_row(index, context_embeddings_.get());
}

inline View Model::get_row(Int index, Float* matrix) {
    return View(matrix + index * cols_, cols_);
}

inline ConstView Model::get_row(Int index, const Float* matrix) const {
    return ConstView(matrix + index * cols_, cols_);
}

void Model::init_word_embeddings() {
    std::uniform_real_distribution<Float> dist(-0.5, 0.5);
    #pragma omp parallel for schedule(static)
    for (Int i = 0; i < size_; ++i) {
        word_embeddings_[i] = dist(Random::global_rng()) / cols_;
    }
}

void Model::init_context_embeddings() {
    #pragma omp parallel for schedule(static)
    for (Int i = 0; i < size_; ++i) {
        context_embeddings_[i] = 0;
    }
}

void Model::free_context_embeddings() {
    context_embeddings_.reset();
}

std::vector<Float> Model::copy_word_embeddings() const {
    return std::vector<Float>(
        word_embeddings_.get() + 0,
        word_embeddings_.get() + size_);
}


} // namespace emb
