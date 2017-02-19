#include "array.hpp"
#include <chrono>
#include <iostream>
#include <functional>
#include <cstdio>
#include <algorithm>

const int bigSize = 409000000;

void check(const std::string& message, bool assertion) {
    if (assertion) {
        std::cerr << "[PASS] " << message << " " << std::flush;
    } else {
        std::cerr << "[FAIL] " << message << " " << std::flush;
    }
}

int countValuesIn(int maxValue, const Array<int>& a) {
    std::vector<bool> mask(maxValue, false);
    for (auto e : a) {
        if (e >= 0 && e < mask.size())
            mask[e] = true;
    }
    return std::count(mask.begin(), mask.end(), true);
}

class Timer {
private:
    typedef std::chrono::high_resolution_clock Clock;
    typedef std::chrono::time_point<Clock> TimePoint;
    typedef std::chrono::milliseconds MilliSec;
    typedef std::chrono::duration<float> Duration;

public:
    explicit Timer(bool autostart = true, bool autoreport = true);
    ~Timer();

    Timer(const Timer& other) = delete;
    Timer& operator = (const Timer& other) = delete;

    void start();
    void stop();
    void report() const;

private:
    bool autoreport_;
    bool stopped_;
    TimePoint last_;
    MilliSec total_;
};

Timer::Timer(bool autostart, bool autoreport)
: autoreport_(autoreport), stopped_(true), last_(), total_(0)
{
    if (autostart) {
        start();
    }
}

Timer::~Timer() {
    stop();
    if (autoreport_) {
        report();
    }
}

void Timer::start() {
    if (stopped_) {
        last_ = Clock::now();
        stopped_ = false;
    }
}

void Timer::stop() {
    if (!stopped_) {
        auto now = Clock::now();
        Duration d = now - last_;
        total_ += std::chrono::duration_cast<MilliSec>(d);
    }
}

void Timer::report() const {
    std::cerr << total_.count() << "ms\n" << std::flush;
}


Array<int> getArray(int size) {
    Array<int> arr;
    for (int i = 0; i < size; ++i) {
        arr.append(i);
    }
    return arr;
}


void testConstructing() {
    Timer t;

    Array<int> arr;
    for (int i = 0; i < bigSize; ++i) {
        arr.append(i);
    }

    check("Constructing", arr.size() == bigSize);
}

void testEquality() {
    Array<int> a1 = getArray(bigSize);
    Array<int> a2 = a1;
    Timer t;
    check("Equality", a1 == a2);
}

void testSaveLoad() {
    std::string fileName = "/tmp/sjdlajwqkclk";
    Array<int> a1 = getArray(bigSize);
    Timer tSave(true, false);
    a1.save(fileName);
    tSave.stop();

    Timer tLoad(true, false);
    Array<int> a2;
    a2.load(fileName);
    tLoad.stop();

    std::remove(fileName.c_str());

    bool same = (a1 == a2);

    check("Saving", same);
    tSave.report();
    check("Loading", same);
    tLoad.report();
}

void testFiltering() {
    Array<int> a1 = getArray(bigSize);

    Timer t;
    a1.filter([] (const int& r) { return r % 2 && r < 1000; });
    t.stop();
    Array<int> a2;
    for (int i = 1; i < 1000; i+= 2) {
        a2.append(i);
    }

    check("Filtering", a1 == a2);
}

void testShuffling() {
    Array<int> a1 = getArray(bigSize);
    auto a2 = a1;

    Timer t;
    a2.shuffle();
    t.stop();

    bool notEqual = (a1 != a2);
    bool sameSize = (a1.size() == a2.size());
    int vals1 =  countValuesIn(bigSize, a1);
    int vals2 =  countValuesIn(bigSize, a2);
    bool sameValues = (vals1 == vals2 && vals2 == bigSize);
    check("Shuffling", notEqual && sameSize && sameValues);
}

void testSorting() {
    Array<int> a;
    for (int i = 0; i < bigSize; ++i) {
        a.append(i % 100);
    }

    auto comparator = std::greater<int>();

    Timer t;
    a.sort(comparator);
    t.stop();

    check("Sorting", std::is_sorted(a.begin(), a.end(), comparator));
}

void testReversing() {
    Array<int> a1 = getArray(bigSize);
    Array<int> a2 = a1;

    Timer t;
    a2.reverse();
    t.stop();

    bool equal = true;
    for (int i = 0; i < a1.size(); ++i) {
        if (a1[i] != a2[a2.size() - 1 - i]) {
            equal = false;
            break;
        }
    }

    check("Reversing", equal);
}

void testForEach() {
    Array<int> a1 = getArray(bigSize);

    Timer t;
    a1.for_each([] (int& e) { e = 0; });
    t.stop();

    bool zeroed = (std::count(a1.begin(), a1.end(), 0) == a1.size());

    check("For each", zeroed);
}

int main() {
    testConstructing();
    testEquality();
    testSaveLoad();
    testFiltering();
    testShuffling();
    testSorting();
    testReversing();
    testForEach();
    return 0;
}