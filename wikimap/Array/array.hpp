#pragma once

#include <string>
#include <vector>
#include <fstream>
#include <iterator>
#include <iostream>
#include <functional>
#include <algorithm>
#include <omp.h>
#include <parallel/algorithm>

template<class T>
class Array {
public:
    typedef typename std::vector<T>::size_type size_type;
    typedef typename std::vector<T>::iterator iterator;
    typedef typename std::vector<T>::const_iterator const_iterator;
    typedef typename std::vector<T>::value_type value_type;

public:
    Array();

    void append(const T& val);

    template<class InputIterator>
    void assign(InputIterator begin, InputIterator end);

    void save(const std::string& path) const;
    void load(const std::string& path);

    bool operator == (const Array<T>& other) const;
    bool operator != (const Array<T>& other) const { return !(*this == other); }

    T& operator [] (size_type index) { return data_[index]; }
    const T& operator [] (size_type index) const { return data_[index]; }

    size_type size() const { return data_.size(); }

    std::ostream& print(std::ostream& out) const;

    void filter(std::function<bool(const T&)> predicate);
    void shuffle();
    void sort(std::function<bool(const T&, const T&)> comparator = std::less<T>());
    void reverse();
    void for_each(std::function<void(T&)> fun);

    iterator begin();
    const_iterator begin() const;

    iterator end();
    const_iterator end() const;

private:
    std::vector<T> data_;
};

template<class T>
Array<T>::Array()
: data_()
{ }

template<class T>
void Array<T>::append(const T& val) {
    data_.push_back(val);
}

template<class T>
template<class InputIterator>
void Array<T>::assign(InputIterator begin, InputIterator end) {
    data_.assign(begin, end);
}

template<class T>
void Array<T>::save(const std::string& path) const {
    std::ofstream outfile(path.c_str(), std::ios::out | std::ios::binary);
    size_type size = data_.size();
    // std::cerr << sizeof(size) << "\n";
    outfile.write((char*)&size, sizeof(size));
    if (data_.size() > 0) {
        outfile.write((char*)data_.data(), sizeof(data_[0]) * data_.size());
    }
}

template<class T>
void Array<T>::load(const std::string& path) {
    std::ifstream infile(path.c_str(), std::ios::in | std::ios::binary);
    size_type size;
    infile.read((char*)&size, sizeof(size));
    // std::cerr << size << "\n";
    data_.resize(size);
    value_type value_type;
    infile.read((char*)data_.data(), sizeof(value_type) * size);
}

template<class T>
bool Array<T>::operator == (const Array<T>& other) const {
    return data_ == other.data_;
}

template<class T>
void Array<T>::filter(std::function<bool(const T&)> predicate) {
    std::vector<short> mask(data_.size(), 0);

#pragma omp parallel for schedule(static)
    for (int i = 0; i < data_.size(); ++i) {
        mask[i] = (short)predicate(data_[i]);
    }

    int next = 0;
    for (int i = 0; i < data_.size(); ++i) {
        if (mask[i]) {
            data_[next++] = data_[i];
        }
    }
    data_.resize(next);
}

template<class T>
void Array<T>::shuffle() {
    __gnu_parallel::random_shuffle(data_.begin(), data_.end());
}

template<class T>
void Array<T>::sort(std::function<bool(const T&, const T&)> comparator) {
    __gnu_parallel::sort(data_.begin(), data_.end(), comparator);
}

template<class T>
void Array<T>::reverse() {
    const auto mid = data_.size() / 2;
    const auto size = data_.size();
#pragma omp parallel for schedule(static)
    for (int i = 0; i < mid; ++i) {
        std::swap(data_[i], data_[size - 1 - i]);
    }
}

template<class T>
void Array<T>::for_each(std::function<void(T&)> fun) {
    __gnu_parallel::for_each(data_.begin(), data_.end(), fun);
}

template<class T>
typename Array<T>::iterator Array<T>::begin() {
    return data_.begin();
}

template<class T>
typename Array<T>::const_iterator Array<T>::begin() const {
    return data_.begin();
}

template<class T>
typename Array<T>::iterator Array<T>::end() {
    return data_.end();
}

template<class T>
typename Array<T>::const_iterator Array<T>::end() const {
    return data_.end();
}

template<class T>
std::ostream& Array<T>::print(std::ostream& out) const {
    out << "[";
    for (int i = 0; i < data_.size() - 1; ++i) {
        out << data_[i] << " ";
    }
    if (data_.size() > 0) {
        out << data_.back();
    }
    out << "]";
    return out;
}
